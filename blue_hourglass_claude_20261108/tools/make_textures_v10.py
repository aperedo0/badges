"""Black marble with white and grey veins, seamless left to right (1024 x 1024, sRGB)."""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
rng = np.random.default_rng(4); N = 2048
def fbm(base, seed, octaves=5):
    r = np.random.default_rng(seed); out = np.zeros((N, N))
    for o in range(octaves):
        f = base * 2 ** o; g = r.standard_normal((f, f)); g = np.pad(g, 2, mode='wrap')
        up = ndi.zoom(g, (N + 4 * N / f) / (f + 4), order=3); s0 = int(2 * N / f)
        out += up[s0:s0 + N, s0:s0 + N] / 2 ** o
    return out / np.abs(out).max()
cloud = np.clip(0.5 + 0.5 * fbm(3, 2), 0, 1) ** 1.3
col = np.array([14, 14, 17]) / 255.0 + np.array([62, 62, 66]) / 255.0 * (cloud[..., None] ** 2.2)
mask = Image.new('L', (N, N), 0); d = ImageDraw.Draw(mask)
for k in range(9):
    p = rng.uniform(0, N, 2); p[1] = rng.uniform(0.2 * N, 0.8 * N); ang = rng.uniform(-0.5, 0.5) + (0 if k % 2 else np.pi); pts = [tuple(p)]
    for step in range(rng.integers(8, 14)):
        ang += rng.normal(0, 0.3); p = p + 120 * np.array([np.cos(ang), np.sin(ang)]); pts.append(tuple(p))
        if rng.random() < 0.35:
            b = p.copy(); ba = ang + rng.choice([-1, 1]) * rng.uniform(0.5, 1.0); bp = [tuple(b)]
            for _ in range(rng.integers(2, 4)):
                ba += rng.normal(0, 0.3); b = b + 90 * np.array([np.cos(ba), np.sin(ba)]); bp.append(tuple(b))
            for dx in (-N, 0, N):
                d.line([(x + dx, y) for x, y in bp], fill=110, width=2)
    for dx in (-N, 0, N):
        d.line([(x + dx, y) for x, y in pts], fill=(255 if k < 3 else 140), width=(4 if k < 3 else 2))
v = ndi.gaussian_filter(np.asarray(mask, float) / 255, 0.6)
vein = np.array([200, 200, 205]) / 255.0
col = col * (1 - v[..., None]) + vein * v[..., None]
Image.fromarray(np.uint8(np.clip(col, 0, 1) * 255)).save('textures/marble_black.png')
# sand: tonal grain in blobs about 12 px at 512 (about 0.05 units), no single pixel speckle
g = ndi.zoom(np.random.default_rng(9).standard_normal((96, 96)), 512 / 96, order=3)[:512, :512]
g = (g - g.mean()) / g.std()
sand = np.clip(np.array([28, 70, 220])[None, None] * (1 + 0.06 * g[..., None]), 0, 255)
Image.fromarray(np.uint8(sand)).save('textures/sand_grain.png')
print('vein share', round(float((v > 0.3).mean()), 3))
