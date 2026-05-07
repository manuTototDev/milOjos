import shutil, time, os

print(f"=== Creando ZIPs a las {time.strftime('%H:%M:%S')} ===")

print("1. Comprimiendo fotos...")
t0 = time.time()
shutil.make_archive("Web/fotos", "zip", "Web/backend/static/fotos_recortadas")
size_mb = os.path.getsize("Web/fotos.zip") / (1024*1024)
print(f"   - fotos.zip creado en {time.time()-t0:.1f}s -- Tamaño: {size_mb:.1f} MB")

print("2. Comprimiendo boletines...")
t1 = time.time()
shutil.make_archive("Web/boletines", "zip", "Web/backend/static/boletines_webp")
size_mb2 = os.path.getsize("Web/boletines.zip") / (1024*1024)
print(f"   - boletines.zip creado en {time.time()-t1:.1f}s -- Tamaño: {size_mb2:.1f} MB")

print("=== Compresión completada ===")
