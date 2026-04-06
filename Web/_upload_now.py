"""Upload remaining images NOW (no delay)."""
import os, time
from pathlib import Path
from huggingface_hub import HfApi, CommitOperationAdd

TOKEN = os.environ.get("HF_TOKEN", "")
SPACE_ID = "manuTototDev/mil-ojos-api"
BATCH = 50
DELAY = 8

api = HfApi(token=TOKEN)

def upload(local_dir, remote_prefix, label):
    local_path = Path(local_dir)
    files = sorted([f for f in local_path.iterdir() if f.is_file() and f.suffix.lower() in ('.jpg','.jpeg','.png','.webp')])
    
    existing = {os.path.basename(f) for f in api.list_repo_files(SPACE_ID, repo_type="space") if f.startswith(remote_prefix)}
    to_upload = [f for f in files if f.name not in existing]
    print(f"{label}: {len(to_upload)} to upload ({len(existing)} exist)")
    
    if not to_upload:
        return
    
    done = 0
    t0 = time.time()
    
    for i in range(0, len(to_upload), BATCH):
        batch = to_upload[i:i+BATCH]
        ops = [CommitOperationAdd(path_in_repo=f"{remote_prefix}/{f.name}", path_or_fileobj=str(f)) for f in batch]
        
        for attempt in range(10):
            try:
                api.create_commit(repo_id=SPACE_ID, repo_type="space", operations=ops,
                    commit_message=f"{label} {i+len(batch)}/{len(to_upload)}")
                done += len(batch)
                el = time.time()-t0
                remaining = len(to_upload)-i-len(batch)
                rate = done/el if el else 1
                eta = remaining/rate if rate else 0
                print(f"  [{done}/{len(to_upload)}] {el:.0f}s, ETA {eta:.0f}s")
                break
            except Exception as e:
                wait = min(30*(attempt+1), 300)
                print(f"  retry {attempt+1}, wait {wait}s: {str(e)[:80]}")
                time.sleep(wait)
        time.sleep(DELAY)
    
    print(f"  {label} DONE: {done} in {time.time()-t0:.0f}s")

print(f"Starting at {time.strftime('%H:%M:%S')}")
upload("Web/backend/static/fotos_recortadas", "static/fotos_recortadas", "fotos")
upload("Web/backend/static/boletines_webp", "static/boletines_webp", "boletines_webp")
print("ALL DONE!")
