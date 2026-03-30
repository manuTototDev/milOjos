"""
actualizar_web.py — Script de actualización diaria de Mil Ojos
Pipeline completo: scrape → crop → index → deploy

Ejecutar diariamente (Task Scheduler / cron):
    python actualizar_web.py

Pasos:
    1. Descargar boletines nuevos de COBUPEM
    2. Recortar fotos faciales con InsightFace
    3. Copiar imágenes al backend estático
    4. Re-indexar la base de datos de embeddings faciales
    5. Reiniciar el backend (para recargar la DB)
"""
import os
import sys
import subprocess
import shutil
import glob
import json
from datetime import datetime

# ── Rutas ──────────────────────────────────────────────────────────
ROOT       = os.path.dirname(os.path.abspath(__file__))
WEB_DIR    = os.path.join(ROOT, '..', 'Web')
DEV_DIR    = os.path.join(ROOT, '..', 'Dev', 'produccion')

FCAES_DIR  = os.path.join(DEV_DIR, 'fcaesDes')
PYTHON_DIR = os.path.join(DEV_DIR, 'python')
RNPDNO_DIR = os.path.join(DEV_DIR, 'rnpdno')

BACKEND_DIR    = os.path.join(WEB_DIR, 'backend')
STATIC_FOTOS   = os.path.join(BACKEND_DIR, 'static', 'fotos_recortadas')
STATIC_BOLS    = os.path.join(BACKEND_DIR, 'static', 'boletines')
DB_FILE        = os.path.join(BACKEND_DIR, 'face_database.pkl')

YEARS = ['2020', '2021', '2022', '2023', '2024', '2025', '2026']

LOG_FILE = os.path.join(ROOT, 'update_log.json')


def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f'[{ts}] {msg}')


def run_script(script_path, cwd=None):
    """Ejecuta un script Python y retorna True si tuvo éxito."""
    if not os.path.exists(script_path):
        log(f'  ⚠ Script no encontrado: {script_path}')
        return False
    cwd = cwd or os.path.dirname(script_path)
    log(f'  → Ejecutando {os.path.basename(script_path)}...')
    result = subprocess.run(
        [sys.executable, script_path],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=600  # 10 min max
    )
    if result.returncode != 0:
        log(f'  ✗ Error: {result.stderr[:500]}')
        return False
    # Mostrar últimas líneas del output
    lines = result.stdout.strip().split('\n')
    for line in lines[-5:]:
        log(f'    {line}')
    return True


def step1_download_bulletins():
    """Paso 1: Descargar boletines nuevos de COBUPEM."""
    log('═══ PASO 1: Descargar boletines de COBUPEM ═══')
    script = os.path.join(FCAES_DIR, 'step1_download.py')
    return run_script(script)


def step2_crop_faces():
    """Paso 2: Recortar fotos faciales de los boletines."""
    log('═══ PASO 2: Recortar fotos faciales ═══')
    script = os.path.join(FCAES_DIR, 'step2_fine_crop.py')
    return run_script(script)


def step3_copy_images():
    """Paso 3: Copiar imágenes nuevas al backend estático."""
    log('═══ PASO 3: Copiar imágenes al backend ═══')
    os.makedirs(STATIC_FOTOS, exist_ok=True)
    os.makedirs(STATIC_BOLS, exist_ok=True)
    
    total_fotos = 0
    total_bols = 0
    
    for year in YEARS:
        # Fotos recortadas
        src_fotos = os.path.join(FCAES_DIR, year, 'fotos_recortadas')
        if os.path.exists(src_fotos):
            for f in glob.glob(os.path.join(src_fotos, '*.jpg')):
                dest = os.path.join(STATIC_FOTOS, f'{year}_{os.path.basename(f)}')
                if not os.path.exists(dest):
                    shutil.copy2(f, dest)
                    total_fotos += 1
        
        # Boletines completos
        src_bols = os.path.join(FCAES_DIR, year, 'boletines_completos')
        if os.path.exists(src_bols):
            for f in glob.glob(os.path.join(src_bols, '*.jpg')):
                dest = os.path.join(STATIC_BOLS, f'{year}_{os.path.basename(f)}')
                if not os.path.exists(dest):
                    shutil.copy2(f, dest)
                    total_bols += 1
    
    log(f'  Fotos nuevas: {total_fotos}')
    log(f'  Boletines nuevos: {total_bols}')
    return True


def step4_reindex():
    """Paso 4: Re-indexar embeddings faciales."""
    log('═══ PASO 4: Re-indexar base de datos facial ═══')
    script = os.path.join(PYTHON_DIR, 'step3_index_faces.py')
    success = run_script(script)
    
    if success:
        # Copiar la DB generada al backend
        src_db = os.path.join(PYTHON_DIR, 'face_database.pkl')
        if os.path.exists(src_db):
            shutil.copy2(src_db, DB_FILE)
            size_mb = os.path.getsize(DB_FILE) / (1024 * 1024)
            log(f'  DB copiada: {size_mb:.1f} MB')
    return success


def save_log(results):
    """Guarda un log de la última actualización."""
    entry = {
        'timestamp': datetime.now().isoformat(),
        'steps': results,
        'fotos_total': len(glob.glob(os.path.join(STATIC_FOTOS, '*.jpg'))),
        'boletines_total': len(glob.glob(os.path.join(STATIC_BOLS, '*.jpg'))),
        'db_size_mb': round(os.path.getsize(DB_FILE) / (1024*1024), 1) if os.path.exists(DB_FILE) else 0,
    }
    
    history = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            history = json.load(f)
    
    history.append(entry)
    # Mantener últimos 30 registros
    history = history[-30:]
    
    with open(LOG_FILE, 'w') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    log(f'Log guardado: {LOG_FILE}')


def main():
    print()
    log('╔══════════════════════════════════════════════╗')
    log('║  MIL OJOS — Actualización diaria            ║')
    log('╚══════════════════════════════════════════════╝')
    print()
    
    results = {}
    
    # Paso 1: Descargar
    results['download'] = step1_download_bulletins()
    
    # Paso 2: Recortar
    results['crop'] = step2_crop_faces()
    
    # Paso 3: Copiar al backend
    results['copy'] = step3_copy_images()
    
    # Paso 4: Re-indexar
    results['reindex'] = step4_reindex()
    
    # Resumen
    print()
    log('═══ RESUMEN ═══')
    for step, ok in results.items():
        status = '✓' if ok else '✗'
        log(f'  {status} {step}')
    
    fotos = len(glob.glob(os.path.join(STATIC_FOTOS, '*.jpg')))
    bols  = len(glob.glob(os.path.join(STATIC_BOLS, '*.jpg')))
    log(f'  Fotos totales: {fotos}')
    log(f'  Boletines totales: {bols}')
    
    save_log(results)
    
    print()
    log('Actualización completada.')
    log('Reinicia el backend para cargar la nueva DB:')
    log('  python -m uvicorn main:app --host 0.0.0.0 --port 8000')


if __name__ == '__main__':
    main()
