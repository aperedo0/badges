"""Overlay a projected silhouette crop (from silhouette.py) on the mockup outline at the same height."""
import sys, numpy as np
from PIL import Image
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/skills/badge-fresh-review/scripts')
import review_pack as RP
mock = RP.aligned(RP.load('/Users/antonioperedo/Desktop/badges/ruby_crown_claude_20261108/reference/crown.png'), (627, 55, 1000), int(900 * 0.78), 40)
mm = RP.silhouette(mock, 40)
b = np.asarray(Image.open(sys.argv[1])) > 0
ys, xs = np.nonzero(b); top, bot = ys.min(), ys.max(); s = 900 / (bot - top)
ba = np.asarray(Image.fromarray((b * 255).astype(np.uint8)).resize((round(b.shape[1] * s), round(b.shape[0] * s)))) > 127
ys, xs = np.nonzero(ba); H, W = mm.shape
yy, xx = ys + 40 - ys.min(), xs + int(W / 2 - (xs.min() + xs.max()) / 2)
ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W); c = np.zeros(mm.shape, bool); c[yy[ok], xx[ok]] = True
img = np.zeros(mm.shape + (3,), np.uint8); img[mm] = (150, 120, 20); img[c] = (0, 100, 160); img[mm & c] = (190, 190, 190)
Image.fromarray(img).resize((W // 2, H // 2)).save(sys.argv[2])
