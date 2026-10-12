"""Adds a soft, continuous ring of light to the badge studio environment map (equirectangular, image center = the
direction toward the camera, +Z). The ring sits between inner and outer angles from that direction, with smooth
edges; every existing light panel keeps its value (max of panel and ring). Usage:
  /usr/local/bin/python3 make_ring_env.py <env.npy> <ring_luminance> <inner_deg> <outer_deg> <out.npy>"""
import sys
import numpy as np
src, lum, a0, a1, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
env = np.load(src).astype(np.float64)
h, w, _ = env.shape
v, u = np.mgrid[0:h, 0:w]
lon = (u + 0.5) / w * 2 * np.pi - np.pi
lat = np.pi / 2 - (v + 0.5) / h * np.pi
z = np.cos(lat) * np.cos(lon)
ang = np.degrees(np.arccos(np.clip(z, -1, 1)))
def smooth(x):
    x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
edge = 8.0
ring = smooth((ang - (a0 - edge)) / edge) * (1 - smooth((ang - a1) / edge))
tint = np.array([1.0, 0.99, 0.97]); tint = tint / (tint @ np.array([0.2126, 0.7152, 0.0722]))
new = np.maximum(env, (lum * ring)[..., None] * tint[None, None, :])
np.save(out, new.astype(np.float32))
L = new @ np.array([0.2126, 0.7152, 0.0722])
for lo, hi in ((10, 30), (30, 50), (50, 70)):
    m = (ang >= lo) & (ang < hi); print(f'{lo}-{hi} deg: mean {L[m].mean():.3f} lit {(L[m] > 0.1).mean():.2f}')
