"""Find leaves (vivid green) and flowers or buds (cream) in the mockup: position, length, width, angle."""
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
im = Image.open('reference/stag.png').convert('RGB'); a = np.asarray(im).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
green = (g > 70) & (g > r + 20) & (g > b - 5) & (a.max(2) - a.min(2) > 35)
cream = (r > 170) & (g > 150) & (b > 110) & (r - b < 90) & (a.max(2) - a.min(2) < 95)
out = {}
for name, m, minarea, erode in (('leaves', green, 250, 2), ('cream', cream, 120, 1)):
    m2 = ndi.binary_opening(m, iterations=1)
    m2 = ndi.binary_fill_holes(ndi.binary_closing(m2, iterations=3))
    m3 = ndi.binary_erosion(m2, iterations=erode)
    lab, n = ndi.label(m3)
    items = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(xs) < minarea: continue
        c = np.array([xs.mean(), ys.mean()])
        cov = np.cov(np.c_[xs, ys].T); w, v = np.linalg.eigh(cov)
        major = v[:, 1]; ang = float(np.degrees(np.arctan2(-major[1], major[0])))
        proj = (np.c_[xs, ys] - c) @ major; projm = (np.c_[xs, ys] - c) @ v[:, 0]
        items.append(dict(x=round(float(c[0]), 1), y=round(float(c[1]), 1), length=round(float(proj.max() - proj.min()) + 2 * erode, 1),
                          width=round(float(projm.max() - projm.min()) + 2 * erode, 1), angle=round(ang, 1), area=int(len(xs))))
    out[name] = sorted(items, key=lambda d: (d['y'], d['x']))
json.dump(out, open('trace/parts.json', 'w'), indent=1)
d = ImageDraw.Draw(im)
for name, col in (('leaves', (255, 0, 255)), ('cream', (0, 255, 255))):
    for k, it in enumerate(out[name]):
        t = np.radians(it['angle']); dx, dy = np.cos(t) * it['length'] / 2, -np.sin(t) * it['length'] / 2
        d.line([(it['x'] - dx, it['y'] - dy), (it['x'] + dx, it['y'] + dy)], fill=col, width=3)
        d.text((it['x'] + 4, it['y'] + 4), f"{name[0]}{k}", fill=(255, 255, 0))
im.resize((900, 900)).save('trace/parts_overlay.png')
print({k: len(v) for k, v in out.items()})
for it in out['cream']: print('cream', it)
