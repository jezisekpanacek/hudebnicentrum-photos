#!/usr/bin/env python3
import sys
from PIL import Image

def pad_image(input_path, output_path, min_size=501):
    img = Image.open(input_path).convert('RGB')
    w, h = img.size
    new_w = max(w, min_size)
    new_h = max(h, min_size)
    if (new_w, new_h) == (w, h):
        img.save(output_path, quality=92)
        return (w, h)
    canvas = Image.new('RGB', (new_w, new_h), (255, 255, 255))
    x = (new_w - w) // 2
    y = (new_h - h) // 2
    canvas.paste(img, (x, y))
    canvas.save(output_path, quality=92)
    return (new_w, new_h)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 pad_to_min.py <input> <output>")
        sys.exit(1)
    size = pad_image(sys.argv[1], sys.argv[2])
    print(f"OK {sys.argv[1]} -> {sys.argv[2]} size={size}")
