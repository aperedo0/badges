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
def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r
gold = ndi.binary_closing(gold, structure=disk(3)) & mask      # v7: close short breaks where a highlight cut a wall
lab, n = ndi.label(gold); sz = ndi.sum(gold, lab, range(1, n + 1))
gold = np.isin(lab, 1 + np.nonzero(sz >= 400)[0])
enamel = mask & ~gold
# v7: whole cells that are really gold. (1) thin light slivers inside walls are highlight streaks on the metal;
# (2) cells colored like the gold metal (less saturated and darker than yellow enamel, with some blue in it)
# are solid gold parts such as spike points
mxc, mnc = img.max(2), img.min(2); satc = (mxc - mnc) / np.maximum(mxc, 1e-6)
dch = np.maximum(mxc - mnc, 1e-6); r_, g_, b_ = img[..., 0], img[..., 1], img[..., 2]
huec = np.where(mxc == r_, ((g_ - b_) / dch) % 6, np.where(mxc == g_, (b_ - r_) / dch + 2, (r_ - g_) / dch + 4)) * 60
lumc = img @ np.array([0.299, 0.587, 0.114])
# v7: wide champagne ivory areas (a phoenix body) are enamel, never gold, even where their shading looks warm;
# near white (saturation under 0.12) is left alone: on gold it is a highlight, and white clouds are already enamel
pale = ndi.binary_closing((satc > 0.12) & (satc < 0.40) & (huec > 25) & (huec < 60) & (lumc > 0.55) & mask, structure=disk(3))
pale = ndi.binary_opening(pale, structure=disk(4))
lab_p, n_p = ndi.label(pale); szp = ndi.sum(pale, lab_p, range(1, n_p + 1))
pale = ndi.binary_erosion(np.isin(lab_p, 1 + np.nonzero(szp > 1500)[0]), structure=disk(1))
gold &= ~pale
enamel = mask & ~gold
lab, n = ndi.label(enamel); ids = np.arange(1, n + 1)
dmax = ndi.maximum(ndi.distance_transform_edt(enamel), lab, ids)
med = lambda v: np.array(ndi.median(v, lab, ids))
h_m, s_m, v_m, l_m = med(huec), med(satc), med(mxc), med(lumc)
br_m = med(b_ / np.maximum(r_, 1e-3))
thin = (dmax < 5.5) & ((l_m > 0.55) | ((h_m > 25) & (h_m < 62)))
csz = np.array(ndi.sum(enamel, lab, ids))
goldcell = (csz < 8000) & (h_m > 25) & (h_m < 62) & (s_m > 0.5) & (s_m < 0.88)   # under 0.45: champagne ivory enamel & (v_m < 0.9) & (br_m > 0.12)
for i in np.nonzero(goldcell)[0]:
    print(f'cell to gold: {int((lab == i + 1).sum())} px, hue {h_m[i]:.0f} sat {s_m[i]:.2f} value {v_m[i]:.2f} blue/red {br_m[i]:.2f}')
gold |= np.isin(lab, 1 + np.nonzero(thin | goldcell)[0])
# v7: thicken walls traced thinner than about 7 px so smoothing cannot erase them
thin_g = gold & ~ndi.binary_opening(gold, structure=disk(3))
gold |= ndi.binary_dilation(thin_g, structure=disk(2)) & mask
# v7: smooth the traced walls through their signed distance (keeps thin walls, removes torn edges)
sd = ndi.distance_transform_edt(gold) - ndi.distance_transform_edt(~gold)
gold = (ndi.gaussian_filter(sd, 2.5) > 0.0) & mask
lab, n = ndi.label(~gold & mask); sz = ndi.sum(~gold & mask, lab, range(1, n + 1))
gold |= np.isin(lab, 1 + np.nonzero(sz < 400)[0])          # small enamel islands become gold
enamel = mask & ~gold

gem = np.zeros_like(mask)
if gem_xy:
    lab_e, _ = ndi.label(enamel)
    gid = lab_e[gem_xy[1], gem_xy[0]]
    if gid:
        gem = lab_e == gid
        if gem.sum() > 0.03 * mask.sum():
            raise SystemExit(f'gem cell too large ({int(gem.sum())} px): a wall around it is open')
        enamel &= ~gem

np.savez_compressed(D / 'trace/carve_masks.npz', gold=gold, enamel=enamel, gem=gem)
# ---------------- height field (pixels) ----------------
d_out = ndi.distance_transform_edt(mask)
d_gold = ndi.distance_transform_edt(~gold)          # enamel: distance to nearest wall
d_in_gold = ndi.distance_transform_edt(gold)        # gold: distance to its own edge
E0, DOME, RIM_W = 34.0, 6.0, 9.0
# v7: gold walls are low rounded beads (sides under about 45 degrees, so they mirror the bright studio, not its
# dark sides), and wide gold rises further to a ridge along its middle (spikes read as two facets)
BEV, BEV_H, RIDGE, RIDGE_MAX = 7.0, 5.0, 0.45, 8.0
z = np.zeros((H, W))
z_en = E0 + DOME * (1 - np.exp(-d_gold / 14.0))
tb = np.clip(d_in_gold / BEV, 0, 1)
z_gold = E0 + BEV_H * (1 - (1 - tb) ** 2) + np.clip((d_in_gold - BEV) * RIDGE, 0, RIDGE_MAX)
z = np.where(gold, z_gold, z_en)
if gem.any():
    d_gem = ndi.distance_transform_edt(gem)
    z = np.where(gem, E0 + 4 + 0.75 * d_gem, z)    # a faceted pyramid: planes meeting along the star's skeleton
