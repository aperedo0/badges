"""Find the dark specks before the simulator: where does one of the app's eight lights reflect straight into the
camera on a glow only (enamel) surface? The app draws a dark pixel there (surface direction = half way between the
light and the camera; proven on Golden Storm, Nov 9, 2026, matched to the pixel). Python 3.11.

Usage: light_centers.py CAND_DIR [MATERIAL,MATERIAL,...]
Reads CAND_DIR/parts.npz and parts.json from badge3d.py. Checks the materials named, else the build's glow_only list,
else every material with an emission texture in CAND_DIR/palette.json. Must print "centers: 0" before the app run;
badge3d.py gives glow_only materials a fixed direction (ENAMEL_NORMAL) that keeps this at 0 at rest.
Exit code 1 when any center is found.
"""
import sys, json
from pathlib import Path
import numpy as np

C = Path(sys.argv[1]); D = np.load(C / 'parts.npz'); META = json.load(open(C / 'parts.json'))
if len(sys.argv) > 2:
    CHECK = set(sys.argv[2].split(','))
elif META.get('glow_only'):
    CHECK = set(META['glow_only'])
else:
    pal = json.load(open(C / 'palette.json')) if (C / 'palette.json').exists() else {}
    CHECK = {k for k, v in pal.items() if isinstance(v, dict) and 'emission_texture' in v}
if not CHECK:
    sys.exit('no glow only materials named or found (pass them as MATERIAL,MATERIAL)')

# the app's studio at rest, in model units (same values Golden Storm's light_centers.py matched to the pixel)
LIGHTS = np.array([[-5.4, 3.5, 2.8], [5.393, 2.023, 3.426], [4.8, 1.8, 4.2], [4.207, 1.577, 4.974], [-0.3, 5.1, 3.5],
                   [-2.075, -2.375, 4.375], [-1.525, -1.825, 4.825], [0, 0.6, 7.5]])
NAMES = ['key', 'rim hi', 'rim mid', 'rim lo', 'top', 'low left a', 'low left b', 'front fill']
CAM = np.array([0, 1.8, 23.])
k = 10; W = np.array([(a / k, b / k, 1 - a / k - b / k) for a in range(k + 1) for b in range(k + 1 - a)])

found = []
for part in META['parts']:
    mats = part['materials']; want = [i for i, m in enumerate(mats) if m in CHECK]
    if not want:
        continue
    nf = part['front']; V = D[part['name'] + '_v'][:nf].astype(float); N = D[part['name'] + '_n'][:nf].astype(float)
    M = D[part['name'] + '_m'][:nf]; sel = np.isin(M, want)
    if not sel.any():
        continue
    V, N = V[sel], N[sel]
    P = np.einsum('sb,tbc->tsc', W, V); Nn = np.einsum('sb,tbc->tsc', W, N); Nn /= np.linalg.norm(Nn, axis=2)[..., None]
    Vw = CAM - P; Vw /= np.linalg.norm(Vw, axis=2)[..., None]
    for li, Lp in enumerate(LIGHTS):
        L = Lp - P; L /= np.linalg.norm(L, axis=2)[..., None]
        Hh = L + Vw; Hh /= np.linalg.norm(Hh, axis=2)[..., None]
        ang = np.degrees(np.arccos(np.clip((Nn * Hh).sum(2), -1, 1)))
        best = ang.min(1)
        for tr in np.nonzero(best < 0.6)[0]:
            p = P[tr, ang[tr].argmin()]
            found.append((NAMES[li], part['name'], float(best[tr]), float(p[0]), float(p[1])))

seen = []
for light, piece, a, x, y in sorted(found, key=lambda q: q[2]):
    if any(l == light and abs(x - xx) < 0.12 and abs(y - yy) < 0.12 for l, _, _, xx, yy in seen):
        continue
    seen.append((light, piece, a, x, y))
for light, piece, a, x, y in seen:
    print(f'{light:11s} reflects straight at the camera on {piece} at badge ({x:+.2f}, {y:+.2f})')
print('materials checked:', ', '.join(sorted(CHECK)), '| centers:', len(seen))
sys.exit(1 if seen else 0)
