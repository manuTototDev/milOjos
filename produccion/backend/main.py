"""
main.py — Mil Ojos v3.0 (Producción)
Backend FastAPI:
  - /search          → recibe frame del frontend, retorna matches + face_box
  - /servo/track     → recibe face_box normalizado, actualiza targets de servos
  - /servo/status    → estado actual de los 9 brazos
  - /servo/reset     → resetea cerebro de seguimiento
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
from brain_trainer import BrainTrainer

# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE  = os.path.join(BASE_DIR, "face_database.pkl")

# ── CDN (HuggingFace Dataset) ─────────────────────────────────────────────────
HF_CDN_BASE = "https://huggingface.co/datasets/manuTototDev/mil-ojos-images/resolve/main"
_img_cache: dict[str, bytes] = {}

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

# ── Servo controller + Brain ──────────────────────────────────────────────────
servo = ServoController()
servo.start()

brain = BrainTrainer()

# ── Modelos Pydantic ──────────────────────────────────────────────────────────
class FaceBoxPayload(BaseModel):
    """Face box normalizado (0-1) enviado desde el frontend."""
    x: float       # left
    y: float       # top
    w: float       # width
    h: float       # height
    img_w: int     # tamaño real del frame (px)  — para calcular distancia
    img_h: int

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
    Recibe la posición del rostro (normalizada 0-1) desde el frontend.
    Calcula error respecto al centro y actualiza el brazo 1.
    """
    cx_norm = payload.x + payload.w / 2   # centro horizontal (0-1)
    cy_norm = payload.y + payload.h / 2   # centro vertical   (0-1)

    # Error respecto al centro: positivo = rostro a la derecha / abajo del centro
    err_x = cx_norm - 0.5    # rango -0.5 .. +0.5
    err_y = cy_norm - 0.5

    # Normalizar a -1..1
    error_input = np.array([err_x * 2, err_y * 2])

    # Distancia en píxeles al centro (para reward del brain)
    cx_px = (cx_norm - 0.5) * payload.img_w
    cy_px = (cy_norm - 0.5) * payload.img_h
    dist  = float(np.sqrt(cx_px**2 + cy_px**2))

    step_v, step_h, status = brain.update(error_input, dist, time.time())

    # Aplicar movimiento al Brazo 1 (índice 0)
    # target[base] += step_h  →  yaw (giro horizontal)
    # target[codo] += step_v  →  tilt (inclinación vertical)
    current = servo.get_status()["targets"][0]
    new_base = current[0] + step_h
    new_codo = current[2] + step_v
    servo.set_target(0, [new_base, current[1], new_codo, current[3]])
    servo.set_face_detected(True)

    return {
        "status":  status,
        "step_v":  round(step_v, 2),
        "step_h":  round(step_h, 2),
        "dist_px": round(dist, 1),
        "brain":   brain.get_state(),
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


@app.post("/servo/reset-brain")
def servo_reset_brain():
    """Resetea los pesos del cerebro de seguimiento."""
    brain.reset_pesos()
    return {"ok": True, "brain": brain.get_state()}


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


# ── Proxy de imágenes (CDN HuggingFace) ──────────────────────────────────────
@app.get("/img/{folder}/{filename}")
async def img_proxy(folder: str, filename: str):
    if folder not in ("fotos_recortadas", "boletines_webp"):
        raise HTTPException(404, "Carpeta desconocida")
    key = f"{folder}/{filename}"
    if key in _img_cache:
        data = _img_cache[key]
    else:
        cdn_url = f"{HF_CDN_BASE}/{folder}/{filename}"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.get(cdn_url)
            if r.status_code != 200:
                raise HTTPException(r.status_code, "Imagen no encontrada en CDN")
            data = r.content
            if folder == "fotos_recortadas":
                _img_cache[key] = data
        except httpx.TimeoutException:
            raise HTTPException(504, "Timeout al obtener imagen")

    ext   = filename.rsplit(".", 1)[-1].lower()
    ctype = {"jpg":"image/jpeg","jpeg":"image/jpeg","webp":"image/webp","png":"image/png"}.get(ext,"image/jpeg")
    return Response(content=data, media_type=ctype,
                    headers={"Cache-Control": "public, max-age=604800"})
