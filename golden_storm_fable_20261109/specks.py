"""Count single dark pixels on the badge in each captured pose (a pixel clearly darker than all eight neighbours
in an otherwise smooth area). Usage: specks.py candidateNN"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
C = Path(__file__).resolve().parent / sys.argv[1]
total = 0
for pose in ['front', 'early_turn', 'turn45', 'turn135', 'back', 'turn225']:
    p = C / 'app' / (pose + '.png')
    if not p.exists():
        continue
    a = np.asarray(Image.open(p).convert('RGB')).astype(float) / 255; l = a @ np.array([.2126, .7152, .0722])
    fp = np.ones((3, 3), bool); fp[1, 1] = False
    nmin = ndi.minimum_filter(l, footprint=fp); nmax = ndi.maximum_filter(l, footprint=fp)
    m = (nmin - l > .05) & (nmax - nmin < .06)
    m[:110] = False; m[1300:] = False
    ys, xs = np.nonzero(m)
    found = [(int(x), int(y), round(float(l[y, x]), 2), round(float(nmin[y, x]), 2)) for x, y in zip(xs, ys)]
    total += len(found); print(f'{pose:11s} single dark pixels: {len(found)}', found[:6])
print('TOTAL', total)
