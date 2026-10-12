import sys; sys.path.insert(0, "/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/diamond/gem_shader_20261011/model")
import math, numpy as np
import try1
from try1 import *
from explore import *
try1.ag = 3.12
def report(star_angle=25.0, upper_angle=50.0, lower_extra=3.0):
    planes, names = try1.build(star_angle, upper_angle, lower_extra)
    V, N, D = polytope(planes); F = faces(V, N, D)
    print('faces', len(F), 'verts', len(V))
    fam = {}
    for i, idx in F.items():
        P = V[idx]; c = P.mean(0)
        # area via sorted polygon
        e1 = np.cross(N[i], [0, 1, 0]) if abs(N[i][1]) < .99 else np.array([1.0, 0.0, 0.0]); e1 /= np.linalg.norm(e1); e2 = np.cross(N[i], e1)
        ang = np.arctan2((P - c) @ e2, (P - c) @ e1); order = np.argsort(ang); Q = P[order]
        area = 0.5 * np.linalg.norm(sum(np.cross(Q[j], Q[(j + 1) % len(Q)]) for j in range(len(Q))))
        fam.setdefault(names[i], []).append((area, len(idx), P[:, 1].min(), P[:, 1].max()))
    for k, v in fam.items():
        a = np.array(v); print(f'{k:6s} n={len(v):2d} area min {a[:,0].min():.4f} max {a[:,0].max():.4f} verts {sorted(set(a[:,1].astype(int)))} ymin {a[:,2].min():.3f} ymax {a[:,3].max():.3f}')
report()
