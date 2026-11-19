"""Where does each of the app's eight lights reflect straight into the camera? (the surface direction equals the
half way direction between light and camera). The app draws a dead pixel at exactly those points.
Usage: light_centers.py candidateNN [piece name fragment]"""
import sys, json
import numpy as np
C = sys.argv[1]; frag = sys.argv[2] if len(sys.argv) > 2 else 'Pearl'
D = np.load(C + '/geometry.npz'); meta = json.load(open(C + '/parts.json')); S = meta['units_per_pixel']; CX = meta['center_x']; TOP = meta['top']
bmin, bmax = meta['bounds_min'], meta['bounds_max']
LIGHTS = np.array([[-5.4, 3.5, 2.8], [5.393, 2.023, 3.426], [4.8, 1.8, 4.2], [4.207, 1.577, 4.974], [-0.3, 5.1, 3.5], [-2.075, -2.375, 4.375], [-1.525, -1.825, 4.825], [0, 0.6, 7.5]])
NAMES = ['key', 'rim hi', 'rim mid', 'rim lo', 'top', 'low left a', 'low left b', 'front fill']
CAM = np.array([0, 1.8, 23.])
X0, PPU, Y0 = 394, 76.9, 358       # the badge on the simulator screen (left edge, pixels per unit, top)
found = []
for i, part in enumerate(meta['parts']):
    if frag not in part['name'] or 'side walls' in part['name']:
        continue
    v = D[f'{i}_v'].astype(float); n = D[f'{i}_n'].astype(float); t = D[f'{i}_t']
    t = t[(v[t][:, :, 2] > 0).all(1)]
    # sample every triangle on a fine barycentric grid
    k = 14; bb = [(a / k, b / k, 1 - a / k - b / k) for a in range(k + 1) for b in range(k + 1 - a)]
    W = np.array(bb)
    P = np.einsum('sb,tbc->tsc', W, v[t]); N = np.einsum('sb,tbc->tsc', W, n[t]); N /= np.linalg.norm(N, axis=2)[..., None]
    V = CAM - P; V /= np.linalg.norm(V, axis=2)[..., None]
    for li, Lp in enumerate(LIGHTS):
        L = Lp - P; L /= np.linalg.norm(L, axis=2)[..., None]
        Hh = L + V; Hh /= np.linalg.norm(Hh, axis=2)[..., None]
        ang = np.degrees(np.arccos(np.clip((N * Hh).sum(2), -1, 1)))
        tri, smp = np.unravel_index(ang.argmin(), ang.shape)
        best = ang.min(1)
        for tr in np.nonzero(best < .6)[0]:
            p = P[tr, ang[tr].argmin()]
            found.append((NAMES[li], round(float(best[tr]), 2), float(p[0]), float(p[1])))
# merge neighbours
seen = []
for name, a, x, y in sorted(found, key=lambda q: q[1]):
    if any(nm == name and abs(x - xx) < .12 and abs(y - yy) < .12 for nm, _, xx, yy in seen):
        continue
    seen.append((name, a, x, y))
for name, a, x, y in seen:
    sx = X0 + (x - bmin[0]) * PPU; sy = Y0 + (bmax[1] - y) * PPU
    print(f'{name:11s} reflects straight at the camera at badge ({x:+.2f}, {y:+.2f})  about screen ({sx:.0f}, {sy:.0f})')
print('centers on', frag, ':', len(seen))
