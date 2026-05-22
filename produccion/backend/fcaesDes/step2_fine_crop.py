import os
from PIL import Image

def fine_crop(img, initial_box):
    """
    Refined crop logic that searches for white gaps to separate the photo from nearby text.
    """
    photo_area = img.crop(initial_box)
    gray = photo_area.convert('L')
    
    # Threshold to identify content vs background
    threshold = 240
    bw = gray.point(lambda x: 0 if x > threshold else 255, '1')
    
    width, height = bw.size
    pixels = bw.load()
    
    # 1. Find the right edge of the photo by looking for a vertical white gap
    best_right = width
    has_seen_dense_content = False
    for x in range(width):
        column_density = sum(1 for y in range(height) if pixels[x, y] == 255) / height
        if column_density > 0.15: # Significant content found
            has_seen_dense_content = True
        
        # If we have seen content and find an empty/gap column
        if has_seen_dense_content and column_density < 0.02:
            # Check if it remains a gap for at least 2 pixels to avoid noise within the photo
            is_gap = True
            for check_x in range(x, min(x + 2, width)):
                check_density = sum(1 for y in range(height) if pixels[check_x, y] == 255) / height
                if check_density > 0.05:
                    is_gap = False
                    break
            if is_gap:
                best_right = x
                break

    # 2. Get the final bounding box within the restricted width
    # We also trim the top and bottom based on the found content
    restricted_bw = bw.crop((0, 0, best_right, height))
    final_bbox = restricted_bw.getbbox()
    
    if final_bbox and has_seen_dense_content:
        left, top, right, bottom = initial_box
        return (left + final_bbox[0], top + final_bbox[1], left + final_bbox[2], top + final_bbox[3])
    
    return initial_box

def process_year_folder(year_path):
    full_dir = os.path.join(year_path, "boletines_completos")
    crop_dir = os.path.join(year_path, "fotos_recortadas")
    
    if not os.path.exists(full_dir):
        return

    if not os.path.exists(crop_dir):
        os.makedirs(crop_dir)

    print(f"Processing photos in: {year_path}")
    
    for filename in os.listdir(full_dir):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
            
        input_path = os.path.join(full_dir, filename)
        output_path = os.path.join(crop_dir, f"foto_{filename}")
        
        if os.path.exists(output_path):
            continue

        try:
            img = Image.open(input_path)
            size = img.size
            
            # Initial guess areas based on known bulletin sizes
            if size == (640, 480):
                initial_guess = (5, 60, 245, 380) # Widen to 245 to catch the gap-text transition
            elif size == (680, 528):
                initial_guess = (10, 80, 420, 450)
            else:
                initial_guess = (int(size[0]*0.02), int(size[1]*0.1), int(size[0]*0.5), int(size[1]*0.8))
            
            final_box = fine_crop(img, initial_guess)
            cropped = img.crop(final_box)
            cropped.save(output_path)
            print(f"  - Cropped: {filename}")
        except Exception as e:
            print(f"  - Error cropping {filename}: {e}")

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Base dir is Dev\produccion\fcaesDes
    base_dir = os.path.join(current_dir, "..", "fcaesDes")
    
    # Process each year folder
    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if os.path.isdir(folder_path) and folder.isdigit():
            process_year_folder(folder_path)

if __name__ == "__main__":
    main()
