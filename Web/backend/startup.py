"""
Startup script for HuggingFace Spaces.
Downloads face_database.pkl and static files from the Space repo at runtime,
then starts the FastAPI server.
"""
import os
import subprocess
import sys

REPO_ID = "manuTototDev/mil-ojos-api"
APP_DIR = "/app"


def download_data():
    """Download data files from HF Space repo if not already present."""
    from huggingface_hub import hf_hub_download, snapshot_download

    # Download face_database.pkl
    pkl_path = os.path.join(APP_DIR, "face_database.pkl")
    if not os.path.exists(pkl_path):
        print("Downloading face_database.pkl...")
        hf_hub_download(
            repo_id=REPO_ID,
            filename="face_database.pkl",
            repo_type="space",
            local_dir=APP_DIR,
        )
        print("OK: face_database.pkl")

    # Download static files
    static_dir = os.path.join(APP_DIR, "static")
    if not os.path.isdir(static_dir) or len(os.listdir(os.path.join(static_dir, "fotos_recortadas", ""))) < 100:
        print("Downloading static files...")
        snapshot_download(
            repo_id=REPO_ID,
            repo_type="space",
            local_dir=APP_DIR,
            allow_patterns=["static/**"],
        )
        print("OK: static files")


if __name__ == "__main__":
    print("=== Mil Ojos API Startup ===")
    download_data()
    print("Starting server...")
    os.execvp(
        sys.executable,
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
    )
