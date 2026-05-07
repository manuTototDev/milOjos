import os
from huggingface_hub import HfApi

TOKEN = os.environ.get("HF_TOKEN", "")
# We will upload directly to the API Space so they are available locally
SPACE_ID = "manuTototDev/mil-ojos-api"

api = HfApi(token=TOKEN)

print("Subiendo fotos.zip...")
api.upload_file(
    path_or_fileobj="Web/fotos.zip",
    path_in_repo="fotos.zip",
    repo_id=SPACE_ID,
    repo_type="space"
)
print("fotos.zip subido exitosamente.")

print("Subiendo boletines.zip...")
api.upload_file(
    path_or_fileobj="Web/boletines.zip",
    path_in_repo="boletines.zip",
    repo_id=SPACE_ID,
    repo_type="space"
)
print("boletines.zip subido exitosamente.")
print("=== Todo arriba ===")
