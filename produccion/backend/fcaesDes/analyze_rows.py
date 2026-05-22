import os
from PIL import Image

def analyze_rows(img, initial_box):
    photo_area = img.crop(initial_box)
    gray = photo_area.convert('L')
    threshold = 240
    bw = gray.point(lambda x: 0 if x > threshold else 255, '1')
    
    width, height = bw.size
    pixels = bw.load()
    
    print(f"Analyzing rows for height {height}:")
    for y in range(height):
        row_density = sum(1 for x in range(width) if pixels[x, y] == 255) / width
        if y > height - 50 or y < 50:
            print(f"y={y}, density={row_density:.4f}")

def main():
    input_path = r"c:\Users\manu\Documents\Jovenes creadores\Dev\produccion\fcaesDes\2020\boletines_completos\AARON ADALID ESCOBEDO CONDE.jpg"
    img = Image.open(input_path)
    initial_guess = (5, 60, 230, 360)
    analyze_rows(img, initial_guess)

if __name__ == "__main__":
    main()
