import os
from PIL import Image

def crop_bulletin_photo(input_dir, output_dir):
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Standard crop coordinates (left, top, right, bottom)
    crops = {
        (640, 480): (5, 70, 215, 355),
        (680, 528): (15, 95, 360, 435)
    }

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')) and not filename.startswith('photo_'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"photo_{filename}")
            
            try:
                img = Image.open(input_path)
                size = img.size
                
                if size in crops:
                    cropped = img.crop(crops[size])
                    cropped.save(output_path)
                    print(f"Cropped photo from {filename} ({size}) and saved to {output_path}")
                else:
                    # Fallback or generic ratio-based crop if size is unknown
                    print(f"Unknown size {size} for {filename}, trying ratio-based crop...")
                    l, t, r, b = 0.05, 0.15, 0.45, 0.75 # Default ratios
                    cropped = img.crop((int(size[0]*l), int(size[1]*t), int(size[0]*r), int(size[1]*b)))
                    cropped.save(output_path)
                    print(f"Cropped with ratio-based fallback for {filename}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(current_dir, "..", "fcaesDes")
    output_dir = os.path.join(input_dir, "cropped_photos")
    
    crop_bulletin_photo(input_dir, output_dir)
