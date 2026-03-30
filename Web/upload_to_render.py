"""
Script para subir los archivos estáticos al disco persistente de Render.

Uso después del primer deploy en Render:
  1. Instalar Render SSH: render ssh milojos-api
  2. O usar este script con scp/rsync si tienes acceso SSH

Alternativa: usar la API de Render para copiar archivos.
"""

import os
import subprocess
import sys

# Configuración
LOCAL_STATIC = os.path.join(os.path.dirname(__file__), "backend", "static")
LOCAL_DB = os.path.join(os.path.dirname(__file__), "backend", "face_database.pkl")
RENDER_SERVICE = "milojos-api"  # nombre del servicio en Render

def check_files():
    """Verifica que los archivos locales existan."""
    fotos = os.path.join(LOCAL_STATIC, "fotos_recortadas")
    bols = os.path.join(LOCAL_STATIC, "boletines")

    print("=== Verificación de archivos locales ===")
    print(f"  face_database.pkl: {'✓' if os.path.exists(LOCAL_DB) else '✗'} ({os.path.getsize(LOCAL_DB) / 1024 / 1024:.1f} MB)")
    
    if os.path.isdir(fotos):
        n = len(os.listdir(fotos))
        print(f"  fotos_recortadas/: ✓ ({n} archivos)")
    else:
        print("  fotos_recortadas/: ✗")

    if os.path.isdir(bols):
        n = len(os.listdir(bols))
        print(f"  boletines/: ✓ ({n} archivos)")
    else:
        print("  boletines/: ✗")

def create_tar():
    """Crea un archivo tar.gz con los datos para subir a Render."""
    print("\n=== Creando archivo comprimido ===")
    tar_file = os.path.join(os.path.dirname(__file__), "milojos_data.tar.gz")
    
    cmd = [
        "tar", "-czf", tar_file,
        "-C", os.path.dirname(LOCAL_DB), "face_database.pkl",
        "-C", os.path.dirname(LOCAL_STATIC), "static"
    ]
    
    print(f"  Ejecutando: {' '.join(cmd)}")
    print("  Esto puede tomar varios minutos (3GB de imágenes)...")
    subprocess.run(cmd, check=True)
    
    size_mb = os.path.getsize(tar_file) / 1024 / 1024
    print(f"  ✓ Archivo creado: {tar_file} ({size_mb:.0f} MB)")
    print(f"\n  Para subir a Render:")
    print(f"    1. render ssh {RENDER_SERVICE}")
    print(f"    2. cd /data")
    print(f"    3. tar -xzf milojos_data.tar.gz")
    return tar_file

if __name__ == "__main__":
    check_files()
    
    if "--tar" in sys.argv:
        create_tar()
    else:
        print("\n  Usa --tar para crear el archivo comprimido para Render")
        print("\n=== Instrucciones para Render ===")
        print("  1. Deploy the service from GitHub")
        print("  2. SSH into the service: render ssh milojos-api")
        print("  3. Copy face_database.pkl to /data/")
        print("  4. Copy static/ folder to /data/static/")
        print("  5. Restart the service")
