import os
import urllib.request
import re
from urllib.parse import unquote

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

def download_bulletin(url, base_dir):
    match = re.search(r'/Desaparecidos/(\d{4})/', url)
    year = match.group(1) if match else "Desconocido"
    
    # Save to base_dir/YYYY/boletines_completos/
    full_dir = os.path.join(base_dir, year, "boletines_completos")
    if not os.path.exists(full_dir):
        os.makedirs(full_dir)
            
    filename = unquote(os.path.basename(url))
    full_path = os.path.join(full_dir, filename)
    
    if os.path.exists(full_path):
        return False, filename # Already exists
        
    try:
        # Fix: Properly encode the URL to handle spaces and special characters like 'ñ'
        parts = url.split('/')
        # The first 3 parts are 'https:', '', 'cobupem.edomex.gob.mx'
        # We need to quote the rest (the path)
        encoded_path = '/'.join([urllib.parse.quote(p) for p in parts[3:]])
        encoded_url = f"https://{parts[2]}/{encoded_path}"
        
        urllib.request.urlretrieve(encoded_url, full_path)
        return True, filename
    except Exception as e:
        print(f"  - Error downloading {filename}: {e}")
        return False, filename

def main():
    target_url = "https://cobupem.edomex.gob.mx/boletines-personas-desaparecidas"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Script is in Dev\produccion\python, base_dir is Dev\produccion\fcaesDes
    base_dir = os.path.join(current_dir, "..", "fcaesDes")
    
    print(f"Fetching bulletin list from {target_url}...")
    html = get_page_html(target_url)
    if not html:
        return
        
    urls = find_bulletin_urls(html)
    total = len(urls)
    print(f"Found {total} bulletins.")
    
    new_count = 0
    for i, url in enumerate(urls, 1):
        success, name = download_bulletin(url, base_dir)
        if success:
            new_count += 1
            print(f"[{i}/{total}] Downloaded: {name}")
        elif i % 100 == 0:
            print(f"[{i}/{total}] Checking existing files...")
    
    print(f"\nDownload complete. New items: {new_count}. Total: {total}.")

if __name__ == "__main__":
    main()
