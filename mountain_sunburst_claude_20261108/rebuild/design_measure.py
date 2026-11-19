"""Measure the Radiant Mountain Sunburst's shapes from the mockup into design.json (plan section 8, step 1).

Ring and sun are fitted circles. Every enamel area is traced from the cleaned gold and enamel split
(trace/carve_masks.npz), split by color where several colors share one traced cell, simplified to straight
edged polygons (3 px tolerance) and grown by half a line width to the gold line centerlines. Wide gold parts
(spike blades and points, the border, the star frame, the curls) are what remains after removing the line
network. Symmetric shapes are measured on the left and mirrored about x 653.5. Python 3.11 with shapely.
"""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.cluster.vq import kmeans2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import shapely
from shapely.geometry import Polygon, MultiPolygon, Point, box
from shapely.ops import unary_union
from shapely.affinity import scale as sscale

HERE = Path(__file__).resolve().parent; BADGE = HERE.parent
img = np.asarray(Image.open(BADGE / 'reference/mockup.png').convert('RGB')).astype(float) / 255
H, W = img.shape[:2]
AX = 653.5
RING_C = (AX, 557.9); RING_R = 473.7; RING_W = 28.6
SUN_C = (AX, 566.2); SUN_R = 195.0; SUN_RIM = 218.0
LINE_W = 11.5
cm = np.load(BADGE / 'trace/carve_masks.npz'); gold, enamel, gemm = cm['gold'], cm['enamel'], cm['gem']
mask = np.load(BADGE / 'trace/mask.npy')
LEFT = box(-10, -10, AX, H + 10)


def mirror(g):
    return sscale(g, xfact=-1, yfact=1, origin=(AX, 0))


def symmetric(g):
    """Left half kept and mirrored onto the right."""
    l = g.intersection(LEFT)
    return unary_union([l, mirror(l)]).buffer(0)


def polys_from_mask(m, min_area=150, smooth=1.2):
    """Traced region outlines as shapely polygons (holes kept)."""
    f = ndi.gaussian_filter(m.astype(float), smooth)
    cs = plt.contour(f, levels=[0.5]); segs = [np.asarray(s) for s in cs.allsegs[0] if len(s) > 8]; plt.close('all')
    rings = [Polygon(s).buffer(0) for s in segs]
    rings = [r for r in rings if r.area > 20]
    out = []
    for r in sorted(rings, key=lambda r: -r.area):           # even odd nesting: an outline inside another is a hole
        depth = sum(1 for o in rings if o is not r and o.area > r.area and o.contains(r.representative_point()))
        out.append((depth, r))
    acc = Polygon()
    for depth, r in out:
        acc = acc.union(r) if depth % 2 == 0 else acc.difference(r)
    parts = [p for p in (acc.geoms if isinstance(acc, MultiPolygon) else [acc]) if p.area >= min_area]
    return parts


def clean(p, tol=3.0):
    return p.simplify(tol, preserve_topology=True).buffer(0)


def grown(p):
    return p.buffer(LINE_W / 2, join_style='mitre', mitre_limit=3.0)


# ---------- enamel areas by color family ----------
base = np.stack([ndi.median_filter(img[..., k], size=7) for k in range(3)], -1)
mx, mn = base.max(2), base.min(2); sat = (mx - mn) / np.maximum(mx, 1e-6); lum = base @ np.array([0.299, 0.587, 0.114])
dch = np.maximum(mx - mn, 1e-6); r_, g_, b_ = base.transpose(2, 0, 1)
hue = np.where(mx == r_, ((g_ - b_) / dch) % 6, np.where(mx == g_, (b_ - r_) / dch + 2, (r_ - g_) / dch + 4)) * 60
fam = np.full((H, W), -1)
FAM = ['red', 'yellow', 'white', 'blue', 'dark']
fam[((hue < 24) | (hue > 340)) & (sat > 0.45) & (lum > 0.18)] = 0
fam[(hue >= 24) & (hue < 62) & (sat > 0.5)] = 1
fam[(sat < 0.28) & (lum > 0.55)] = 2
fam[(hue >= 180) & (hue < 255) & (sat > 0.25)] = 3
fam[(fam < 0) & (lum <= 0.25)] = 4
lab, n = ndi.label(enamel)
votes = np.stack([ndi.uniform_filter((fam == j).astype(float), 17) for j in range(len(FAM))], -1)
famv = np.where(enamel, np.argmax(votes, -1), -1)                          # highlights and shading voted away
areas = []
for i in range(1, n + 1):
    cell = lab == i
    if cell.sum() < 150:
        continue
    for j, fname in enumerate(FAM):
        mm = cell & (famv == j)
        if mm.sum() < 250:
            continue
        if fname == 'blue':                                                # split the blues into their shades
            ys, xs = np.nonzero(mm); X = np.c_[lum[ys, xs], hue[ys, xs] / 360]
            kk = np.zeros(len(ys), int)
            for k in (3, 2):
                if len(ys) < 600 * k:
                    continue
                cent, lb = kmeans2(X, k, seed=1, minit='++')
                d_ = np.abs(cent[:, None, 0] - cent[None, :, 0]) + np.eye(k)
                if d_.min() > 0.06 and (np.bincount(lb, minlength=k) / len(lb)).min() > 0.08:
                    kk = lb; break
            lm = np.full((H, W), -1); lm[ys, xs] = kk
            vv = np.stack([ndi.uniform_filter((lm == q).astype(float), 21) for q in range(kk.max() + 1)], -1)
            kk = np.argmax(vv[ys, xs], 1)
            subs = []
            for q in range(kk.max() + 1):
                sm = np.zeros((H, W), bool); sm[ys[kk == q], xs[kk == q]] = True; subs.append(sm)
            subs.sort(key=lambda sm: -float(lum[sm].mean()))
            shade = ['teal', 'steel', 'navy'] if len(subs) == 3 else (['teal', 'navy'] if len(subs) == 2 else ['blue'])
            for sm, nm in zip(subs, shade):
                for pp in polys_from_mask(sm, 250):
                    areas.append(dict(color=nm, rgb=np.median(base[sm], 0).round(3).tolist(), poly=pp, cell=i))
        else:
            for pp in polys_from_mask(mm, 250):
                areas.append(dict(color=fname, rgb=np.median(base[mm], 0).round(3).tolist(), poly=pp, cell=i))
print('traced areas', len(areas), {c: sum(1 for a in areas if a['color'] == c) for c in ['red', 'yellow', 'white', 'teal', 'steel', 'navy', 'blue', 'dark']})

# ---------- save a first version for checkpoint 1 ----------
def coords(p):
    return [list(map(lambda v: round(v, 1), xy)) for xy in np.asarray(p.exterior.coords)]
design = dict(units=dict(S=5.45 / 1161, axis=AX, top=15.0, bottom=1176.0), ring=dict(center=RING_C, r_outer=RING_R, width=RING_W),
              sun=dict(center=SUN_C, r_enamel=SUN_R, r_rim=SUN_RIM), line_width=LINE_W,
              areas=[dict(id=k, color=a['color'], rgb=a['rgb'], cell=int(a['cell']), poly=coords(clean(a['poly'])), holes=[coords(Polygon(h)) for h in clean(a['poly']).interiors]) for k, a in enumerate(areas)])
json.dump(design, open(HERE / 'design_traced.json', 'w'), indent=0)
