"""specks.py <tris.npz> <id_rest.png> : dark pixels inside the eroded silhouette of an ID render (all faces emissive, bright),
then the triangles under each: their facing (n.view) at rest. Prints clusters."""
import sys, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_erosion, label, center_of_mass
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/diamond/codex_rest_20261011/approved5/tools')
from common import to_screen, CAM_POS
d = np.load(sys.argv[1]); P = d['P']; im = np.asarray(Image.open(sys.argv[2]).convert('RGB'), float)
H, W = im.shape[:2]; m = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(m)
S = to_screen(P.reshape(-1, 3)).reshape(-1, 3, 2)
for t in S: dr.polygon([tuple(p) for p in t], fill=255)
inside = binary_erosion(np.asarray(m) > 0, iterations=3)
from scipy.ndimage import median_filter
lum = im.max(-1); med = median_filter(lum, 7); dark = inside & (lum < 0.75 * med)
lab, n = label(dark); print('dark clusters inside:', n)
nrm = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); area = np.linalg.norm(nrm, axis=1); nrm /= np.maximum(area[:, None], 1e-12)
view = CAM_POS - P.mean(1); view /= np.linalg.norm(view, axis=1, keepdims=True); facing = (nrm * view).sum(1)
cen = S.mean(1)
for c in center_of_mass(dark, lab, range(1, n + 1))[:40]:
    y, x = c; dist = np.linalg.norm(cen - [x, y], axis=1); near = np.argsort(dist)[:6]
    print(f'  px ({x:.0f},{y:.0f}) lum {lum[int(round(y)), int(round(x))]:.0f}: nearest tris', [(int(k), d["MESH"][k], d["MAT"][k].split("/")[-1], round(float(facing[k]), 2), f'{area[k] / 2:.1e}') for k in near[:3]])
