"""Add raised polished gold ridge lines on the stag's near and far sides, following its surface.

Usage: add_ridges.py GEOM.npz OUT.npz
"""
import sys
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/emerald_stag_claude_20261108/tools')
from meshkit import merge, orient
import stag_parts as SP

d = dict(np.load(sys.argv[1]))
lift = -2.455 - min(d[k][:, 1].min() for k in d if k.endswith('_v'))  # already lifted: 0
V = d['stag_v']
RIDGES = [  # mockup pixels along the stag's flowing panel lines
    [(808, 300), (788, 338), (772, 388), (760, 438), (745, 472)],
    [(822, 302), (814, 350), (810, 400), (814, 448), (824, 480)],
    [(795, 292), (770, 322), (748, 362), (737, 410), (728, 452)],
    [(745, 470), (760, 508), (770, 548), (765, 582)],
    [(735, 470), (680, 488), (620, 503), (562, 528), (522, 548)],
    [(760, 560), (700, 574), (640, 580), (592, 586)],
    [(604, 530), (574, 560), (562, 600), (576, 630)],
    [(822, 272), (846, 268), (872, 268)],
    [(814, 300), (842, 296), (872, 290)],
    [(700, 520), (690, 560), (676, 596)],
    [(650, 535), (640, 570), (630, 600)],
    [(780, 330), (792, 380), (790, 430)],
]
ref_lift = np.load(sys.argv[1].replace('geometry.npz', 'geometry.npz'))  # same file; kept for clarity
dy = d['stag_v'][:, 1].min()  # not used
tubes = []
# the exported model was lifted so its lowest point is at -2.455; recover that shift from the base point
shift = d['marble_v'][:, 1].min() - SP.P(625, 1195)[1] if 'marble_v' in d else 0.0
import os
for ridge in ([] if os.environ.get('CARVED') else RIDGES):
    for side in (1, -1):
        pts = []
        for (x, y) in np.array(ridge, float):
            q = SP.P(x, y) + [0, shift]
            near = V[np.linalg.norm(V[:, :2] - q, axis=1) < 0.035]
            if len(near) < 3: continue
            z = near[:, 2].max() if side > 0 else near[:, 2].min()
            pts.append(np.r_[q, z + side * 0.006])
        if len(pts) >= 2:
            tubes.append(SP.tube(np.array(pts), SP.PX(4.6), sides=8, taper=(0.6, 1.0)))
r = orient(merge(tubes))
g = 'gold'
off = len(d[g + '_v'])
d[g + '_v'] = np.vstack([d[g + '_v'], r.V]); d[g + '_n'] = np.vstack([d[g + '_n'], r.N]); d[g + '_t'] = np.vstack([d[g + '_t'], r.T + off])
np.savez(sys.argv[2], **d)
print('ridges', len(tubes), 'triangles added', len(r.T), 'shift', round(float(shift), 4))

# final fit: keep the lowest point at -2.455 and the top at or under 3.0 (app limit 3.015), uniform scale
d = dict(np.load(sys.argv[2]))
vs = [k for k in d if k.endswith('_v')]
lo = min(d[k][:, 1].min() for k in vs); hi = max(d[k][:, 1].max() for k in vs)
s = min(1.0, (3.0 + 2.455) / (hi - lo))
for k in vs:
    v = d[k].copy(); v[:, 1] -= lo; v *= s; v[:, 1] += -2.455; d[k] = v
np.savez(sys.argv[2], **d)
allv = np.vstack([d[k] for k in vs])
print('fit scale', round(float(s), 4), 'bounds', allv.min(0).round(3).tolist(), allv.max(0).round(3).tolist())
