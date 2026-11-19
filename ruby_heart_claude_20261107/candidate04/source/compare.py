"""Side by side: reference, then app poses cropped around the badge at a common size."""
import sys
import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path
ROOT = Path('/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107')
cand = Path(sys.argv[1]); poses = sys.argv[3].split(',') if len(sys.argv) > 3 else ['front']
SIZE = 520
def crop_badge(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    top = a[120:1500, 250:950]
    lum = top.max(2)
    sat = top.max(2) - top.min(2)
    mask = (sat > 45) & (lum > 60)
    ys, xs = np.nonzero(mask); xs = xs + 250
    y0, y1 = ys.min() + 120, ys.max() + 120
    # the floor reflection sits below the badge: cut at the first gap row
    rows = mask.any(1)
    yy = np.nonzero(rows)[0]
    gaps = np.nonzero(np.diff(yy) > 12)[0]
    if len(gaps): y1 = yy[gaps[0]] + 120
    sel = ys + 120 <= y1
    x0, x1 = xs[sel].min(), xs[sel].max()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; h = max(y1 - y0, x1 - x0) * 1.08
    return Image.open(path).convert('RGB').crop((int(cx - h / 2), int(cy - h / 2), int(cx + h / 2), int(cy + h / 2)))
import os
if os.environ.get('REF2'):
    r2 = Image.open(ROOT / 'reference2/front.png').convert('RGB'); hh = r2.height
    panels = [('reference', r2.crop((r2.width // 2 - int(hh * 0.55), 0, r2.width // 2 + int(hh * 0.55) - 30, hh)))]
else:
    panels = [('reference', Image.open(ROOT / 'reference.png').convert('RGB').crop((95, 95, 1150, 1150)))]
import sys as _s
_s.path.insert(0, str(ROOT / 'tools'))
import screen_render as SR
P2, _ = SR.project(np.array([[-2.76, 0.27, 0], [2.76, 0.27, 0], [0, 2.995, 0], [0, -2.455, 0]]))
x0, x1, y0, y1 = P2[0, 0], P2[1, 0], P2[2, 1], P2[3, 1]
# same margins as the reference crop (heart 119..1126 x 123..1111 inside 95..1150)
sx = (x1 - x0) / (1126 - 119); sy = (y1 - y0) / (1111 - 123)
FRONT_BOX = (x0 - (119 - 95) * sx, y0 - (123 - 95) * sy, x1 + (1150 - 1126) * sx, y1 + (1150 - 1111) * sy)
for p in poses:
    if p == 'front':
        panels.append((p, Image.open(cand / 'app' / 'front.png').convert('RGB').crop(tuple(int(round(v)) for v in FRONT_BOX))))
    else:
        panels.append((p, crop_badge(cand / 'app' / f'{p}.png')))
out = Image.new('RGB', (SIZE * len(panels), SIZE + 24), (12, 12, 14))
d = ImageDraw.Draw(out)
for i, (name, im) in enumerate(panels):
    out.paste(im.resize((SIZE, SIZE), Image.LANCZOS), (i * SIZE, 24))
    d.text((i * SIZE + 6, 6), name, fill=(255, 255, 255))
out.save(sys.argv[2])
