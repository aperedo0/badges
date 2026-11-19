"""Project a crown geometry npz through the app's front camera; print its width table next to the mockup's.

Usage: silhouette.py GEOM.npz [OUT_overlay.png]
Also prints the badge box (cx, top, bottom) on the 1206 x 2622 app capture, for review.json.
"""
import sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/ruby_crown_claude_20261108/tools')
import screen_render as SR

MOCK = {0.1: 0.24, 0.2: 0.08, 0.3: 0.54, 0.4: 1.12, 0.5: 1.26, 0.6: 1.26, 0.7: 1.20, 0.8: 1.12, 0.9: 1.06}
d = np.load(sys.argv[1])
mask = Image.new('L', (1206, 2622), 0); dr = ImageDraw.Draw(mask)
for k in d.files:
    if not k.endswith('_v'):
        continue
    V = d[k]; T = d[k[:-2] + '_t']
    P, _ = SR.project(V)
    for tri in P[T]:
        dr.polygon([tuple(p) for p in tri], fill=255)
m = np.asarray(mask) > 0
ys, xs = np.nonzero(m)
top, bot = ys.min(), ys.max(); H = bot - top
print(f'box: cx {(xs.min() + xs.max()) / 2:.1f} top {top} bottom {bot} (height {H} px)')
print('from top  mockup  build')
for f, mv in MOCK.items():
    r = int(top + f * H); row = np.nonzero(m[r])[0]
    w = (row[-1] - row[0]) / H if len(row) else 0
    print(f'  {int(f * 100)}%     {mv:.2f}    {w:.2f}')
print(f'  widest  1.27    {(xs.max() - xs.min()) / H:.2f}')
if len(sys.argv) > 2:
    Image.fromarray((m * 255).astype(np.uint8)).crop((150, top - 40, 1056, bot + 40)).save(sys.argv[2])
