#!/usr/bin/env python3
"""
Fix the square-padding bug: re-crop a lead photo tightly (rectangular,
no square-canvas padding), and if a side is still under 501px, pad with
white (never upscale actual content).
"""
import sys
from PIL import Image

def tight_bbox(img, cutoff=150, row_frac=0.01):
    rgb_img = img.convert('RGB')
    w, h = rgb_img.size
    px = rgb_img.load()
    xs = list(range(0, w, max(1, w // 300)))
    ys = list(range(0, h, max(1, h // 300)))
    def row_is_content(y):
        cnt = sum(1 for x in xs if min(px[x, y]) < cutoff)
        return (cnt / len(xs)) > row_frac
    def col_is_content(x):
        cnt = sum(1 for y in ys if min(px[x, y]) < cutoff)
        return (cnt / len(ys)) > row_frac
    left = 0
    for x in range(w):
        if col_is_content(x):
            left = x; break
    else:
        return (0, 0, w, h)
    right = w - 1
    for x in range(w - 1, -1, -1):
        if col_is_content(x):
            right = x; break
    top = 0
    for y in range(h):
        if row_is_content(y):
            top = y; break
    else:
        return (0, 0, w, h)
    bottom = h - 1
    for y in range(h - 1, -1, -1):
        if row_is_content(y):
            bottom = y; break
    return (left, top, right + 1, bottom + 1)

def process_image(input_path, output_path, min_size=501):
    img = Image.open(input_path)
    if img.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = bg
    else:
        img = img.convert('RGB')
    w, h = img.size
    left, top, right, bottom = tight_bbox(img, cutoff=150, row_frac=0.01)
    content_w = right - left
    content_h = bottom - top
    pad_x = int(content_w * 0.025)
    pad_y = int(content_h * 0.025)
    left = max(0, left - pad_x)
    top = max(0, top - pad_y)
    right = min(w, right + pad_x)
    bottom = min(h, bottom + pad_y)
    cropped = img.crop((left, top, right, bottom))

    cw, ch = cropped.size
    new_w = max(cw, min_size)
    new_h = max(ch, min_size)
    if (new_w, new_h) != (cw, ch):
        canvas = Image.new('RGB', (new_w, new_h), (255, 255, 255))
        x = (new_w - cw) // 2
        y = (new_h - ch) // 2
        canvas.paste(cropped, (x, y))
        cropped = canvas

    cropped.save(output_path, quality=92)
    return cropped.size

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 fix_square_bug.py <input> <output>")
        sys.exit(1)
    size = process_image(sys.argv[1], sys.argv[2])
    print(f"OK {sys.argv[1]} -> {sys.argv[2]} size={size}")
