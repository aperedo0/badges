"""Jagged edge hunt: zooms of every part of the badge, from the front and while it turns.

Usage: zoom.py candidateNN
Writes into the candidate folder:
  zoom_front_1..3.png   the front in three bands at 5x (every pixel of the badge is in one of them)
  zoom_turn_<pose>.png  each turning pose at 4x
  finish_real_front.png the front at the phone's real pixels
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
C = Path(__file__).resolve().parent / sys.argv[1]
f = Image.open(C / 'app/front.png').convert('RGB')
x0, y0, x1, y1 = 384, 348, 820, 788
f.crop((x0, y0, x1, y1)).save(C / 'finish_real_front.png')
bands = 3; h = (y1 - y0) // bands + 12
for b in range(bands):
    top = y0 + b * ((y1 - y0) // bands) - 6
    f.crop((x0, top, x1, top + h)).resize(((x1 - x0) * 5, h * 5), Image.NEAREST).save(C / f'zoom_front_{b + 1}.png')
for pose in ['early_turn', 'turn45', 'side_left', 'turn135', 'back', 'turn225']:
    p = C / 'app' / (pose + '.png')
    if not p.exists():
        continue
    g = Image.open(p).convert('RGB'); a = np.asarray(g).astype(int)
    sat = ((a.max(2) - a.min(2)) > 45) & (a.max(2) > 90)
    sat[:, :300] = False; sat[:, 900:] = False; sat[:110] = False
    rows = np.nonzero(sat.sum(1) > 3)[0]
    start = rows[0]; end = start
    for r in rows[1:]:
        if r - end > 25:
            break
        end = r
    cols = np.nonzero(sat[start:end + 1].sum(0) > 0)[0]
    box = (cols.min() - 12, start - 12, cols.max() + 12, end + 12)
    t = g.crop(box); k = 4 if t.size[0] * 4 <= 1900 else 3
    t.resize((t.size[0] * k, t.size[1] * k), Image.NEAREST).save(C / f'zoom_turn_{pose}.png')
print('zooms written')
