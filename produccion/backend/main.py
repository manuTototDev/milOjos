"""
main.py — Mil Ojos v3.0 (Producción)
Backend FastAPI:
  - /search          → recibe frame del frontend, retorna matches + face_box
  - /servo/track     → recibe face_box normalizado, actualiza targets de servos
  - /servo/status    → estado actual de los 9 brazos
  - /fichas          → lista paginada de fichas
  - /fichas/{id}     → ficha individual
  - /years           → años disponibles
  - /img/...         → proxy de imágenes (CDN HuggingFace)
"""

import os
import io
import pickle
import time
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
import cv2
import httpx
from insightface.app import FaceAnalysis

from servo_controller import ServoController

# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE  = os.path.join(BASE_DIR, "face_database.pkl")

# ── Imágenes locales ──────────────────────────────────────────────────────────
# Se leerán localmente desde la carpeta fcaesDes

# ── FastAPI ───────────────────────────────────────────────────────────────────
app = FastAPI(title="Mil Ojos API v3", version="3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Cargar base de datos de rostros ───────────────────────────────────────────
print("[DB] Cargando base de datos de rostros…")
with open(DB_FILE, "rb") as f:
    raw_db = pickle.load(f)

database: list[dict] = []
db_embeddings: list  = []

for i, entry in enumerate(raw_db):
    raw_name = entry["name"]
    name     = os.path.splitext(raw_name)[0]
    year     = str(entry["year"])
    bol_base = os.path.splitext(raw_name)[0] + ".webp"

    database.append({
        "id":      i,
        "name":    name,
        "year":    year,
        "foto":    f"/img/fotos_recortadas/{year}_foto_{raw_name}",
        "boletin": f"/img/boletines_webp/{year}_{bol_base}",
        "has_foto": True,
    })
    db_embeddings.append(entry["embedding"])

db_matrix = np.array(db_embeddings, dtype=np.float32)
print(f"[DB] {len(database)} personas indexadas.")

# ── InsightFace ───────────────────────────────────────────────────────────────
print("[AI] Cargando InsightFace (buffalo_l)…")
face_app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
face_app.prepare(ctx_id=0, det_size=(640, 640))
print("[AI] Modelo listo.")

# ── Servo controller ─────────────────────────────────────────────────────────
servo = ServoController()
servo.start()

# ── Modelos Pydantic ──────────────────────────────────────────────────────────
class FaceBoxPayload(BaseModel):
    """Face box normalizado (0-1) enviado desde el frontend."""
    x: float       # left
    y: float       # top
    w: float       # width
    h: float       # height
    img_w: int     # tamaño real del frame (px)  — para calcular distancia
    img_h: int

class ServoOverridePayload(BaseModel):
    arm_index: int
    servo_index: int
    angle: float

# ══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/")
def health():
    return {
        "status":   "ok",
        "personas": len(database),
        "con_foto": sum(1 for e in database if e.get("has_foto")),
        "servos":   servo.get_status(),
    }


# ── Búsqueda facial ────────────────────────────────────────────────────────────
@app.post("/search")
async def search_face(file: UploadFile = File(...)):
    """
    Recibe un frame JPEG del browser, detecta el rostro principal,
    retorna las 8 personas más similares + face_box + landmarks.
    """
    contents = await file.read()
    nparr    = np.frombuffer(contents, np.uint8)
    img_cv   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img_cv is None:
        raise HTTPException(400, "No se pudo decodificar la imagen")

    faces = face_app.get(img_cv)
    if not faces:
        raise HTTPException(422, "No se detectó ningún rostro")

    main_face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
    query_emb = main_face.normed_embedding.astype(np.float32)

    similarities = np.dot(db_matrix, query_emb)
    top_idx      = np.argsort(similarities)[-30:][::-1]

    results = []
    for idx in top_idx:
        if len(results) >= 8:
            break
        entry  = database[idx]
        result = entry.copy()
        result["score"] = float(round(similarities[idx] * 100, 1))
        results.append(result)

    h, w = img_cv.shape[:2]
    bbox = main_face.bbox.astype(float)
    face_box = {
        "x": float(bbox[0] / w),
        "y": float(bbox[1] / h),
        "w": float((bbox[2] - bbox[0]) / w),
        "h": float((bbox[3] - bbox[1]) / h),
    }

    lm106 = []
    if hasattr(main_face, "landmark_2d_106") and main_face.landmark_2d_106 is not None:
        for pt in main_face.landmark_2d_106:
            lm106.append({"x": float(pt[0] / w), "y": float(pt[1] / h)})

    gender = "femenino" if main_face.sex == 0 else "masculino"
    age    = int(main_face.age)

    return JSONResponse({
        "visitor":  {"gender": gender, "age": age},
        "face_box": face_box,
        "lm106":    lm106,
        "results":  results,
    })


# ── Control de servos ─────────────────────────────────────────────────────────
@app.post("/servo/track")
async def servo_track(payload: FaceBoxPayload):
    """
    Recibe la posición del rostro. Si está a un 50% de cercanía del centro de la imagen,
    detiene el brazo. Si no, lo ignora (como si no hubiera rostro).
    """
    cx_norm = payload.x + payload.w / 2
    cy_norm = payload.y + payload.h / 2

    # Distancia al centro en coordenadas normalizadas (0 a 1)
    # Centro = 0.5. El 50% de cercanía significa estar a menos de 0.25 de distancia del centro.
    dist_centro = np.sqrt((cx_norm - 0.5)**2 + (cy_norm - 0.5)**2)

    if dist_centro <= 0.25:
        servo.set_face_detected(True)
        status = "PAUSED (CENTER)"
    else:
        servo.set_face_detected(False)
        status = "IGNORED (OFF-CENTER)"

    return {
        "status":  status,
        "step_v":  0.0,
        "step_h":  0.0,
        "dist_px": float(dist_centro * payload.img_w),
        "brain":   {},
    }


@app.post("/servo/no-face")
async def servo_no_face():
    """Notifica que no hay rostro; los servos usan suavizado lento."""
    servo.set_face_detected(False)
    return {"ok": True}


@app.get("/servo/status")
def servo_status():
    """Estado completo de los 9 brazos."""
    return servo.get_status()




@app.post("/servo/test/override")
def servo_test_override(payload: ServoOverridePayload):
    servo.set_target_override(payload.arm_index, payload.servo_index, payload.angle)
    return {"ok": True}

@app.post("/servo/test/all")
def servo_test_all(angle: float):
    servo.set_all_servos(angle)
    return {"ok": True}


# ── Fichas ────────────────────────────────────────────────────────────────────
@app.get("/fichas")
def list_fichas(page: int = 1, limit: int = 48, year: str = None, q: str = None):
    filtered = database
    if year:
        filtered = [p for p in filtered if p["year"] == year]
    if q:
        q_lower = q.lower()
        filtered = [p for p in filtered if q_lower in p["name"].lower()]
    total = len(filtered)
    start = (page - 1) * limit
    items = filtered[start:start + limit]
    return {"total": total, "page": page, "pages": (total + limit - 1) // limit, "items": items}


@app.get("/fichas/{ficha_id}")
def get_ficha(ficha_id: int):
    if ficha_id < 0 or ficha_id >= len(database):
        raise HTTPException(404, "Ficha no encontrada")
    return database[ficha_id]


@app.get("/years")
def get_years():
    return {"years": sorted(set(p["year"] for p in database))}


from fastapi.responses import FileResponse

# ── Servir imágenes locales ──────────────────────────────────────────────────
@app.get("/img/{folder}/{filename}")
async def get_local_image(folder: str, filename: str):
    if folder not in ("fotos_recortadas", "boletines_webp"):
        raise HTTPException(404, "Carpeta desconocida")
    
    try:
        year = filename[:4]
    except:
        raise HTTPException(400, "Nombre de archivo inválido")

    base_dir = os.path.join(BASE_DIR, "fcaesDes", year)
    
    if folder == "fotos_recortadas":
        # De "2020_foto_NOMBRE.jpg" a "foto_NOMBRE.jpg"
        actual_filename = filename[5:]
        file_path = os.path.join(base_dir, "fotos_recortadas", actual_filename)
    else:
        # folder == "boletines_webp"
        # De "2020_NOMBRE.webp" a "NOMBRE.jpg"
        actual_filename = filename[5:-5] + ".jpg"
        file_path = os.path.join(base_dir, "boletines_completos", actual_filename)

    if not os.path.exists(file_path):
        raise HTTPException(404, "Imagen no encontrada localmente")
        
    return FileResponse(file_path)
