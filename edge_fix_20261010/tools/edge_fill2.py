"""edge_fill2.py <model.npz> <pkg_dir> <inset_px> : for every color and emissive map of the package, refills the texels whose surface
point projects (app camera) within <inset_px> Home pixels of the badge's silhouette against the background, from the nearest kept
texel of the same UV island; texels no triangle covers are refilled from the nearest covered texel. Interior seams stay untouched.
Writes maps in place and prints per map statistics."""
import sys, json, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt, label, map_coordinates, find_objects
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from common import to_screen
d = np.load(sys.argv[1]); pkg = sys.argv[2]; inset = float(sys.argv[3]); info = json.loads(str(d['info']))
# silhouette: union of every projected triangle, 4x supersampled over the screenshot
SS = 4; W, H = 1206, 2622
allp = d['ALLP']; scr = to_screen(allp.reshape(-1, 3)).reshape(-1, 3, 2)
x0, y0 = np.floor(scr.reshape(-1, 2).min(0)).astype(int) - 8; x1, y1 = np.ceil(scr.reshape(-1, 2).max(0)).astype(int) + 8
img = Image.new('L', ((x1 - x0) * SS, (y1 - y0) * SS), 0); dr = ImageDraw.Draw(img)
for t in scr: dr.polygon([((p[0] - x0) * SS, (p[1] - y0) * SS) for p in t], fill=255)
sil = np.asarray(img) > 127
dist = distance_transform_edt(sil) / SS          # Home pixels to the outside, inside the silhouette
# group textured triangles by map file
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
        dd = map_coordinates(dist, [(s[:, 1] - y0) * SS, (s[:, 0] - x0) * SS], order=1, mode='constant', cval=0)
        cover[ys[ins], xs[ins]] = True
        near[ys[ins], xs[ins]] |= dd < inset
    kept = cover & ~near; out = a.copy()
    lab, n = label(cover, structure=np.ones((3, 3)))
    unchanged_islands = 0
    for i, sl in enumerate(find_objects(lab), start=1):
        if sl is None: continue
        isl = lab[sl] == i; k = kept[sl] & isl; fix = isl & ~k
        if not fix.any(): continue
        if not k.any(): unchanged_islands += 1; continue
        _, (iy, ix) = distance_transform_edt(~k, return_indices=True)
        blk = out[sl]; src = a[sl]
        blk[fix] = src[iy[fix], ix[fix]]; out[sl] = blk
    # uncovered texels: refilled from their nearest covered texel only when that texel was refilled (near the outline);
    # every other uncovered texel (padding beside interior seams) stays byte identical
    _, (iy, ix) = distance_transform_edt(~cover, return_indices=True)
    refilled = cover & near & np.any(out != a, axis=-1) | (cover & near)
    take = ~cover & refilled[iy, ix]
    out = np.where(take[..., None], out[iy, ix], out)
    Image.fromarray(out).convert(mode).save(path)
    print(f'{f}: materials {sorted(mats)} covered {cover.mean():.3f} refilled near outline {int((cover & near).sum())} islands {n} islands left as is {unchanged_islands}')
