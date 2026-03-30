"""
Deploy Mil Ojos backend to HuggingFace Spaces.

Requisitos:
  pip install huggingface_hub

Uso:
  python deploy_hf.py --token TU_HF_TOKEN --user tu-usuario-hf
"""

import os
import sys
import shutil
import argparse
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(SCRIPT_DIR, "backend")
DEPLOY_DIR = os.path.join(SCRIPT_DIR, "_hf_deploy")
SPACE_NAME = "mil-ojos-api"


def main():
    parser = argparse.ArgumentParser(description="Deploy Mil Ojos backend to HuggingFace Spaces")
    parser.add_argument("--token", required=True, help="HuggingFace API token")
    parser.add_argument("--user", required=True, help="HuggingFace username")
    parser.add_argument("--skip-images", action="store_true", help="Skip copying static images (for testing)")
    args = parser.parse_args()

    space_id = f"{args.user}/{SPACE_NAME}"
    print(f"\n{'='*60}")
    print(f"  Deploying to: huggingface.co/spaces/{space_id}")
    print(f"{'='*60}\n")

    # 1. Clean and create deploy directory
    if os.path.exists(DEPLOY_DIR):
        shutil.rmtree(DEPLOY_DIR)
    os.makedirs(DEPLOY_DIR)

    # 2. Create HF Space README
    readme = f"""---
title: Mil Ojos API
emoji: 👁️
colorFrom: green
colorTo: gray
sdk: docker
app_port: 7860
---

# Mil Ojos API

Backend de reconocimiento facial para el proyecto Mil Ojos.
FastAPI + InsightFace (buffalo_l) + Base de datos de 11,375 personas desaparecidas.
"""
    with open(os.path.join(DEPLOY_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    # 3. Copy backend files
    print("[1/5] Copiando código del backend...")
    for fname in ["Dockerfile", "main.py", "requirements.txt", "face_database.pkl"]:
        src = os.path.join(BACKEND_DIR, fname)
        if os.path.exists(src):
            shutil.copy2(src, DEPLOY_DIR)
            size_mb = os.path.getsize(src) / 1024 / 1024
            print(f"  ✓ {fname} ({size_mb:.1f} MB)")
        else:
            print(f"  ✗ {fname} NO ENCONTRADO")
            if fname != "face_database.pkl":
                sys.exit(1)

    # 4. Copy static files
    static_src = os.path.join(BACKEND_DIR, "static")
    static_dst = os.path.join(DEPLOY_DIR, "static")

    if args.skip_images:
        print("[2/5] Saltando imágenes (--skip-images)")
        os.makedirs(os.path.join(static_dst, "fotos_recortadas"), exist_ok=True)
        os.makedirs(os.path.join(static_dst, "boletines"), exist_ok=True)
    else:
        print("[2/5] Copiando imágenes estáticas (esto puede tomar varios minutos)...")
        if os.path.isdir(static_src):
            shutil.copytree(static_src, static_dst)
            fotos = len(os.listdir(os.path.join(static_dst, "fotos_recortadas"))) if os.path.isdir(os.path.join(static_dst, "fotos_recortadas")) else 0
            bols = len(os.listdir(os.path.join(static_dst, "boletines"))) if os.path.isdir(os.path.join(static_dst, "boletines")) else 0
            print(f"  ✓ {fotos} fotos recortadas")
            print(f"  ✓ {bols} boletines")
        else:
            print(f"  ✗ {static_src} no existe")
            os.makedirs(os.path.join(static_dst, "fotos_recortadas"), exist_ok=True)
            os.makedirs(os.path.join(static_dst, "boletines"), exist_ok=True)

    # 5. Initialize git + LFS and push to HuggingFace
    print("[3/5] Inicializando repositorio git...")
    os.chdir(DEPLOY_DIR)
    subprocess.run(["git", "init"], check=True, capture_output=True)
    subprocess.run(["git", "lfs", "install"], check=True, capture_output=True)
    
    # Track large files with LFS
    subprocess.run(["git", "lfs", "track", "*.pkl"], check=True, capture_output=True)
    subprocess.run(["git", "lfs", "track", "*.jpg"], check=True, capture_output=True)
    subprocess.run(["git", "lfs", "track", "*.jpeg"], check=True, capture_output=True)
    subprocess.run(["git", "lfs", "track", "*.png"], check=True, capture_output=True)

    print("[4/5] Configurando remote de HuggingFace...")
    remote_url = f"https://{args.user}:{args.token}@huggingface.co/spaces/{space_id}"
    subprocess.run(["git", "remote", "add", "origin", remote_url], check=True, capture_output=True)

    print("[5/5] Subiendo a HuggingFace Spaces...")
    subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Deploy Mil Ojos API"], check=True, capture_output=True)
    
    print("\n  Haciendo push (las imágenes se suben con Git LFS)...")
    print("  Esto puede tomar 10-30 minutos dependiendo de tu conexión...\n")
    
    result = subprocess.run(
        ["git", "push", "-u", "origin", "main", "--force"],
        capture_output=False
    )
    
    if result.returncode == 0:
        print(f"\n{'='*60}")
        print(f"  ✅ Deploy exitoso!")
        print(f"  URL: https://huggingface.co/spaces/{space_id}")
        print(f"  API: https://{args.user}-{SPACE_NAME}.hf.space")
        print(f"{'='*60}")
        print(f"\n  Para el frontend en Vercel, usa esta variable de entorno:")
        print(f"  NEXT_PUBLIC_API_URL = https://{args.user}-{SPACE_NAME}.hf.space")
    else:
        print("\n  ✗ Error en el push. Verifica tu token y usuario.")

    # Cleanup
    os.chdir(SCRIPT_DIR)


if __name__ == "__main__":
    main()
