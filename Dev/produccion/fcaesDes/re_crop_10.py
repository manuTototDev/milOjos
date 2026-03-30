import os
from PIL import Image
from step2_fine_crop import fine_crop

def re_process_2020_10():
    year_path = r"c:\Users\manu\Documents\Jovenes creadores\Dev\produccion\fcaesDes\2020"
    full_dir = os.path.join(year_path, "boletines_completos")
    crop_dir = os.path.join(year_path, "fotos_recortadas") # Overwriting the original crop folder
    
    if not os.path.exists(crop_dir):
        os.makedirs(crop_dir)
        
    files = sorted([f for f in os.listdir(full_dir) if f.lower().endswith('.jpg')])[:10]
    
    print(f"Re-processing first 10 photos in 2020 with refined logic...")
    
    for filename in files:
        img = Image.open(os.path.join(full_dir, filename))
        size = img.size
        
        if size == (640, 480):
            initial_guess = (5, 60, 245, 380)
        else:
            initial_guess = (int(size[0]*0.02), int(size[1]*0.1), int(size[0]*0.5), int(size[1]*0.8))
            
        final_box = fine_crop(img, initial_guess)
        cropped = img.crop(final_box)
        output_path = os.path.join(crop_dir, f"foto_{filename}")
        cropped.save(output_path)
        print(f"  - Refined crop for: {filename}")

if __name__ == "__main__":
    re_process_2020_10()
