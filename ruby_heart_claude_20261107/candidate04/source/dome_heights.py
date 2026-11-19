"""Vertex heights from one smooth dome over distance to the gem edge.

Usage: dome_heights.py OUT.json [ZG] [RISE] [POWER]
z = ZG + RISE * (d / dmax) ** POWER, d = distance from the vertex to the gem edge.
"""
import sys, json
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/tools')
import facets
names, xy, girdle, faces = facets.layout()
inner = facets.INNER
full = np.vstack([inner, inner[::-1] * [-1, 1]])
keep = np.r_[True, np.linalg.norm(np.diff(full, axis=0), axis=1) > 1e-9]
full = full[keep]
ZG = float(sys.argv[2]) if len(sys.argv) > 2 else 0.22
RISE = float(sys.argv[3]) if len(sys.argv) > 3 else 0.72
POW = float(sys.argv[4]) if len(sys.argv) > 4 else 0.55
def dist(p):
    a, b = full[:-1], full[1:]
    ab = b - a; t = np.clip(np.sum((p - a) * ab, 1) / np.sum(ab * ab, 1), 0, 1)
    return np.min(np.linalg.norm(a + ab * t[:, None] - p, axis=1))
d = {k: (0.0 if g else dist(p)) for k, p, g in zip(names, xy, girdle) if not k.endswith("'")}
dmax = max(d.values())
h = {k: (ZG if v == 0 else ZG + RISE * (v / dmax) ** POW) for k, v in d.items()}
# Make every facet exactly flat: smallest change to the dome heights such that
# each polygon's extra corners lie on the plane of its first three corners.
left = [k for k in names if not k.endswith("'")]
free = [k for k in left if not girdle[names.index(k)]]
col = {k: i for i, k in enumerate(free)}
P = {k: xy[names.index(k)] for k in left}
A, bvec = [], []
for f in facets.FACES:
    if len(f) < 4: continue
    p1, p2, p3 = (P[k] for k in f[:3])
    M = np.array([[p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]], [1, 1, 1]])
    for k4 in f[3:]:
        w = np.linalg.solve(M, [P[k4][0], P[k4][1], 1])     # affine weights of corner 4
        row = np.zeros(len(free)); rhs = 0.0
        for kk, ww in zip(list(f[:3]) + [k4], list(-w) + [1.0]):
            if kk in col: row[col[kk]] += ww
            else: rhs -= ww * h[kk]
        A.append(row); bvec.append(rhs)
A = np.array(A); bvec = np.array(bvec)
zd = np.array([h[k] for k in free])
z = zd - A.T @ np.linalg.solve(A @ A.T, A @ zd - bvec)
print('planarity changes (max |dz|):', round(float(np.abs(z - zd).max()), 3), 'residual', float(np.abs(A @ z - bvec).max()))
for k, v in zip(free, z): h[k] = float(v)
json.dump({'heights': h, 'dome': dict(ZG=ZG, RISE=RISE, POWER=POW, dmax=dmax)}, open(sys.argv[1], 'w'), indent=1)
print({k: round(v, 3) for k, v in h.items() if not k.startswith('g')}, 'dmax', round(dmax, 3))
