"""Carve the stag from the mockup: its outline becomes a rounded solid, its gold ridge lines become raised ridges,
each panel between ridges bulges slightly. Colors are flat per class (gold ridges and antlers, champagne panels),
with no lighting copied from the picture.

Usage: carve_stag.py OUT.npz OUT_TEXTURE.png
Writes 'stag' vertices, normals, triangles and uv (into the texture) in model units, front and back.
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import Delaunay
from matplotlib import contour as _c
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/emerald_stag_claude_20261108/tools')
from meshkit import unit
import stag_parts as SP

ROOT = '/Users/antonioperedo/Desktop/badges/emerald_stag_claude_20261108/'
X0, Y0, X1, Y1 = 355, 60, 920, 840
im = np.asarray(Image.open(ROOT + 'reference/stag.png').convert('RGB')).astype(int)
a = im[Y0:Y1, X0:X1]; r, g, b = a[..., 0], a[..., 1], a[..., 2]; mx = a.max(2)
H, W = a.shape[:2]
cut = np.asarray(Image.open(ROOT + 'gen/stag_input.png').convert('RGB').resize((780, 780)))
oy, ox = (780 - H) // 2, (780 - W) // 2
mask = cut[oy:oy + H, ox:ox + W].max(2) > 20
mask = ndi.binary_fill_holes(ndi.binary_opening(mask, iterations=1))
lab, n = ndi.label(mask); sizes = ndi.sum(mask, lab, range(1, n + 1)); mask = lab == (1 + int(np.argmax(sizes)))
ym, xm = np.mgrid[Y0:Y1, X0:X1]

# classes: antlers solid gold; ridge lines gold; the rest champagne
antler = mask & ((ym < 262) | ((ym < 300) & (xm < 700)))
ridge = mask & ((r - b) > 105) & (mx > 110) & ((r - g) > 40)
ridge = ndi.gaussian_filter(ridge.astype(float), 1.6) > 0.42
lab_r, n_r = ndi.label(ridge); sz_r = ndi.sum(ridge, lab_r, range(1, n_r + 1))
ridge = np.isin(lab_r, 1 + np.nonzero(sz_r >= 40)[0])          # keep the long lines, drop specks
gold = antler | ridge

# height: rounded statue from the outline, scaled to the local half width
dist = ndi.distance_transform_edt(mask)
R = ndi.maximum_filter(dist, size=61)
R = np.maximum(R, 1.0)
dd = np.clip(dist, 0, R)
z_base = np.sqrt(np.maximum(dd * (2 * R - dd), 0)) * 0.78
# panels bulge between ridges; ridges stand up as crests (body only, not antlers)
d_ridge = ndi.distance_transform_edt(~ridge)
panel = (1 - np.exp(-d_ridge / 9.0)) * 2.2
crest = ndi.gaussian_filter(ridge.astype(float), 1.8) * 2.2
body = mask & ~antler
z_px = z_base + np.where(body, panel + crest, 0.0)
z_px = ndi.gaussian_filter(z_px, 1.8) * mask
S = SP.S
Z = z_px * S                               # model units

# texture: flat colors, antialiased edges, padded outward so mipmaps never bleed black
tex_scale = 2
champ = np.array([182, 138, 80]); goldc = np.array([196, 104, 22])
gsoft = ndi.gaussian_filter(gold.astype(float), 1.0)
col = champ[None, None] * (1 - gsoft[..., None]) + goldc[None, None] * gsoft[..., None]
idx = ndi.distance_transform_edt(~mask, return_distances=False, return_indices=True)
col = col[idx[0], idx[1]]
Image.fromarray(np.uint8(col)).resize((W * tex_scale, H * tex_scale), Image.LANCZOS).save(sys.argv[2])

# triangulate: grid points inside plus a smooth outline
step = 3
gy, gx = np.mgrid[1:H - 1:step, 1:W - 1:step]
inside = ndi.binary_erosion(mask, iterations=2)[gy, gx]
pts = np.c_[gx[inside], gy[inside]].astype(float)
cs = plt.contour(mask.astype(float), levels=[0.5]); segs = cs.allsegs[0]; plt.close('all')
outline = max(segs, key=len)
d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(outline, axis=0), axis=1))]
t = np.arange(0, d[-1], 2.2)
outline = np.c_[np.interp(t, d, outline[:, 0]), np.interp(t, d, outline[:, 1])]
allp = np.vstack([pts, outline])
tri = Delaunay(allp)
cent = allp[tri.simplices].mean(1)
keep = mask[np.clip(cent[:, 1].round().astype(int), 0, H - 1), np.clip(cent[:, 0].round().astype(int), 0, W - 1)]
T = tri.simplices[keep]
# drop slivers spanning gaps between legs or antler tines
e = allp[T]; longest = np.max(np.linalg.norm(e - np.roll(e, 1, axis=1), axis=2), axis=1)
T = T[longest < 7.5]
nb = len(outline); is_edge = np.r_[np.zeros(len(pts), bool), np.ones(nb, bool)]
zf = ndi.map_coordinates(Z, [allp[:, 1], allp[:, 0]], order=1)
zf[is_edge] = 0.0
XY = np.array([SP.P(x + X0, y + Y0) for x, y in allp])
V_front = np.c_[XY, zf]
UV = np.c_[allp[:, 0] / W, 1 - allp[:, 1] / H]


def normals(V, T):
    N = np.zeros_like(V)
    fn = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    for k in range(3):
        np.add.at(N, T[:, k], fn)
    return unit(N)


Tf = T.copy()
fn = np.cross(V_front[Tf[:, 1]] - V_front[Tf[:, 0]], V_front[Tf[:, 2]] - V_front[Tf[:, 0]])
Tf[fn[:, 2] < 0] = Tf[fn[:, 2] < 0][:, ::-1]
N_front = normals(V_front, Tf)
# at the outline the surface turns sideways: blend edge normals toward the in plane outward direction
V_back = V_front * [1, 1, -1]; Tb = Tf[:, ::-1]
N_back = normals(V_back, Tb)
n = len(V_front)
V = np.vstack([V_front, V_back]); N = np.vstack([N_front, N_back]); UVs = np.vstack([UV, UV])
TT = np.vstack([Tf, Tb + n])
# weld the outline: back edge vertices reuse the front ones, with a shared sideways normal
edge_idx = np.nonzero(is_edge)[0]
side_n = unit(N_front[edge_idx] * [1, 1, 0] + 1e-9)
N[edge_idx] = side_n
remap = np.arange(len(V)); remap[edge_idx + n] = edge_idx
TT = remap[TT]
np.savez(sys.argv[1], stag_v=V, stag_n=N, stag_t=TT, stag_uv=UVs)
print('carved stag: vertices', len(V), 'triangles', len(TT), 'max depth', round(float(Z.max()), 3),
      'x', XY[:, 0].min().round(2), XY[:, 0].max().round(2), 'y', XY[:, 1].min().round(2), XY[:, 1].max().round(2))
