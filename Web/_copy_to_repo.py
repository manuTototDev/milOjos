"""Copy missing images to the cloned HF Space repo, then git add + commit + push."""
import os
import shutil
from pathlib import Path

CLONE_DIR = Path("Web/_hf_space_repo")
FOTOS_SRC = Path("Web/backend/static/fotos_recortadas")
FOTOS_DST = CLONE_DIR / "static" / "fotos_recortadas"
BOL_SRC = Path("Web/backend/static/boletines_webp")
BOL_DST = CLONE_DIR / "static" / "boletines_webp"

# Ensure destination dirs exist
FOTOS_DST.mkdir(parents=True, exist_ok=True)
BOL_DST.mkdir(parents=True, exist_ok=True)

# 1. Copy missing fotos
existing_fotos = {f.name for f in FOTOS_DST.iterdir() if f.is_file()}
all_fotos = [f for f in FOTOS_SRC.iterdir() if f.is_file() and f.suffix.lower() in ('.jpg','.jpeg','.png')]
missing_fotos = [f for f in all_fotos if f.name not in existing_fotos]
print(f"Fotos: {len(existing_fotos)} exist, {len(missing_fotos)} to copy")
for f in missing_fotos:
    shutil.copy2(f, FOTOS_DST / f.name)
print(f"  Copied {len(missing_fotos)} fotos")

# 2. Copy ALL boletines_webp (new folder)
existing_bols = {f.name for f in BOL_DST.iterdir() if f.is_file()} if BOL_DST.exists() else set()
all_bols = [f for f in BOL_SRC.iterdir() if f.is_file() and f.suffix == '.webp']
missing_bols = [f for f in all_bols if f.name not in existing_bols]
print(f"Boletines WebP: {len(existing_bols)} exist, {len(missing_bols)} to copy")
for i, f in enumerate(missing_bols):
    shutil.copy2(f, BOL_DST / f.name)
    if (i+1) % 2000 == 0:
        print(f"  ...copied {i+1}/{len(missing_bols)}")
print(f"  Copied {len(missing_bols)} boletines")

print(f"\nTotal files in clone repo:")
print(f"  fotos_recortadas: {len(list(FOTOS_DST.iterdir()))} files")
print(f"  boletines_webp: {len(list(BOL_DST.iterdir()))} files")
print("\nReady for: git add + commit + push")
