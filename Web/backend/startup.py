"""
Startup script for HuggingFace Spaces.
If face_database.pkl is already copied in (via COPY . .), just start the server.
Otherwise, download from the Space repo.
"""
import os
import sys

REPO_ID = "manuTototDev/mil-ojos-api"
APP_DIR = os.path.dirname(os.path.abspath(__file__))


def ensure_data():
    """Ensure data files exist, downloading from HF if needed."""
    pkl_path = os.path.join(APP_DIR, "face_database.pkl")
    static_dir = os.path.join(APP_DIR, "static")
    fotos_dir = os.path.join(static_dir, "fotos_recortadas")

    # Check if face_database.pkl exists
    if not os.path.exists(pkl_path):
        print("face_database.pkl not found locally, downloading...")
        from huggingface_hub import hf_hub_download
        hf_hub_download(
            repo_id=REPO_ID,
            filename="face_database.pkl",
            repo_type="space",
            local_dir=APP_DIR,
        )
        print("OK: face_database.pkl downloaded")
    else:
        size_mb = os.path.getsize(pkl_path) / 1024 / 1024
        print(f"OK: face_database.pkl found ({size_mb:.1f} MB)")

    # Check if static files exist
    if not os.path.isdir(fotos_dir) or len(os.listdir(fotos_dir)) < 10:
        print("Static files not found locally, downloading...")
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id=REPO_ID,
            repo_type="space",
            local_dir=APP_DIR,
            allow_patterns=["static/**"],
        )
        print("OK: static files downloaded")
    else:
        n = len(os.listdir(fotos_dir))
        print(f"OK: static/fotos_recortadas/ found ({n} files)")


if __name__ == "__main__":
    print("=== Mil Ojos API Startup ===")
    print(f"Working directory: {APP_DIR}")
    print(f"Files in app dir: {os.listdir(APP_DIR)}")
    
    ensure_data()
    
    print("Starting FastAPI server on port 7860...")
    os.execvp(
        sys.executable,
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
    )
