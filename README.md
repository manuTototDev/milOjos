# MIL OJOS
### Exoesqueleto de vigilancia afectiva

Mil Ojos es una pieza de arte electrónico en forma de exoesqueleto equipado con **nueve cámaras móviles** distribuidas alrededor de la cabeza del portador. Cada cámara está montada sobre servomotores que le permiten moverse de forma independiente. Un módulo de inteligencia artificial compara **en tiempo real** los rostros detectados en el entorno con una base de datos de **personas desaparecidas en el Estado de México**.

Esta plataforma web funciona como extensión digital del proyecto: permite a cualquier persona interactuar remotamente con el sistema de reconocimiento facial, convirtiendo cada pantalla en un nuevo ojo.

---

## 🔗 URLs de producción

| Componente | URL |
|---|---|
| **Frontend** | [frontend-kappa-five-99-five.vercel.app](https://frontend-kappa-five-99-five.vercel.app) |
| **API Backend** | [manuTototDev-mil-ojos-api.hf.space](https://manuTototDev-mil-ojos-api.hf.space) |
| **API Docs** | [/docs](https://manuTototDev-mil-ojos-api.hf.space/docs) |

---

## 🏗️ Arquitectura

```
┌─────────────────┐     ┌──────────────────────────────────┐
│    COBUPEM       │     │        HUGGINGFACE SPACES         │
│ Portal oficial   │────▶│  Docker · FastAPI · InsightFace   │
│ de búsqueda      │     │  face_database.pkl (25MB)         │
└─────────────────┘     │  Modelo buffalo_l (CPU)           │
                        └──────────┬──────────┬────────────┘
                                   │          │
                          API REST │          │ CDN de imágenes
                         /search   │          │ /resolve/main/static/
                                   │          │
                        ┌──────────▼──────────▼────────────┐
                        │          VERCEL                    │
                        │  Next.js 15 · React 19             │
                        │  Cámara → Captura → API → Render   │
                        └───────────────────────────────────┘
```

### Stack técnico

| Capa | Tecnología | Descripción |
|---|---|---|
| **Frontend** | Next.js 15, React 19, CSS Modules | UI con modo de escaneo en tiempo real, explorador de fichas y detalle de boletines |
| **Backend API** | FastAPI, Python 3.11 | Endpoints REST: `/search` (reconocimiento), `/fichas` (galería), `/years` |
| **IA Facial** | InsightFace (buffalo_l) | Detección de rostros, embeddings 512-dim, 106 landmarks faciales |
| **Búsqueda** | NumPy (similitud coseno) | Comparación vectorial contra toda la base en <100ms |
| **Imágenes** | HuggingFace CDN | Fotos recortadas (JPG ~10KB) y boletines optimizados (WebP ~45KB) |
| **Hosting** | HuggingFace Spaces (Docker) + Vercel | Infraestructura serverless, sin servidores propios |

---

## 📊 Base de datos

- **+11,000 personas** registradas
- **Período**: 2020–2026
- **Región**: Estado de México
- **Fuente**: COBUPEM (Comisión de Búsqueda de Personas del Estado de México)
- **Contenido por ficha**: Nombre, año, foto recortada facial, boletín oficial, embedding 512-dim

---

## 🔄 Pipeline de datos

```
COBUPEM portal → Scraper Python → Descarga boletines PDF/JPG
    → InsightFace detecta rostro → Recorte facial normalizado
    → Genera embedding 512-dim → Se almacena en face_database.pkl
    → Se sube a HuggingFace Spaces → API lista para búsqueda
```

---

## 🚀 Desarrollo local

### Backend
```bash
cd Web/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd Web/frontend
npm install
npm run dev
```

El frontend levanta en `http://localhost:3000` y por defecto se conecta al backend en `http://localhost:8000`.

### Variables de entorno

| Variable | Archivo | Descripción |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `Web/frontend/.env.production` | URL del backend API en producción |

---

## 📁 Estructura del proyecto

```
├── Web/
│   ├── backend/
│   │   ├── main.py              # FastAPI app (endpoints + InsightFace)
│   │   ├── startup.py           # Descarga face_database.pkl al iniciar
│   │   ├── Dockerfile           # Contenedor para HuggingFace Spaces
│   │   ├── requirements.txt     # Dependencias Python
│   │   ├── face_database.pkl    # Base de datos de embeddings (~25MB)
│   │   └── static/
│   │       ├── fotos_recortadas/  # ~12,886 fotos faciales
│   │       └── boletines_webp/    # ~12,894 boletines en WebP
│   │
│   └── frontend/
│       ├── app/
│       │   ├── page.tsx           # Landing page con concepto y arquitectura
│       │   ├── escaneo/page.tsx   # Escaneo facial en tiempo real
│       │   ├── explorar/page.tsx  # Galería paginada con filtros y búsqueda
│       │   └── ficha/[id]/page.tsx # Detalle de ficha individual
│       ├── components/
│       └── .env.production        # URL del API en producción
│
└── Dev/                           # Scripts de scraping y procesamiento
```

---

## 🎨 Concepto artístico

La pieza opera como una metáfora técnica de una **memoria extendida**, un cuerpo expandido que busca incansablemente entre la multitud. Propone una reflexión sobre el duelo colectivo, la **vigilancia afectiva** y la carga que implica la memoria social. La obra explora cómo el cuerpo puede ser habitado por la tecnología no como arma, sino como **órgano de búsqueda**.

---

**Mil Ojos** · Jóvenes Creadores · EDOMEX 2020–2026
