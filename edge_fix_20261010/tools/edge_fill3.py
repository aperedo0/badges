"""edge_fill3.py <model.npz> <pkg_dir> <inset_px> : like edge_fill2 (refill color and emissive texels near the outline from the nearest
kept texel of the same island), with two changes:
1. Visible side walls: a texel also counts as near the outline when it lies within the inset of the FRONT surface's edge (the union of
   camera facing triangles, n dot view > 0.5) and that edge is itself near the full silhouette (within inset + 8 px), which is where a
   side wall shows beyond the front face. Interior seams far from the silhouette stay untouched.
2. Thin parts: the inset shrinks to a third of the local thickness (the largest distance to the silhouette within 6 px), so a thin tip
   is never refilled across its whole width."""
import sys, json, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt, label, map_coordinates, find_objects, maximum_filter
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from common import to_screen, CAM_POS
d = np.load(sys.argv[1]); pkg = sys.argv[2]; inset = float(sys.argv[3]); info = json.loads(str(d['info']))
SS = 4
allp = d['ALLP']; scr = to_screen(allp.reshape(-1, 3)).reshape(-1, 3, 2)
x0, y0 = np.floor(scr.reshape(-1, 2).min(0)).astype(int) - 12; x1, y1 = np.ceil(scr.reshape(-1, 2).max(0)).astype(int) + 12
def raster(tris):
    img = Image.new('L', ((x1 - x0) * SS, (y1 - y0) * SS), 0); dr = ImageDraw.Draw(img)
    for t in tris: dr.polygon([((p[0] - x0) * SS, (p[1] - y0) * SS) for p in t], fill=255)
    return np.asarray(img) > 127
n = np.cross(allp[:, 1] - allp[:, 0], allp[:, 2] - allp[:, 0]); n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
view = CAM_POS - allp.mean(1); view /= np.linalg.norm(view, axis=1, keepdims=True)
facing = (n * view).sum(1) > 0.5
sil = raster(scr); front = raster(scr[facing])
dsil = distance_transform_edt(sil) / SS; dfront = distance_transform_edt(front) / SS
thick = maximum_filter(dsil, size=int(12 * SS) + 1)
def sample(f, s): return map_coordinates(f, [(s[:, 1] - y0) * SS, (s[:, 0] - x0) * SS], order=1, mode='constant', cval=0)
maps = {}
for mat, mi in info.items():
    for kind in ('diffuseColor', 'emissiveColor'):
        f = mi['files'].get(kind)
        if f: maps.setdefault(f, set()).add(mat)
for f, mats in maps.items():
    path = f'{pkg}/{f}'; im = Image.open(path); mode = im.mode; a = np.asarray(im.convert('RGB')).copy(); Hh, Ww = a.shape[:2]
    cover = np.zeros((Hh, Ww), bool); near = np.zeros((Hh, Ww), bool)
    sel = np.isin(d['MAT'], list(mats)); P = d['P'][sel]; UV = d['UV'][sel]
    for tri, uv in zip(P, UV):
        px = np.stack([uv[:, 0] * Ww - .5, (1 - uv[:, 1]) * Hh - .5], -1)
        bx0, by0 = np.floor(px.min(0)).astype(int); bx1, by1 = np.ceil(px.max(0)).astype(int)
        xs, ys = np.meshgrid(np.arange(max(bx0, 0), min(bx1, Ww - 1) + 1), np.arange(max(by0, 0), min(by1, Hh - 1) + 1))
        e1 = px[1] - px[0]; e2 = px[2] - px[0]; den = e1[0] * e2[1] - e1[1] * e2[0]
        if abs(den) < 1e-12 or xs.size == 0: continue
        u = ((xs - px[0, 0]) * e2[1] - (ys - px[0, 1]) * e2[0]) / den; v = (e1[0] * (ys - px[0, 1]) - e1[1] * (xs - px[0, 0])) / den
        ins = (u >= -0.01) & (v >= -0.01) & (u + v <= 1.01)
        if not ins.any(): continue
        w0 = 1 - u[ins] - v[ins]; pos = w0[:, None] * tri[0] + u[ins][:, None] * tri[1] + v[ins][:, None] * tri[2]
        s = to_screen(pos)
        ds = sample(dsil, s); df = sample(dfront, s); th = sample(thick, s)
        local = np.minimum(inset, th / 3.0)
        hit = (ds < local) | ((df < local) & (ds < inset + 8))
        cover[ys[ins], xs[ins]] = True
        near[ys[ins], xs[ins]] |= hit
    kept = cover & ~near; out = a.copy()
    lab, nlab = label(cover, structure=np.ones((3, 3))); left = 0
    for i, sl in enumerate(find_objects(lab), start=1):
        if sl is None: continue
        isl = lab[sl] == i; k = kept[sl] & isl; fix = isl & ~k
        if not fix.any(): continue
        if not k.any(): left += 1; continue
        _, (iy, ix) = distance_transform_edt(~k, return_indices=True)
        blk = out[sl]; src = a[sl]; blk[fix] = src[iy[fix], ix[fix]]; out[sl] = blk
    _, (iy, ix) = distance_transform_edt(~cover, return_indices=True)
    take = ~cover & (cover & near)[iy, ix]
    out = np.where(take[..., None], out[iy, ix], out)
    Image.fromarray(out).convert(mode).save(path)
    print(f'{f}: covered {cover.mean():.3f} refilled {int((cover & near).sum())} islands {nlab} left {left}')
