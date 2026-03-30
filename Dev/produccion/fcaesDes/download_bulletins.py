import os
import urllib.request
from urllib.parse import unquote

def download_bulletins(urls, output_dir):
    # Create directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Download images
    for url in urls:
        filename = unquote(os.path.basename(url))
        filepath = os.path.join(output_dir, filename)
        
        print(f"Downloading {url} to {filepath}...")
        try:
            # Simple check if file already exists to avoid re-downloading
            if os.path.exists(filepath):
                print(f"File {filename} already exists, skipping...")
                continue
                
            urllib.request.urlretrieve(url, filepath)
            print(f"Successfully downloaded {filename}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")

if __name__ == "__main__":
    # URLs of the first 3 bulletins from https://cobupem.edomex.gob.mx/boletines-personas-desaparecidas
    bulletin_urls = [
        "https://cobupem.edomex.gob.mx/sites/cobupem.edomex.gob.mx/files/images/Desaparecidos/2026/Febrero/NORMA%20DIANEY%20GARCIA%20GARCIA.jpg",
        "https://cobupem.edomex.gob.mx/sites/cobupem.edomex.gob.mx/files/images/Desaparecidos/2026/Febrero/ISABEL%20CASTILLO%20MACEDA.jpg",
        "https://cobupem.edomex.gob.mx/sites/cobupem.edomex.gob.mx/files/images/Desaparecidos/2026/Febrero/ABEL%20BARRAGAN%20JUAREZ.jpg"
    ]

    # Target directory relative to this script's location
    # Script is in Dev\produccion\python, fcaesDes is in Dev\produccion\fcaesDes
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(current_dir, "..", "fcaesDes")
    
    download_bulletins(bulletin_urls, target_dir)