# rounded outline edge
edge = np.sqrt(np.clip(1 - (1 - np.clip(d_out / RIM_W, 0, 1)) ** 2, 0, 1))
z = z * edge
z = ndi.gaussian_filter(z, 1.7) * mask
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
_mx, _mn = den.max(2), den.min(2)
whiteish = ((_mx - _mn) / np.maximum(_mx, 1e-6) < 0.25) & (den @ np.array([0.299, 0.587, 0.114]) > 0.55)
gold_rgb = np.array([218, 151, 0]) / 255.0       # v7: measured: the app showed (245, 178, 58) pale and greyish next to the mockup's gold
# enamel as tinted metal reads saturated under the app's bright studio (plain gloss turns pastel);
# near white enamel stays mostly dielectric so it reads as porcelain, not chrome
# glossy enamel (dielectric): solve each pixel's albedo backwards from the mockup's color through the app's
# measured response (display_linear = gain * albedo_linear + offset), as the badge guide describes
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from agx import agx_inv, agx
cal = json.loads((Path(__file__).resolve().parent / 'calibration.json').read_text())
gain, off = np.array(cal['gain']), np.array(cal['offset'])
from scipy.spatial import cKDTree
# a forward table over the light reaching the eye (paint times studio light, plus glow where paint cannot reach):
# each mockup color takes the nearest; paint carries what it can, a glow adds the rest (badge guide, section 4)
lv = np.r_[0.0, np.geomspace(0.003, 10.0, 72)]
L3 = np.stack(np.meshgrid(lv, lv, lv, indexing='ij'), -1).reshape(-1, 3)
shown = np.clip(agx(L3), 0, 1)
q = np.round(np.clip(den, 0, 1) * 63).astype(int)
keys = q[..., 0] * 4096 + q[..., 1] * 64 + q[..., 2]
uniq, inv = np.unique(keys.ravel(), return_inverse=True)
pal = np.stack([uniq // 4096, (uniq // 64) % 64, uniq % 64], -1) / 63.0
_, nn = cKDTree(shown).query(pal)
L_pal = L3[nn]
alb_pal = np.clip((L_pal - off) / gain, 0.0, 1.0)
emi_pal = np.clip(L_pal - off - gain * alb_pal, 0.0, 1.0)
alb_lin = alb_pal[inv].reshape(den.shape)
emi_lin = emi_pal[inv].reshape(den.shape)
np.save(D / 'trace/predicted.npy', np.clip(agx(alb_lin * gain + off + emi_lin), 0, 1))
den = alb_lin ** (1 / 2.2)
# the color map is written from the solved enamel colors (this came before the solve until v6, by mistake)
col = np.where(gold[..., None], gold_rgb, den)
gsoft = ndi.gaussian_filter(gold.astype(float), 0.8)[..., None]
col = gold_rgb * gsoft + den * (1 - gsoft)
metal = np.where(gold, 1.0, 0.0)
# v7: colored enamel glossy but not glassy (0.05 drew rippled glare streaks); ivory and white enamel satin
rough = np.where(gold, 0.26, np.where(gem, 0.06, np.where(whiteish, 0.28, 0.12)))
pad = ndi.distance_transform_edt(~mask, return_distances=False, return_indices=True)
col, metal, rough = col[pad[0], pad[1]], metal[pad[0], pad[1]], rough[pad[0], pad[1]]
tw, th = TEX, int(round(TEX * H / W))
Image.fromarray(np.uint8(np.clip(col, 0, 1) * 255)).resize((tw, th), Image.LANCZOS).save(D / 'textures/badge_color.png')
Image.fromarray(np.uint8(metal * 255)).resize((tw, th), Image.BILINEAR).save(D / 'textures/badge_metal.png')
emi = np.where(gold[..., None] | gem[..., None], 0.0, emi_lin)[pad[0], pad[1]]
Image.fromarray(np.uint8(np.clip(emi, 0, 1) * 255)).resize((tw, th), Image.BILINEAR).save(D / 'textures/badge_emissive.png')
print('glow share', round(float((emi_lin.max(2) > 0.02)[enamel].mean()), 3))
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
# smooth shading: normals straight from the smoothed height field, not from the triangles
Zs = ndi.gaussian_filter(Z, 1.2)
gy_, gx_ = np.gradient(Zs)                        # per pixel, in model units per pixel
dzdx = ndi.map_coordinates(gx_, [allp[:, 1], allp[:, 0]], order=1) / S
dzdy = -ndi.map_coordinates(gy_, [allp[:, 1], allp[:, 0]], order=1) / S   # image y runs down, model y up
Nf = unit(np.c_[-dzdx, -dzdy, np.ones(len(allp))])
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
