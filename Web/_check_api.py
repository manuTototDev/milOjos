import requests
r = requests.get("https://manutototdev-mil-ojos-api.hf.space/?v=9")
d = r.json()
print(f"con_foto: {d['con_foto']}")
print(f"use_local_static: {d['debug_info']['use_local_static']}")
print(f"fotos_dir_exists: {d['debug_info']['fotos_dir_exists']}")
if 'fotos_count' in d['debug_info']:
    print(f"fotos_count: {d['debug_info']['fotos_count']}")
