import os
from PIL import Image

def fine_crop_refined(img, initial_box):
    photo_area = img.crop(initial_box)
    gray = photo_area.convert('L')
    
    # Background threshold
    threshold = 240
    bw = gray.point(lambda x: 0 if x > threshold else 255, '1')
    
    width, height = bw.size
    pixels = bw.load()
    
    # Find the right gap (photo/text separator)
    best_right = width
    has_seen_content = False
    for x in range(width):
        column_density = sum(1 for y in range(height) if pixels[x, y] == 255) / height
        if column_density > 0.3:
            has_seen_content = True
        
        # If we've seen content and now see a very empty column
        if has_seen_content and column_density < 0.02:
            # Check for a small gap (2 pixels)
            if x + 1 < width:
                next_density = sum(1 for y in range(height) if pixels[x+1, y] == 255) / height
                if next_density < 0.02:
                    best_right = x
                    break
    
    # Find the bottom gap if any (sometimes text below)
    # Similar logic for rows
    best_bottom = height
    has_seen_rows = False
    for y in range(height):
        # row_density = sum(1 for x in range(best_right) if pixels[x, y] == 255) / best_right if best_right > 0 else 1
        # Wait, sum is easier
        row_sum = sum(1 for x in range(best_right) if pixels[x, y] == 255)
        row_density = row_sum / best_right if best_right > 0 else 0
        
        if row_density > 0.3:
            has_seen_rows = True
        if has_seen_rows and row_density < 0.02:
            if y + 1 < height:
                row_sum_next = sum(1 for x in range(best_right) if pixels[x, y+1] == 255)
                row_density_next = row_sum_next / best_right if best_right > 0 else 0
                if row_density_next < 0.02:
                    best_bottom = y
                    break

    # Now crop the BW and get regular bbox for fine margin trimming
    restricted_bw = bw.crop((0, 0, best_right, best_bottom))
    final_bbox = restricted_bw.getbbox()
    
    if final_bbox:
        left, top, right, bottom = initial_box
        return (left + final_bbox[0], top + final_bbox[1], left + final_bbox[2], top + final_bbox[3])
    
    return initial_box

def process_test(limit=10):
    year_path = r"c:\Users\manu\Documents\Jovenes creadores\Dev\produccion\fcaesDes\2020"
    full_dir = os.path.join(year_path, "boletines_completos")
    crop_dir = os.path.join(year_path, "fotos_recortadas_v2")
    
    if not os.path.exists(crop_dir):
        os.makedirs(crop_dir)
        
    files = sorted([f for f in os.listdir(full_dir) if f.lower().endswith('.jpg')])[:limit]
    
    for filename in files:
        img = Image.open(os.path.join(full_dir, filename))
        size = img.size
        
        if size == (640, 480):
            initial_guess = (5, 60, 240, 380) # Slightly wider guess to allow gap detection
        else:
            initial_guess = (int(size[0]*0.02), int(size[1]*0.1), int(size[0]*0.5), int(size[1]*0.8))
            
        final_box = fine_crop_refined(img, initial_guess)
        cropped = img.crop(final_box)
        cropped.save(os.path.join(crop_dir, f"foto_{filename}"))
        print(f"Processed: {filename} -> {final_box}")

if __name__ == "__main__":
    process_test()
