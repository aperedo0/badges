"""Side by side: crown mockup, then app poses cropped around the badge."""
import sys
import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path
ROOT = Path('/Users/antonioperedo/Desktop/badges/ruby_crown_claude_20261108')
cand = Path(sys.argv[1]); poses = sys.argv[3].split(',')
SIZE = 520
def crop_badge(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    top = a[150:1450, 150:1056]
    sat = top.max(2) - top.min(2); lum = top.max(2)
    m = (sat > 40) & (lum > 50)
    rows = np.nonzero(m.sum(1) > 3)[0]
    # stop at the first big gap below the badge (the floor reflection)
    gaps = np.nonzero(np.diff(rows) > 15)[0]
    y0 = rows[0]; y1 = rows[gaps[0]] if len(gaps) else rows[-1]
    cols = np.nonzero(m[y0:y1].sum(0) > 2)[0]
    x0, x1 = cols[0], cols[-1]
    cx, cy = (x0 + x1) / 2 + 150, (y0 + y1) / 2 + 150; h = max(y1 - y0, x1 - x0) * 1.12
    return Image.open(path).convert('RGB').crop((int(cx - h / 2), int(cy - h / 2), int(cx + h / 2), int(cy + h / 2)))
panels = [('mockup', Image.open(ROOT / 'reference/crown.png').convert('RGB').crop((0, 20, 1254, 1080)))]
for p in poses:
    panels.append((p, crop_badge(cand / 'app' / f'{p}.png')))
out = Image.new('RGB', (SIZE * len(panels), SIZE + 24), (12, 12, 14))
d = ImageDraw.Draw(out)
for i, (name, im) in enumerate(panels):
    im = im.resize((SIZE, int(SIZE * im.height / im.width)))
    out.paste(im, (i * SIZE, 24 + (SIZE - im.height) // 2))
    d.text((i * SIZE + 6, 6), name, fill=(255, 255, 255))
out.save(sys.argv[2])
