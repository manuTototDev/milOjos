import os
import urllib.request
import re
from urllib.parse import unquote
from PIL import Image

def get_page_html(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error reading page {url}: {e}")
        return ""

def find_bulletin_urls(html):
    # Pattern to match image URLs in the boletines page
    # Pattern: /sites/.../files/images/Desaparecidos/YYYY/Month/Name.jpg
    pattern = r'/sites/cobupem\.edomex\.gob\.mx/files/images/Desaparecidos/\d{4}/[^/]+/[^"]+\.jpg'
    found = re.findall(pattern, html)
    
    # Prepend domain if relative
    base_url = "https://cobupem.edomex.gob.mx"
    return list(set(base_url + url for url in found))

def process_bulletin(url, base_dir, crops):
    # Pattern: .../Desaparecidos/YYYY/...
    match = re.search(r'/Desaparecidos/(\d{4})/', url)
    year = match.group(1) if match else "Desconocido"
    
    # Structure: base_dir/YYYY/boletines_completos/ and base_dir/YYYY/fotos_recortadas/
    year_dir = os.path.join(base_dir, year)
    full_dir = os.path.join(year_dir, "boletines_completos")
    crop_dir = os.path.join(year_dir, "fotos_recortadas")
    
    for d in [full_dir, crop_dir]:
        if not os.path.exists(d):
            os.makedirs(d)
            
    filename = unquote(os.path.basename(url))
    full_path = os.path.join(full_dir, filename)
    crop_path = os.path.join(crop_dir, f"foto_{filename}")
    
    if os.path.exists(full_path) and os.path.exists(crop_path):
        return False, filename # Already exists
        
    try:
        # Download
        urllib.request.urlretrieve(url, full_path)
        
        # Crop
        img = Image.open(full_path)
        size = img.size
        
        if size in crops:
            cropped = img.crop(crops[size])
            cropped.save(crop_path)
        else:
            # Ratio fallback
            l, t, r, b = 0.05, 0.15, 0.45, 0.75
            cropped = img.crop((int(size[0]*l), int(size[1]*t), int(size[0]*r), int(size[1]*b)))
            cropped.save(crop_path)
            
        return True, filename
    except Exception as e:
        print(f"  - Error processing {filename}: {e}")
        return False, filename

def main():
    target_url = "https://cobupem.edomex.gob.mx/boletines-personas-desaparecidas"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Script is in Dev\produccion\python, base_dir is Dev\produccion\fcaesDes
    base_dir = os.path.join(current_dir, "..", "fcaesDes")
    
    crops = {
        (640, 480): (5, 70, 215, 355),
        (680, 528): (15, 95, 360, 435)
    }
    
    print(f"Reading page {target_url}...")
    html = get_page_html(target_url)
    if not html:
        return
        
    urls = find_bulletin_urls(html)
    print(f"Found {len(urls)} bulletin URLs.")
    
    processed_count = 0
    new_count = 0
    for i, url in enumerate(urls):
        success, filename = process_bulletin(url, base_dir, crops)
        processed_count += 1
        if success:
            new_count += 1
            print(f"[{processed_count}/{len(urls)}] New: {filename}")
        else:
            if i % 50 == 0: # Status every 50 existing items
                print(f"[{processed_count}/{len(urls)}] Skipping (already exists)...")
    
    print(f"\nProcessing complete. New items: {new_count}. Total items: {processed_count}.")

if __name__ == "__main__":
    main()
