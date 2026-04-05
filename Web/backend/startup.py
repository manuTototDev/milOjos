"""
Startup script for HuggingFace Spaces.
Downloads only face_database.pkl (25MB) and starts the server.
Static images are served directly from the HF repo CDN.
"""
import os
import sys

REPO_ID = "manuTototDev/mil-ojos-api"
APP_DIR = os.path.dirname(os.path.abspath(__file__))


def ensure_data():
    """Download face_database.pkl if not present."""
    pkl_path = os.path.join(APP_DIR, "face_database.pkl")

    if not os.path.exists(pkl_path):
        print("Downloading face_database.pkl...")
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


if __name__ == "__main__":
    print("=== Mil Ojos API Startup ===")
    print(f"Working directory: {APP_DIR}")

    ensure_data()

    print("Starting FastAPI server on port 7860...")
    os.execvp(
        sys.executable,
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
    )
