"""Crops a transparent coin render to the tier-art footprint (coin width = 108/120 of the square, centered)
and writes a 600 x 600 RGBA PNG. Resizes in premultiplied alpha so the edge has no dark fringe.
Usage: /usr/local/bin/python3 make_still.py <render.png> <out.png>"""
import sys
import numpy as np
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGBA')
a = np.asarray(im)[..., 3]
ys, xs = np.nonzero(a > 8)
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
w = x1 - x0 + 1; h = y1 - y0 + 1
cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
side = w * 120 / 108
box = (round(cx - side / 2), round(cy - side / 2), round(cx + side / 2), round(cy + side / 2))
sq = im.crop(box).convert('RGBa').resize((600, 600), Image.LANCZOS).convert('RGBA')
sq.save(out, optimize=True)
print(out, 'coin bbox w x h', w, h, 'crop', box)
