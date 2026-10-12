import sys; sys.path.insert(0, "/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/diamond/gem_shader_20261011/model")
import math, numpy as np
import try1
from explore import *
try1.ag = 3.12
def stats(star_angle, upper_angle, lower_extra):
    planes, names = try1.build(star_angle, upper_angle, lower_extra)
    V, N, D = polytope(planes); F = faces(V, N, D)
    by = {}
    for i, idx in F.items(): by.setdefault(names[i], []).append(V[idx][:, 1])
    cnt = len(F)
    star_y = min(min(y) for y in by['star']); upper_y = max(max(y) for y in by['upper']); low_y = min(min(y) for y in by['lower'])
    return cnt, star_y, upper_y, low_y
for sa in (28, 30, 32, 34):
    for ua in (48, 52, 56, 60):
        c, sy, uy, ly = stats(sa, ua, 3.0)
        print(f'star {sa} upper {ua}: faces {c} star tip y {sy:.3f} upper apex y {uy:.3f} lower tip y {ly:.3f}')
