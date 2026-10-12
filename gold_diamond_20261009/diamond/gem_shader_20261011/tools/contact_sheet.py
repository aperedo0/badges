"""contact_sheet.py <out.png> <cols> <crop l,t,r,b> <scale> <label=img.png> ... : a grid of cropped Home shots."""
import sys
from PIL import Image, ImageDraw
out, cols, crop, scale = sys.argv[1], int(sys.argv[2]), tuple(int(v) for v in sys.argv[3].split(',')), float(sys.argv[4])
items = [a.split('=', 1) for a in sys.argv[5:]]
w, h = int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale); rows = (len(items) + cols - 1) // cols
sheet = Image.new('RGB', (w * cols, (h + 18) * rows), (0, 0, 0)); d = ImageDraw.Draw(sheet)
for i, (label, path) in enumerate(items):
    tile = Image.open(path).convert('RGB').crop(crop).resize((w, h), Image.LANCZOS)
    x, y = (i % cols) * w, (i // cols) * (h + 18); sheet.paste(tile, (x, y + 18)); d.text((x + 6, y + 3), label, fill=(255, 255, 255))
sheet.save(out); print(out, sheet.size)
