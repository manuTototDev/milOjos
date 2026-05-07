"""Upload remaining images to HF Dataset. One process only, gentle rate."""
import os, time
from pathlib import Path
from huggingface_hub import HfApi, CommitOperationAdd

TOKEN = os.environ.get("HF_TOKEN", "")
DS = "manuTototDev/mil-ojos-images"
BATCH = 25
DELAY = 15  # generous delay between batches

api = HfApi(token=TOKEN)

def upload(local_dir, prefix, label):
    local = sorted(Path(local_dir).glob("*"))
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    local = [f for f in local if f.suffix.lower() in exts]
    existing = {os.path.basename(f) for f in api.list_repo_files(DS, repo_type="dataset") if f.startswith(prefix)}
    todo = [f for f in local if f.name not in existing]
    print(f"{label}: {len(todo)} pendientes ({len(existing)} ya subidas)")
    if not todo:
        return
    done = 0
    t0 = time.time()
    for i in range(0, len(todo), BATCH):
        batch = todo[i:i+BATCH]
        ops = [CommitOperationAdd(path_in_repo=f"{prefix}/{f.name}", path_or_fileobj=str(f)) for f in batch]
        for att in range(12):
            try:
                api.create_commit(repo_id=DS, repo_type="dataset", operations=ops,
                    commit_message=f"{label} {i+len(batch)}/{len(todo)}")
                done += len(batch)
                el = time.time() - t0
                rem = len(todo) - i - len(batch)
                rate = done / el if el else 1
                print(f"  [{done}/{len(todo)}] {el:.0f}s, ETA {rem/rate:.0f}s")
                break
            except Exception as e:
                wait = min(60 * (att + 1), 600)
                print(f"  retry {att+1}, wait {wait}s: {str(e)[:80]}")
                time.sleep(wait)
        time.sleep(DELAY)
    print(f"  {label} DONE: {done} in {time.time()-t0:.0f}s")

print(f"=== Single upload at {time.strftime('%H:%M:%S')} (batch=25, delay=15s) ===")
upload("Web/backend/static/fotos_recortadas", "fotos_recortadas", "fotos")
upload("Web/backend/static/boletines_webp", "boletines_webp", "boletines")
print(f"=== ALL DONE at {time.strftime('%H:%M:%S')} ===")
