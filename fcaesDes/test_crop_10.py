import os
from PIL import Image

def fine_crop(img, initial_box):
    """
    Attempts to refine the crop by finding the actual image boundaries 
    within the initial box, ignoring white background.
    """
    # Safety check for image size
    if img.size[0] < initial_box[2] or img.size[1] < initial_box[3]:
        return (0, 0, img.size[0], img.size[1])

    photo_area = img.crop(initial_box)
    gray = photo_area.convert('L')
    
    # Threshold to handle "near-white" background
    threshold = 240
    bw = gray.point(lambda x: 0 if x > threshold else 255, '1')
    
    bbox = bw.getbbox()
    if bbox:
        left, top, right, bottom = initial_box
        return (left + bbox[0], top + bbox[1], left + bbox[2], top + bbox[3])
    
    return initial_box

def process_year_folder_limited(year_path, limit=10):
    full_dir = os.path.join(year_path, "boletines_completos")
    crop_dir = os.path.join(year_path, "fotos_recortadas")
    
    if not os.path.exists(full_dir):
        print(f"Directory not found: {full_dir}")
        return

    if not os.path.exists(crop_dir):
        os.makedirs(crop_dir)

    print(f"Processing first {limit} photos in: {year_path}")
    
    count = 0
    files = sorted(os.listdir(full_dir))
    
    for filename in files:
        if count >= limit:
            break
            
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
            
        input_path = os.path.join(full_dir, filename)
        output_path = os.path.join(crop_dir, f"foto_{filename}")
        
        # We'll overwrite for the test to make sure it works
        # if os.path.exists(output_path):
        #     continue

        try:
            img = Image.open(input_path)
            size = img.size
            
            # Initial guess areas based on known bulletin sizes
            if size == (640, 480):
                initial_guess = (5, 60, 230, 360)
            elif size == (680, 528):
                initial_guess = (10, 80, 400, 450)
            else:
                initial_guess = (int(size[0]*0.02), int(size[1]*0.1), int(size[0]*0.5), int(size[1]*0.8))
            
            final_box = fine_crop(img, initial_guess)
            cropped = img.crop(final_box)
            cropped.save(output_path)
            print(f"  [{count+1}/{limit}] Cropped: {filename}")
            count += 1
        except Exception as e:
            print(f"  - Error cropping {filename}: {e}")

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(current_dir, "..", "fcaesDes")
    year_2020_path = os.path.join(base_dir, "2020")
    
    if os.path.exists(year_2020_path):
        process_year_folder_limited(year_2020_path, limit=10)
    else:
        print(f"2020 folder not found at {year_2020_path}")

if __name__ == "__main__":
    main()
