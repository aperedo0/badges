"""compare.py <before.png> <after.png> <out.png> [label] : 4x nearest zooms of the two outline areas with the most near white pixels in the before shot, before left, after right."""
import sys, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_erosion
b = Image.open(sys.argv[1]).convert('RGB'); a = Image.open(sys.argv[2]).convert('RGB')
x = np.asarray(b).astype(int)[330:830, 300:906]; L = x.mean(-1); m = L > 55; rim = m & ~binary_erosion(m, iterations=2)
wh = (x.min(-1) > 190) & rim
H, _, _ = np.histogram2d(*np.nonzero(wh), bins=[10, 12], range=[[0, 500], [0, 606]])
order = np.argsort(H.ravel())[::-1][:2]
out = Image.new('RGB', (1300, 1300), (0, 0, 0)); dr = ImageDraw.Draw(out)
for r, o in enumerate(order):
    iy, ix = np.unravel_index(o, H.shape); cy, cx = 330 + iy * 50 + 25, 300 + ix * 50 + 25
    box = (cx - 40, cy - 40, cx + 40, cy + 40)
    out.paste(b.crop(box).resize((640, 640), Image.NEAREST), (0, r * 655)); out.paste(a.crop(box).resize((640, 640), Image.NEAREST), (655, r * 655))
dr.text((8, 6), 'before', fill=(255, 255, 0)); dr.text((663, 6), 'after ' + (sys.argv[4] if len(sys.argv) > 4 else ''), fill=(255, 255, 0))
out.save(sys.argv[3])
