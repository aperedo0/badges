"""Marble (dark forest teal clouds, lightning gold cracks), lighter top marble, crack metal mask, and moss."""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
rng = np.random.default_rng(3); N = 1024
def fbm(octaves, base, seed):
    r = np.random.default_rng(seed); out = np.zeros((N, N))
    for o in range(octaves):
        f = base * 2 ** o
        g = r.standard_normal((f, f)); g = np.pad(g, 2, mode='wrap')
        up = ndi.zoom(g, (N + 4 * N / f) / (f + 4), order=3)
        s0 = int(2 * N / f); out += up[s0:s0 + N, s0:s0 + N] / 2 ** o
    return out / np.abs(out).max()
cloud = np.clip(0.5 + 0.5 * fbm(5, 4, 1), 0, 1) ** 1.6
base = np.array([10, 30, 26]) / 255.0; pale = np.array([62, 92, 80]) / 255.0
col = base * (1 - cloud[..., None] * 0.8) + pale * cloud[..., None] * 0.8
# lightning cracks: jagged polylines with branches, about 8 px wide
mask = Image.new('L', (N, N), 0); d = ImageDraw.Draw(mask)
for k in range(9):
    p = rng.uniform(0, N, 2); ang = rng.uniform(0, 2 * np.pi); pts = [tuple(p)]
    for step in range(rng.integers(6, 11)):
        ang += rng.normal(0, 0.55); p = p + 55 * np.array([np.cos(ang), np.sin(ang)]); pts.append(tuple(p))
        if rng.random() < 0.3:
            b = p.copy(); ba = ang + rng.choice([-1, 1]) * rng.uniform(0.6, 1.1); bp = [tuple(b)]
            for _ in range(rng.integers(2, 4)):
                ba += rng.normal(0, 0.4); b = b + 40 * np.array([np.cos(ba), np.sin(ba)]); bp.append(tuple(b))
            for dx in (-N, 0, N):
                for dy in (-N, 0, N):
                    d.line([(x + dx, y + dy) for x, y in bp], fill=255, width=6)
    for dx in (-N, 0, N):
        for dy in (-N, 0, N):
            d.line([(x + dx, y + dy) for x, y in pts], fill=255, width=8)
crack = np.asarray(mask) > 127
gold = np.array([235, 165, 70]) / 255.0
col[crack] = gold
Image.fromarray(np.uint8(np.clip(col, 0, 1) * 255)).save('textures/marble.png')
top = np.clip(col * 1.8 + 0.03, 0, 1); top[crack] = gold
Image.fromarray(np.uint8(top * 255)).save('textures/marble_top.png')
Image.fromarray(np.uint8(crack * 255)).save('textures/marble_metal.png')
# moss: olive velvet with yellow green tufts (about 30 to 50 px) and dark gaps
tuft = fbm(3, 8, 5)
m = np.array([52, 62, 10]) / 255.0; hi = np.array([128, 140, 34]) / 255.0; dark = np.array([20, 26, 5]) / 255.0
t = np.clip((tuft - 0.15) / 0.5, 0, 1)[..., None]; g = np.clip((-tuft - 0.25) / 0.4, 0, 1)[..., None]
moss = m * (1 - t) + hi * t; moss = moss * (1 - g) + dark * g
Image.fromarray(np.uint8(np.clip(moss, 0, 1) * 255)).save('textures/moss.png')
print('cracks share', round(float(crack.mean()), 3))
