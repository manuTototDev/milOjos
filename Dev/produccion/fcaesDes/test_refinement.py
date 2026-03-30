import os
from PIL import Image

def fine_crop_v2(img, initial_box):
    photo_area = img.crop(initial_box)
    gray = photo_area.convert('L')
    
    # More sensitive threshold for background?
    threshold = 245
    bw = gray.point(lambda x: 0 if x > threshold else 255, '1')
    
    width, height = bw.size
    pixels = bw.load()
    
    # Find the right edge of the photo by looking for a vertical white gap
    # Text is usually to the right of the photo.
    # We scan from left to right, looking for a column that is mostly white
    # AFTER we have seen some photo pixels.
    
    best_right = width
    found_photo = False
    for x in range(width):
        column_density = sum(1 for y in range(height) if pixels[x, y] == 255) / height
        if column_density > 0.2: # Significant content
            found_photo = True
        
        if found_photo and column_density < 0.03: # Gap found
            # Check if it stays a gap for a bit to avoid noise
            is_real_gap = True
            for check_x in range(x, min(x + 5, width)):
                check_density = sum(1 for y in range(height) if pixels[check_x, y] == 255) / height
                if check_density > 0.1:
                    is_real_gap = False
                    break
            if is_real_gap:
                best_right = x
                break

    # Now get the bbox within that restricted area
    restricted_bw = bw.crop((0, 0, best_right, height))
    final_bbox = restricted_bw.getbbox()
    
    if final_bbox:
        left, top, right, bottom = initial_box
        return (left + final_bbox[0], top + final_bbox[1], left + final_bbox[2], top + final_bbox[3])
    
    return initial_box

def main():
    input_path = r"c:\Users\manu\Documents\Jovenes creadores\Dev\produccion\fcaesDes\2020\boletines_completos\AARON ADALID ESCOBEDO CONDE.jpg"
    output_path_v1 = r"c:\Users\manu\Documents\Jovenes creadores\Dev\produccion\python\test_v1.jpg"
    output_path_v2 = r"c:\Users\manu\Documents\Jovenes creadores\Dev\produccion\python\test_v2.jpg"
    
    img = Image.open(input_path)
    # Initial guess for (640, 480)
    initial_guess = (5, 60, 230, 360)
    
    # Original logic (approx)
    gray = img.crop(initial_guess).convert('L')
    bw = gray.point(lambda x: 0 if x > 240 else 255, '1')
    bbox1 = bw.getbbox()
    if bbox1:
        v1_box = (initial_guess[0]+bbox1[0], initial_guess[1]+bbox1[1], initial_guess[0]+bbox1[2], initial_guess[1]+bbox1[3])
        img.crop(v1_box).save(output_path_v1)
    
    # V2 logic
    v2_box = fine_crop_v2(img, initial_guess)
    img.crop(v2_box).save(output_path_v2)
    
    print(f"V1 box: {v1_box if 'v1_box' in locals() else 'None'}")
    print(f"V2 box: {v2_box}")

if __name__ == "__main__":
    main()
