"""Textures: black marble with kintsugi gold seams (color and metallic mask), and glittery cobalt sand."""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
N = 2048
def fbm(n, base, seed, octaves=5):
    r = np.random.default_rng(seed); out = np.zeros((n, n))
    for o in range(octaves):
        f = base * 2 ** o; g = r.standard_normal((f, f)); g = np.pad(g, 2, mode='wrap')
        up = ndi.zoom(g, (n + 4 * n / f) / (f + 4), order=3); s0 = int(2 * n / f)
        out += up[s0:s0 + n, s0:s0 + n] / 2 ** o
    return out / np.abs(out).max()
# marble: near black with soft charcoal clouding
cloud = np.clip(0.5 + 0.5 * fbm(N, 3, 2), 0, 1) ** 1.4
col = np.array([10, 10, 12]) / 255.0 + np.array([48, 48, 52]) / 255.0 * (cloud[..., None] ** 2.4)
# kintsugi seams: jagged branching cracks, tileable left to right
rng = np.random.default_rng(21)
mask = Image.new('L', (N, N), 0); d = ImageDraw.Draw(mask)
for k in range(6):
    p = np.array([rng.uniform(0, N), rng.uniform(0.25 * N, 0.75 * N)]); ang = rng.uniform(-0.45, 0.45) + (0 if k % 2 else np.pi)
    pts = [tuple(p)]
    for step in range(rng.integers(9, 15)):
        ang += rng.normal(0, 0.45); p = p + 95 * np.array([np.cos(ang), np.sin(ang)]); pts.append(tuple(p))
        if rng.random() < 0.4:
            b = p.copy(); ba = ang + rng.choice([-1, 1]) * rng.uniform(0.6, 1.2); bp = [tuple(b)]
            for _ in range(rng.integers(2, 4)):
                ba += rng.normal(0, 0.4); b = b + 70 * np.array([np.cos(ba), np.sin(ba)]); bp.append(tuple(b))
            for dx in (-N, 0, N):
                d.line([(x + dx, y) for x, y in bp], fill=255, width=7)
    for dx in (-N, 0, N):
        d.line([(x + dx, y) for x, y in pts], fill=255, width=12)
seam = ndi.gaussian_filter(np.asarray(mask, float) / 255, 1.0)
gold = np.array([226, 160, 62]) / 255.0
col = col * (1 - seam[..., None]) + gold * seam[..., None]
Image.fromarray(np.uint8(np.clip(col, 0, 1) * 255)).save('textures/marble_black.png')
Image.fromarray(np.uint8(np.clip(seam * 1.2, 0, 1) * 255)).save('textures/marble_metal.png')
# sand: deep cobalt, fine tonal grain, sparse glitter grains that are metallic and smooth
M = 512
r = np.random.default_rng(9)
tone = ndi.gaussian_filter(r.standard_normal((M, M)), 0.7, mode='wrap')
tone = (tone - tone.mean()) / tone.std()
base = np.array([6, 42, 178]) / 255.0
sand = base[None, None] * (1 + 0.07 * tone[..., None])
glit = np.zeros((M, M))
for _ in range(2200):
    x, y = r.integers(0, M, 2); rad = r.uniform(0.7, 1.2)
    yy, xx = np.ogrid[-3:4, -3:4]
    spot = np.exp(-(xx ** 2 + yy ** 2) / (rad ** 2))
    ys, xs = (np.arange(-3, 4) + y) % M, (np.arange(-3, 4) + x) % M
    glit[np.ix_(ys, xs)] = np.maximum(glit[np.ix_(ys, xs)], spot)
sparkle = np.array([175, 212, 255]) / 255.0
sand = sand * (1 - glit[..., None]) + sparkle * glit[..., None]
Image.fromarray(np.uint8(np.clip(sand, 0, 1) * 255)).save('textures/sand_color.png')
Image.fromarray(np.uint8(np.clip(glit, 0, 1) * 255)).save('textures/sand_metal.png')
Image.fromarray(np.uint8(np.clip(0.78 - 0.6 * glit, 0, 1) * 255)).save('textures/sand_rough.png')
print('seam share', round(float((seam > 0.3).mean()), 3), 'glitter share', round(float((glit > 0.3).mean()), 3))
