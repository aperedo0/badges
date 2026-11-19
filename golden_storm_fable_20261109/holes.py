"""Prove no piece has slits: every piece's triangles must cover its whole shape. Usage: holes.py candidateNN"""
import sys, json, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
C = sys.argv[1]
D = np.load(C + '/geometry.npz'); meta = json.load(open(C + '/parts.json')); S = meta['units_per_pixel']; CX = meta['center_x']; TOP = meta['top']
shapes = np.load(C + '/shapes.npz')
K = 4; total = 0
for i, part in enumerate(meta['parts']):
    if 'side walls' in part['name']:
        continue
    v = D[f'{i}_v']; t = D[f'{i}_t']; t = t[(v[t][:, :, 2] > 0).all(1)]
    px = np.c_[v[:, 0] / S + CX, (3.015 - v[:, 1]) / S + TOP] * K
    img = Image.new('L', (1254 * K, 1254 * K)); d = ImageDraw.Draw(img)
    for tri in t:
        d.polygon([tuple(px[j]) for j in tri], fill=255, outline=255)
    foot = np.asarray(img.resize((1254, 1254), Image.BOX)) > 100
    want = ndi.binary_erosion(shapes[part['name']], iterations=2)
    missing = want & ~foot
    lab, n = ndi.label(missing); sizes = ndi.sum(missing, lab, range(1, n + 1)) if n else np.array([0])
    print(f"{part['name'][:42]:42s} uncovered spots: {n:4d}  pixels {int(missing.sum()):5d}  largest {int(np.max(sizes))}")
    total += int(missing.sum())
print('TOTAL uncovered pixels:', total)
