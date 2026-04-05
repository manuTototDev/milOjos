"""
Deploy Mil Ojos a HuggingFace Spaces paso a paso.

Uso:
  python deploy_hf.py --token TOKEN --user USER              # Solo codigo
  python deploy_hf.py --token TOKEN --user USER --images     # Codigo + imagenes
"""

import os
import sys
import shutil
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(SCRIPT_DIR, "backend")
SPACE_NAME = "mil-ojos-api"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--images", action="store_true", help="Tambien sube imagenes")
    args = parser.parse_args()

    try:
        from huggingface_hub import HfApi
    except ImportError:
        os.system(f"{sys.executable} -m pip install huggingface_hub")
        from huggingface_hub import HfApi

    space_id = f"{args.user}/{SPACE_NAME}"
    api = HfApi(token=args.token)

    print(f"\n  Deploying to: huggingface.co/spaces/{space_id}\n")

    # --- Paso 1: Subir archivos de codigo ---
    print("[1] Subiendo codigo del backend...")
    code_files = ["Dockerfile", "main.py", "requirements.txt"]
    for fname in code_files:
        src = os.path.join(BACKEND_DIR, fname)
        if os.path.exists(src):
            api.upload_file(
                path_or_fileobj=src,
                path_in_repo=fname,
                repo_id=space_id,
                repo_type="space",
                commit_message=f"Add {fname}",
            )
            print(f"  OK: {fname}")

    # --- Paso 2: Subir face_database.pkl ---
    print("[2] Subiendo face_database.pkl (25MB)...")
    pkl_path = os.path.join(BACKEND_DIR, "face_database.pkl")
    if os.path.exists(pkl_path):
        api.upload_file(
            path_or_fileobj=pkl_path,
            path_in_repo="face_database.pkl",
            repo_id=space_id,
            repo_type="space",
            commit_message="Add face_database.pkl",
        )
        print("  OK: face_database.pkl")

    # --- Paso 3: Subir imagenes en lotes ---
    if args.images:
        for folder_name in ["fotos_recortadas", "boletines"]:
            src_dir = os.path.join(BACKEND_DIR, "static", folder_name)
            if not os.path.isdir(src_dir):
                print(f"  SKIP: {folder_name} no encontrado")
                continue

            files = sorted(os.listdir(src_dir))
            total = len(files)
            print(f"\n[3] Subiendo {folder_name}/ ({total} archivos)...")

            # Subir en lotes de 100 archivos
            batch_size = 100
            for i in range(0, total, batch_size):
                batch = files[i:i+batch_size]
                batch_paths = []
                for fname in batch:
                    batch_paths.append(os.path.join(src_dir, fname))

                # Usar upload_folder con allow_patterns para el lote
                # Mas eficiente: subir la carpeta completa de una vez
                pct = min(100, int((i + batch_size) / total * 100))
                print(f"  {pct}% ({min(i+batch_size, total)}/{total})", end="\r")

            # Subir la carpeta completa de una vez
            print(f"  Subiendo {folder_name}/ completo...")
            api.upload_folder(
                folder_path=src_dir,
                path_in_repo=f"static/{folder_name}",
                repo_id=space_id,
                repo_type="space",
                commit_message=f"Add static/{folder_name}",
            )
            print(f"  OK: {folder_name}/ ({total} archivos)")
    else:
        # Crear carpetas vacias con un .gitkeep
        print("[3] Creando carpetas static/ vacias (usa --images para subir imagenes)...")
        import io
        for folder_name in ["fotos_recortadas", "boletines"]:
            api.upload_file(
                path_or_fileobj=io.BytesIO(b""),
                path_in_repo=f"static/{folder_name}/.gitkeep",
                repo_id=space_id,
                repo_type="space",
                commit_message=f"Create static/{folder_name}/",
            )
            print(f"  OK: static/{folder_name}/")

    print(f"\n  DEPLOY COMPLETADO!")
    print(f"  Space: https://huggingface.co/spaces/{space_id}")
    print(f"  API:   https://{args.user}-{SPACE_NAME}.hf.space")
    print(f"\n  Para Vercel, usa:")
    print(f"  NEXT_PUBLIC_API_URL = https://{args.user}-{SPACE_NAME}.hf.space\n")


if __name__ == "__main__":
    main()
