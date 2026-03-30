import os
import urllib.request
import re
import time
from urllib.parse import unquote
from PIL import Image, ImageChops

def get_page_html(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error reading page {url}: {e}")
        return ""

def find_bulletin_urls(html):
    pattern = r'/sites/cobupem\.edomex\.gob\.mx/files/images/Desaparecidos/\d{4}/[^/]+/[^"]+\.jpg'
    found = re.findall(pattern, html)
    base_url = "https://cobupem.edomex.gob.mx"
    return list(set(base_url + url for url in found))

def fine_crop(img, initial_box):
    """
    Attempts to refine the crop by finding the actual image boundaries 
    within the initial box, ignoring white background.
    """
    photo_area = img.crop(initial_box)
    
    # Convert to grayscale to simplify border detection
    gray = photo_area.convert('L')
    
    # Invert so white becomes black (0)
    # We use a threshold to handle "near-white"
    threshold = 240
    bw = gray.point(lambda x: 0 if x > threshold else 255, '1')
    
    # Find bounding box of non-zero (non-white original) pixels
    bbox = bw.getbbox()
    
    if bbox:
        # Map bbox back to original image coordinates
        left, top, right, bottom = initial_box
        new_left = left + bbox[0]
        new_top = top + bbox[1]
        new_right = left + bbox[2]
        new_bottom = top + bbox[3]
        return (new_left, new_top, new_right, new_bottom)
    
    return initial_box

def process_bulletin(url, base_dir):
    match = re.search(r'/Desaparecidos/(\d{4})/', url)
    year = match.group(1) if match else "Desconocido"
    
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
        return "EXISTS", filename
        
    try:
        # Download
        urllib.request.urlretrieve(url, full_path)
        
        # Load and Crop
        img = Image.open(full_path)
        size = img.size
        
        # Initial guess areas based on known bulletin sizes
        if size == (640, 480):
            initial_guess = (5, 60, 230, 360)
        elif size == (680, 528):
            initial_guess = (10, 80, 400, 450)
        else:
            # Generic ratio-based guess
            initial_guess = (int(size[0]*0.02), int(size[1]*0.1), int(size[0]*0.5), int(size[1]*0.8))
        
        # Refine crop to remove white borders
        final_box = fine_crop(img, initial_guess)
        cropped = img.crop(final_box)
        cropped.save(crop_path)
        
        return "NEW", filename
    except Exception as e:
        print(f"  - Error processing {filename}: {e}")
        return "ERROR", filename

def main():
    target_url = "https://cobupem.edomex.gob.mx/boletines-personas-desaparecidas"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(current_dir, "..", "fcaesDes")
    
    print(f"Initializing Bulletin Engine...")
    html = get_page_html(target_url)
    if not html:
        print("Failed to reach source page.")
        return
        
    urls = find_bulletin_urls(html)
    total = len(urls)
    print(f"Total bulletins discovered: {total}")
    
    new_items = 0
    errors = 0
    start_time = time.time()
    
    for i, url in enumerate(urls, 1):
        status, name = process_bulletin(url, base_dir)
        
        if status == "NEW":
            new_items += 1
            print(f"[{i}/{total}] Downloaded & Fine-Cropped: {name}")
        elif status == "ERROR":
            errors += 1
        
        # Progress update every 100 items even if skipped
        if i % 100 == 0:
            elapsed = time.time() - start_time
            print(f"--- Progress: {i}/{total} ({ (i/total)*100:.1f}%) | Elapsed: {elapsed/60:.1f} min ---")

    print(f"\n--- MISSION COMPLETE ---")
    print(f"Processed: {total} | New: {new_items} | Errors: {errors}")

if __name__ == "__main__":
    main()
