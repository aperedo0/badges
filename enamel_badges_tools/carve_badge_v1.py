"""Carve an enamel badge from its mockup: raised rounded gold walls and rim, glossy pillowed enamel cells,
an optional faceted gem cell, front and mirrored back joined at a rounded outline edge.

Usage: carve_badge.py BADGE_DIR OUT.npz [--gem X,Y]
Reads BADGE_DIR/reference/mockup.png, BADGE_DIR/trace/seg.npz, BADGE_DIR/review.json (mockup_box).
Writes OUT.npz (badge_v, badge_n, badge_t, badge_uv; gem_* if a gem cell is given) and textures in BADGE_DIR/textures.
Colors are flat per pixel from the mockup with its highlights filtered out; gold is one flat color.
"""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import Delaunay
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

D = Path(sys.argv[1]); OUT = sys.argv[2]
gem_xy = None
if '--gem' in sys.argv:
    gem_xy = tuple(int(v) for v in sys.argv[sys.argv.index('--gem') + 1].split(','))
cfg = json.loads((D / 'review.json').read_text())
cx_px, top_px, bot_px = cfg['mockup_box']
img = np.asarray(Image.open(D / 'reference/mockup.png').convert('RGB')).astype(float) / 255
seg = np.load(D / 'trace/seg.npz'); gold, enamel, mask = seg['gold'], seg['enamel'], seg['mask']
H, W = mask.shape
S = 5.45 / (bot_px - top_px)                       # model units per pixel

# clean gold: drop small isolated specks inside enamel (highlights), keep the wall network
lab, n = ndi.label(gold); sz = ndi.sum(gold, lab, range(1, n + 1))
gold = np.isin(lab, 1 + np.nonzero(sz >= 400)[0])
enamel = mask & ~gold

gem = np.zeros_like(mask)
if gem_xy:
    lab_e, _ = ndi.label(enamel)
    gid = lab_e[gem_xy[1], gem_xy[0]]
    if gid:
        gem = lab_e == gid
        enamel &= ~gem

# ---------------- height field (pixels) ----------------
d_out = ndi.distance_transform_edt(mask)
d_gold = ndi.distance_transform_edt(~gold)          # enamel: distance to nearest wall
d_in_gold = ndi.distance_transform_edt(gold)        # gold: distance to its own edge
E0, DOME, WALL, RIM_W = 34.0, 7.0, 13.0, 9.0
z = np.zeros((H, W))
z_en = E0 + DOME * (1 - np.exp(-d_gold / 14.0))
z_gold = E0 + WALL * np.sqrt(np.clip(d_in_gold / 5.0, 0, 1)) + 2.0 * np.clip((d_in_gold - 5) / 10, 0, 1)
z = np.where(gold, z_gold, z_en)
if gem.any():
    d_gem = ndi.distance_transform_edt(gem)
    z = np.where(gem, E0 + 4 + 0.75 * d_gem, z)    # a faceted pyramid: planes meeting along the star's skeleton
# rounded outline edge
edge = np.sqrt(np.clip(1 - (1 - np.clip(d_out / RIM_W, 0, 1)) ** 2, 0, 1))
z = z * edge
z = ndi.gaussian_filter(z, 0.9) * mask
Z = z * S

# ---------------- textures (flat colors, no light copied) ----------------
TEX = 1024
fill_idx = ndi.distance_transform_edt(~(enamel | gem), return_distances=False, return_indices=True)
base = img[fill_idx[0], fill_idx[1]]               # enamel colors spread under the walls
den = np.stack([ndi.median_filter(base[..., k], size=17) for k in range(3)], -1)   # thin highlights removed
# pull bright glare toward the local cell color, keep hue
lum = den @ np.array([0.299, 0.587, 0.114])
lum_local = ndi.median_filter(lum, size=41)
scale = np.clip(np.minimum(lum, lum_local * 1.12 + 0.02) / np.maximum(lum, 1e-4), 0.55, 1.0)
den = den * scale[..., None]
gold_rgb = np.array([246, 190, 95]) / 255.0
col = np.where(gold[..., None], gold_rgb, den)
metal = np.where(gold, 1.0, 0.0)
rough = np.where(gold, 0.28, np.where(gem, 0.06, 0.14))
pad = ndi.distance_transform_edt(~mask, return_distances=False, return_indices=True)
col, metal, rough = col[pad[0], pad[1]], metal[pad[0], pad[1]], rough[pad[0], pad[1]]
tw, th = TEX, int(round(TEX * H / W))
Image.fromarray(np.uint8(np.clip(col, 0, 1) * 255)).resize((tw, th), Image.LANCZOS).save(D / 'textures/badge_color.png')
Image.fromarray(np.uint8(metal * 255)).resize((tw, th), Image.BILINEAR).save(D / 'textures/badge_metal.png')
Image.fromarray(np.uint8(rough * 255)).resize((tw, th), Image.BILINEAR).save(D / 'textures/badge_rough.png')

