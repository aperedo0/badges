"""montage.py <out.png> <label=img.png> ... : crops each Home shot to the badge area and lays them side by side with labels."""
import sys
from PIL import Image, ImageDraw
import os
BOX = tuple(int(v) for v in os.environ.get('BOX', '150,100,1050,1000').split(','))
out = sys.argv[1]; items = [a.split('=', 1) for a in sys.argv[2:]]
tiles = [Image.open(p).convert('RGB').crop(BOX) for _, p in items]
w, h = tiles[0].size
sheet = Image.new('RGB', (w * len(tiles), h + 30), (0, 0, 0)); d = ImageDraw.Draw(sheet)
for i, ((label, _), t) in enumerate(zip(items, tiles)):
    sheet.paste(t, (i * w, 30)); d.text((i * w + 8, 8), label, fill=(255, 255, 255))
sheet.save(out); print(out, sheet.size)
