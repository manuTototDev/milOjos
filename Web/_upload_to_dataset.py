"""
Upload all images to HF Dataset (no 10K file limit).
Uploads fotos_recortadas and boletines_webp in batches.
"""
import os, time, sys
from pathlib import Path
from huggingface_hub import HfApi, CommitOperationAdd

TOKEN = os.environ.get("HF_TOKEN", "")
DATASET_ID = "manuTototDev/mil-ojos-images"
BATCH = 80
DELAY = 5  # seconds between batches

api = HfApi(token=TOKEN)

def upload(local_dir, remote_prefix, label):
    local_path = Path(local_dir)
    if not local_path.exists():
        print(f"  {label}: carpeta no existe: {local_dir}")
        return

    exts = {'.jpg', '.jpeg', '.png', '.webp'}
    files = sorted([f for f in local_path.iterdir() if f.is_file() and f.suffix.lower() in exts])

    # Check what already exists in the dataset
    try:
        existing = {os.path.basename(f) for f in api.list_repo_files(DATASET_ID, repo_type="dataset") if f.startswith(remote_prefix)}
    except Exception:
        existing = set()

    to_upload = [f for f in files if f.name not in existing]
    print(f"{label}: {len(to_upload)} pendientes ({len(existing)} ya subidas, {len(files)} total)")

    if not to_upload:
        return

    done = 0
    t0 = time.time()

    for i in range(0, len(to_upload), BATCH):
        batch = to_upload[i:i+BATCH]
        ops = [CommitOperationAdd(
            path_in_repo=f"{remote_prefix}/{f.name}",
            path_or_fileobj=str(f)
        ) for f in batch]

        for attempt in range(10):
            try:
                api.create_commit(
                    repo_id=DATASET_ID,
                    repo_type="dataset",
                    operations=ops,
                    commit_message=f"{label} {i+len(batch)}/{len(to_upload)}"
                )
                done += len(batch)
                el = time.time() - t0
                remaining = len(to_upload) - i - len(batch)
                rate = done / el if el else 1
                eta = remaining / rate if rate else 0
                print(f"  [{done}/{len(to_upload)}] {el:.0f}s elapsed, ETA {eta:.0f}s")
                break
            except Exception as e:
                wait = min(30 * (attempt + 1), 300)
                print(f"  retry {attempt+1}, wait {wait}s: {str(e)[:80]}")
                time.sleep(wait)

        time.sleep(DELAY)

    print(f"  {label} DONE: {done} in {time.time()-t0:.0f}s")

print(f"=== Upload to Dataset started at {time.strftime('%H:%M:%S')} ===")

# Upload fotos first (remaining ~2,887)
upload("Web/backend/static/fotos_recortadas", "fotos_recortadas", "fotos")

# Then boletines
upload("Web/backend/static/boletines_webp", "boletines_webp", "boletines")

print(f"=== ALL DONE at {time.strftime('%H:%M:%S')} ===")
