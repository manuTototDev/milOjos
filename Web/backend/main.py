import os
import io
import pickle
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from PIL import Image
import cv2
from insightface.app import FaceAnalysis

# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.environ.get("DATA_DIR", BASE_DIR)
DB_FILE    = os.path.join(DATA_DIR, "face_database.pkl") if os.path.exists(os.path.join(os.environ.get("DATA_DIR", ""), "face_database.pkl")) else os.path.join(BASE_DIR, "face_database.pkl")
STATIC_DIR = os.path.join(DATA_DIR, "static") if os.path.isdir(os.path.join(os.environ.get("DATA_DIR", ""), "static")) else os.path.join(BASE_DIR, "static")

# CDN base URL for images (when static files are not on disk)
HF_CDN_BASE = "https://huggingface.co/spaces/manuTototDev/mil-ojos-api/resolve/main"
USE_LOCAL_STATIC = os.path.isdir(STATIC_DIR) and len(os.listdir(os.path.join(STATIC_DIR, "fotos_recortadas", ""))) > 10 if os.path.isdir(os.path.join(STATIC_DIR, "fotos_recortadas")) else False

# ── FastAPI ───────────────────────────────────────────────────────────────────
app = FastAPI(title="Mil Ojos API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Cargar DB de embeddings al arrancar ───────────────────────────────────────
print("Cargando base de datos de rostros...")
with open(DB_FILE, "rb") as f:
    raw_db = pickle.load(f)

# Construir índice limpio
database   = []
db_embeddings = []

for i, entry in enumerate(raw_db):
    raw_name = entry["name"]          # ej. "AARON ADALID ESCOBEDO CONDE.jpg"
    name     = os.path.splitext(raw_name)[0]   # quitar .jpg
    year     = str(entry["year"])

    # Boletin: use WebP version (much smaller), foto: keep JPG (already tiny)
    bol_base = os.path.splitext(raw_name)[0] + ".webp"

    # URLs: local /static/ when images on disk, HF CDN otherwise
    if USE_LOCAL_STATIC:
        foto_url = f"/static/fotos_recortadas/{year}_foto_{raw_name}"
        bol_url  = f"/static/boletines_webp/{year}_{bol_base}"
    else:
        foto_url = f"{HF_CDN_BASE}/static/fotos_recortadas/{year}_foto_{raw_name}"
        bol_url  = f"{HF_CDN_BASE}/static/boletines_webp/{year}_{bol_base}"

    database.append({
        "id":      i,
        "name":    name,
        "year":    year,
        "foto":    foto_url,
        "boletin": bol_url,
    })
    db_embeddings.append(entry["embedding"])

db_matrix = np.array(db_embeddings, dtype=np.float32)
print(f"Base de datos lista: {len(database)} personas.")

# ── Marcar entradas con imagen disponible ─────────────────────────────────────
if USE_LOCAL_STATIC:
    # Local: check disk
    fotos_dir = os.path.join(STATIC_DIR, "fotos_recortadas")
    available_fotos = set(os.listdir(fotos_dir)) if os.path.isdir(fotos_dir) else set()
else:
    # CDN: query HF Space file list at startup
    print("Consultando archivos disponibles en HF Space...")
    try:
        from huggingface_hub import HfApi
        _api = HfApi()
        _all_files = _api.list_repo_files("manuTototDev/mil-ojos-api", repo_type="space")
        available_fotos = {os.path.basename(f) for f in _all_files if f.startswith("static/fotos_recortadas/")}
        print(f"  Fotos disponibles en CDN: {len(available_fotos)}")
    except Exception as e:
        print(f"  Error consultando HF: {e} — asumiendo todas disponibles")
        available_fotos = None  # None = no filter

count_available = 0
for entry in database:
    year = entry["year"]
    # Reconstruct filename to check
    foto_filename = entry["foto"].split("/")[-1]  # e.g. 2024_foto_NAME.jpg
    if available_fotos is None:
        entry["has_foto"] = True
    else:
        entry["has_foto"] = foto_filename in available_fotos
    if entry["has_foto"]:
        count_available += 1

print(f"Personas con foto disponible: {count_available}/{len(database)}")

# ── InsightFace ───────────────────────────────────────────────────────────────
print("Cargando modelo InsightFace...")
face_app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
face_app.prepare(ctx_id=0, det_size=(640, 640))
print("Modelo listo.")

# ── Caché de face bboxes para las fotos de la DB ─────────────────────────────
# Se llena lazy: cada foto se detecta una sola vez y se guarda el bbox
face_bbox_cache: dict[int, dict | None] = {}

def detect_face_in_photo(entry_id: int) -> dict | None:
    """Detecta el rostro en la foto de una persona y retorna bbox normalizado."""
    if entry_id in face_bbox_cache:
        return face_bbox_cache[entry_id]

    # If images aren't on disk, return a default centered bbox
    if not USE_LOCAL_STATIC:
        face_bbox_cache[entry_id] = {"x": 0.1, "y": 0.05, "w": 0.8, "h": 0.85}
        return face_bbox_cache[entry_id]

    entry = database[entry_id]
    foto_rel = entry["foto"]  # e.g. /static/fotos_recortadas/2024_foto_NAME.jpg
    foto_path = os.path.join(BASE_DIR, foto_rel.lstrip("/"))

    if not os.path.exists(foto_path):
        face_bbox_cache[entry_id] = None
        return None

    try:
        img = cv2.imread(foto_path)
        if img is None:
            face_bbox_cache[entry_id] = None
            return None

        h, w = img.shape[:2]
        faces = face_app.get(img)
        if not faces:
            face_bbox_cache[entry_id] = {"x": 0.1, "y": 0.05, "w": 0.8, "h": 0.85}
            return face_bbox_cache[entry_id]

        face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
        bbox = face.bbox.astype(float)
        result = {
            "x": float(max(0, bbox[0]) / w),
            "y": float(max(0, bbox[1]) / h),
            "w": float(min(bbox[2] - bbox[0], w) / w),
            "h": float(min(bbox[3] - bbox[1], h) / h),
        }
        face_bbox_cache[entry_id] = result
        return result
    except Exception:
        face_bbox_cache[entry_id] = None
        return None

# ── Imágenes estáticas (solo si están en disco) ──────────────────────────────
if USE_LOCAL_STATIC:
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    print(f"Sirviendo imágenes locales desde {STATIC_DIR}")
else:
    print(f"Imágenes servidas desde CDN: {HF_CDN_BASE}")

# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/")
def health():
    available = sum(1 for e in database if e.get("has_foto"))
    return {"status": "ok", "personas": len(database), "con_foto": available}


@app.post("/search")
async def search_face(file: UploadFile = File(...)):
    """
    Recibe una imagen (selfie), detecta el rostro,
    y devuelve las 12 personas más parecidas de la DB.
    """
    contents = await file.read()
    nparr    = np.frombuffer(contents, np.uint8)
    img_cv   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img_cv is None:
        raise HTTPException(400, "No se pudo decodificar la imagen")

    faces = face_app.get(img_cv)
    if not faces:
        raise HTTPException(422, "No se detectó ningún rostro en la imagen")

    # El rostro principal = el más grande
    main_face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
    query_emb = main_face.normed_embedding.astype(np.float32)

    # Similitud coseno (embeddings ya normalizados)
    similarities = np.dot(db_matrix, query_emb)
    # Get more candidates than needed, then filter by available images
    top_idx = np.argsort(similarities)[-30:][::-1]

    results = []
    for idx in top_idx:
        if len(results) >= 8:
            break
        entry = database[idx]
        if not entry.get("has_foto", True):
            continue  # Skip entries without uploaded images
        result = entry.copy()
        result["score"] = float(round(similarities[idx] * 100, 1))
        result["match_face_box"] = detect_face_in_photo(idx)
        results.append(result)

    # Atributos del visitante
    gender = "femenino" if main_face.sex == 0 else "masculino"
    age    = int(main_face.age)

    # BBox normalizado (0-1)
    h, w = img_cv.shape[:2]
    bbox = main_face.bbox.astype(float)
    face_box = {
        "x":  float(bbox[0] / w),
        "y":  float(bbox[1] / h),
        "w":  float((bbox[2] - bbox[0]) / w),
        "h":  float((bbox[3] - bbox[1]) / h),
    }

    # 106 landmarks normalizados (0-1) del modelo 2d106det incluido en buffalo_l
    lm106 = []
    if hasattr(main_face, 'landmark_2d_106') and main_face.landmark_2d_106 is not None:
        for pt in main_face.landmark_2d_106:
            lm106.append({"x": float(pt[0] / w), "y": float(pt[1] / h)})

    return JSONResponse({
        "visitor":  {"gender": gender, "age": age},
        "face_box": face_box,
        "lm106":    lm106,
        "results":  results
    })


@app.get("/fichas")
def list_fichas(page: int = 1, limit: int = 48, year: str = None, q: str = None):
    """Lista paginada de todas las fichas, con filtro opcional por año y nombre."""
    filtered = database

    if year:
        filtered = [p for p in filtered if p["year"] == year]

    if q:
        q_lower = q.lower()
        filtered = [p for p in filtered if q_lower in p["name"].lower()]

    total = len(filtered)
    start = (page - 1) * limit
    end   = start + limit
    items = filtered[start:end]

    return {
        "total": total,
        "page":  page,
        "pages": (total + limit - 1) // limit,
        "items": items,
    }


@app.get("/fichas/{ficha_id}")
def get_ficha(ficha_id: int):
    """Retorna los datos de una ficha por su ID numérico."""
    if ficha_id < 0 or ficha_id >= len(database):
        raise HTTPException(404, "Ficha no encontrada")
    return database[ficha_id]


@app.get("/years")
def get_years():
    """Retorna los años disponibles en la base de datos."""
    years = sorted(set(p["year"] for p in database))
    return {"years": years}
