"""check_v2.py <tier> <before.png> <after.png> : interior check (pixels 8+ px inside the projected silhouette must match the before
shot, mean absolute difference under 1 level) and a whole contour tile sheet (quad.py style) written next to the after shot."""
import sys, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from common import to_screen
t, bp, ap = sys.argv[1:4]
d = np.load(f'/Users/antonioperedo/Desktop/badges/edge_fix_20261010/model/{t}.npz')
scr = to_screen(d['ALLP'].reshape(-1, 3)).reshape(-1, 3, 2)
im = Image.new('L', (1206, 2622), 0); dr = ImageDraw.Draw(im)
for tri in scr: dr.polygon([tuple(p) for p in tri], fill=255)
sil = np.asarray(im) > 127; dist = distance_transform_edt(sil)
b = np.asarray(Image.open(bp).convert('RGB')).astype(float); a = np.asarray(Image.open(ap).convert('RGB')).astype(float)
inner = dist >= 8; diff = np.abs(a - b).max(-1)
print(f'{t}: interior (8+ px inside) mean abs diff {np.abs(a - b)[inner].mean():.3f}, pixels differing > 8 levels {int((diff[inner] > 8).sum())} of {int(inner.sum())}; band (< 8 px) changed px {int((diff[sil & ~inner] > 8).sum())}')
