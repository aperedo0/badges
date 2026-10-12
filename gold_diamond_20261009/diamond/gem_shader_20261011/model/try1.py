import sys; sys.path.insert(0, "/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/diamond/gem_shader_20261011/model")
import sys, math, numpy as np
from explore import *
Yt = 2.349; Rtv = 1.40; at = Rtv * math.cos(math.radians(22.5)); ag = 3.12 * math.cos(math.pi / 32)
Ytop, Ybot, Yc = 0.88, 0.78, -2.455
def build(star_angle=25.0, upper_angle=50.0, lower_extra=3.0):
    planes = []; names = []
    planes.append((np.array([0, 1.0, 0]), Yt)); names.append('table')
    tb = math.degrees(math.atan2(1.0, (Yt - Ytop) / (ag - Rtv)))
    # bezel
    for k in range(8):
        planes.append(plane(45 * k, tb, ag, Ytop)); names.append('bezel')
    # recompute bezel offset through the table vertex too (rho = Rtv at Yt)
    for k in range(8):
        planes.append(plane(22.5 + 45 * k, 90 - star_angle, at, Yt)); names.append('star')
    for k in range(16):
        planes.append(plane(11.25 + 22.5 * k, 90 - upper_angle, ag, Ytop)); names.append('upper')
    for m in range(32):
        planes.append(plane(11.25 * m, 0.0, ag, 0.0)); names.append('wall')
    bm = math.degrees(math.atan2(Ybot - Yc, ag))
    for k in range(8):
        planes.append(plane(45 * k, -(90 - bm), ag, Ybot)); names.append('main')
    for k in range(16):
        planes.append(plane(11.25 + 22.5 * k, -(90 - (bm + lower_extra)), ag, Ybot)); names.append('lower')
    return planes, names
if __name__ == '__main__':
    planes, names = build()
    V, N, D = polytope(planes)
    F = faces(V, N, D)
    from collections import Counter
    c = Counter(names[i] for i in F)
    print(len(V), 'verts', len(F), 'faces', dict(c))
    print('y range', V[:, 1].min(), V[:, 1].max(), 'x', V[:,0].min(), V[:,0].max(), 'z', V[:,2].min(), V[:,2].max())