# ---------------- adaptive triangulation ----------------
gz = np.hypot(*np.gradient(z))
busy = ndi.binary_dilation((gz > 0.6) | (d_out < 6), iterations=3)
pts = []
for step, region in ((4, busy), (12, ~busy)):
    yy, xx = np.mgrid[2:H - 2:step, 2:W - 2:step]
    sel = region[yy, xx] & ndi.binary_erosion(mask, iterations=2)[yy, xx]
    pts.append(np.c_[xx[sel], yy[sel]])
pts = np.vstack(pts).astype(float)
cs = plt.contour(mask.astype(float), levels=[0.5]); outline = max(cs.allsegs[0], key=len); plt.close('all')
dd = np.r_[0, np.cumsum(np.linalg.norm(np.diff(outline, axis=0), axis=1))]
t = np.arange(0, dd[-1], 3.0)
outline = np.c_[np.interp(t, dd, outline[:, 0]), np.interp(t, dd, outline[:, 1])]
allp = np.vstack([pts, outline]); nb = len(outline)
tri = Delaunay(allp)
cent = allp[tri.simplices].mean(1)
keep = mask[np.clip(cent[:, 1].round().astype(int), 0, H - 1), np.clip(cent[:, 0].round().astype(int), 0, W - 1)]
T = tri.simplices[keep]
e = allp[T]; longest = np.max(np.linalg.norm(e - np.roll(e, 1, axis=1), axis=2), axis=1)
T = T[longest < 26]
is_edge = np.r_[np.zeros(len(pts), bool), np.ones(nb, bool)]
zf = ndi.map_coordinates(Z, [allp[:, 1], allp[:, 0]], order=1); zf[is_edge] = 0.0
X = (allp[:, 0] - cx_px) * S; Yc = 2.995 - (allp[:, 1] - top_px) * S
Vf = np.c_[X, Yc, zf]
UV = np.c_[allp[:, 0] / W, 1 - allp[:, 1] / H]


def unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12)


def normals(V, T):
    N = np.zeros_like(V); fn = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    for k in range(3): np.add.at(N, T[:, k], fn)
    return unit(N)


fn = np.cross(Vf[T[:, 1]] - Vf[T[:, 0]], Vf[T[:, 2]] - Vf[T[:, 0]])
T[fn[:, 2] < 0] = T[fn[:, 2] < 0][:, ::-1]
Nf = normals(Vf, T)
n = len(Vf)
Vb = Vf * [1, 1, -1]; Tb = T[:, ::-1] + n
V = np.vstack([Vf, Vb]); N = np.vstack([Nf, Nf * [1, 1, -1]]); UVs = np.vstack([UV, UV]); TT = np.vstack([T, Tb])
eidx = np.nonzero(is_edge)[0]
N[eidx] = unit(Nf[eidx] * [1, 1, 0] + 1e-9)
remap = np.arange(len(V)); remap[eidx + n] = eidx; TT = remap[TT]
# split the gem triangles into their own mesh (glossy stone material)
data = {}
if gem.any():
    cx_t = (V[TT].mean(1)); px = cx_t[:, 0] / S + cx_px; py = (2.995 - cx_t[:, 1]) / S + top_px
    in_gem = gem[np.clip(py.round().astype(int), 0, H - 1), np.clip(px.round().astype(int), 0, W - 1)] & (np.abs(cx_t[:, 2]) > (E0 + 2) * S * 0.9)
    gT = TT[in_gem]; TT = TT[~in_gem]
    used = np.unique(gT); m = -np.ones(len(V), int); m[used] = np.arange(len(used))
    gV = V[used]; gN_ = normals(gV, m[gT])
    data.update(gem_v=gV, gem_n=gN_, gem_t=m[gT], gem_uv=UVs[used])
data.update(badge_v=V, badge_n=N, badge_t=TT, badge_uv=UVs)
np.savez(OUT, **data)
allv = np.vstack([data[k] for k in data if k.endswith('_v')])
print('triangles', sum(len(data[k]) for k in data if k.endswith('_t')), {k[:-2]: len(data[k]) for k in data if k.endswith('_t')},
      'bounds', allv.min(0).round(3), allv.max(0).round(3))
