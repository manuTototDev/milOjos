"""Convert boletines from JPG to WebP for ~70% size reduction."""
import os
import sys
from pathlib import Path
from PIL import Image
import time

SRC_DIR = Path(r"Web\backend\static\boletines")
DST_DIR = Path(r"Web\backend\static\boletines_webp")
QUALITY = 80

DST_DIR.mkdir(parents=True, exist_ok=True)

files = sorted([f for f in SRC_DIR.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png')])
total = len(files)
print(f"Converting {total} boletines to WebP (q={QUALITY})...")

converted = 0
skipped = 0
total_src = 0
total_dst = 0
t0 = time.time()

for i, src_path in enumerate(files):
    dst_path = DST_DIR / (src_path.stem + ".webp")
    
    if dst_path.exists():
        skipped += 1
        total_dst += dst_path.stat().st_size
        total_src += src_path.stat().st_size
        continue
    
    try:
        with Image.open(src_path) as img:
            img.save(dst_path, "WEBP", quality=QUALITY)
        total_src += src_path.stat().st_size
        total_dst += dst_path.stat().st_size
        converted += 1
    except Exception as e:
        print(f"  ERROR: {src_path.name}: {e}")
    
    if (i + 1) % 500 == 0:
        elapsed = time.time() - t0
        rate = (i + 1) / elapsed
        eta = (total - i - 1) / rate
        pct = (total_dst / total_src * 100) if total_src else 0
        print(f"  [{i+1}/{total}] {elapsed:.0f}s elapsed, ETA {eta:.0f}s, ratio: {pct:.0f}%")

elapsed = time.time() - t0
src_mb = total_src / 1024 / 1024
dst_mb = total_dst / 1024 / 1024
ratio = (dst_mb / src_mb * 100) if src_mb else 0

print(f"\nDone in {elapsed:.0f}s")
print(f"  Converted: {converted}, Skipped: {skipped}")
print(f"  JPG: {src_mb:.0f} MB -> WebP: {dst_mb:.0f} MB ({ratio:.0f}%)")
print(f"  Saved: {src_mb - dst_mb:.0f} MB")
