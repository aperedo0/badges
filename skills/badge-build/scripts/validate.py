"""Contract and stack checks for a badge built by badge3d.py (badge-build skill). Python 3.11.

Usage: validate.py CAND_DIR [--break-shift | --break-base]   (the break options prove the checks can fail)
Checks: bounds without rescaling, the triangle budget, Z centered, names, each part closed with positive volume, each back the
mirror of its front, the gem's foil UVs, and per pixel stacking: the top front surface belongs to the latest
part in the stack order and stands at least 0.006 above the next.
"""
import sys, json
from pathlib import Path
import numpy as np
from matplotlib.tri import Triangulation, LinearTriInterpolator
C = Path(sys.argv[1]); D = dict(np.load(C / 'parts.npz')); META = json.load(open(C / 'parts.json'))
if 'validate_order' in META:
    byname = {q['name']: q for q in META['parts']}; META['parts'] = [byname[n] for n in META['validate_order']]
U = META['units']; S = U['S']; AX = U['axis']; TOP = U.get('top', 15.0); BOX = META.get('box') or [AX - 600, TOP, AX + 600, TOP + 5.45 / S]; fails = []
if '--break-shift' in sys.argv:
    for k in D:
        if k.endswith('_v'):
            D[k] = D[k] + np.array([0, 0.01, 0], np.float32)
if '--break-base' in sys.argv:
    k = META['parts'][-2]['name'] + '_v'; v = D[k]; D[k] = np.where(v[..., 2:3] > 0, v - [0, 0, 0.06], v + [0, 0, 0.06]).astype(np.float32)
allv = np.vstack([D[p['name'] + '_v'].reshape(-1, 3) for p in META['parts']])
lo, hi = allv.min(0), allv.max(0)
# bottom at the shared floating height; top at 2.995, or lower only when the width limit (X 3.35) is what stops it
wide = max(abs(lo[0]), abs(hi[0])) >= 3.30
if abs(lo[1] + 2.455) > 0.004 or hi[1] > 2.999 or (hi[1] < 2.991 and not wide):
    fails.append(f'Y bounds {lo[1]:.4f} to {hi[1]:.4f}, want -2.455 to 2.995 (top lower only for a badge as wide as X 3.35)')
TRIS = sum(p['triangles'] for p in META['parts'])
if TRIS > 45000 and not META.get('budget_reason'):
    fails.append(f'{TRIS} triangles, over the 45,000 budget (AGENTS.md 3.8): reduce, or give "budget_reason" in PIECES.json and say it in the report')
if max(abs(lo[0]), abs(hi[0])) > 3.35: fails.append(f'X extent {lo[0]:.3f} {hi[0]:.3f}')
if abs(hi[2] + lo[2]) > 0.002: fails.append(f'Z not centered {lo[2]:.4f} {hi[2]:.4f}')
names = sum((p['materials'] for p in META['parts']), [])
if any('Casing' in n or 'circumferential' in n for n in names): fails.append('coin names used')
for p in META['parts']:
    V = D[p['name'] + '_v']; key = np.round(V.reshape(-1, 3), 5); u, inv = np.unique(key, axis=0, return_inverse=True); F = inv.reshape(-1, 3)
    E = np.sort(np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), 1); _, cnt = np.unique(E, axis=0, return_counts=True)
    open_edges = int((cnt == 1).sum())
    vol = float(np.sum(np.einsum('ij,ij->i', V[:, 0], np.cross(V[:, 1], V[:, 2]))) / 6)
    front = V[:p['front']]; back = V[p['front']:2 * p['front']]
    mirror_err = float(np.abs(np.sort((back * [1, 1, -1]).reshape(-1, 3), 0) - np.sort(front.reshape(-1, 3), 0)).max())
    if open_edges: fails.append(f"{p['name']}: {open_edges} open edges")
    if vol <= 0: fails.append(f"{p['name']}: volume {vol:.5f} not positive")
    if mirror_err > 1e-5: fails.append(f"{p['name']}: back is not the mirror of the front ({mirror_err:.2e})")
if 'gem_uv' in D:                                            # a badge without a gem skips this (it crashed before)
    uv = D['gem_uv']; zc = D['gem_v'].mean(1)[:, 2]
    if not (np.allclose(uv[zc >= 0], [0, 0.5]) and np.allclose(uv[zc < 0], [0.5, 0.5])): fails.append('gem foil UVs wrong')
# side walls in the same place: two pieces whose visible outlines run within 1.5 px of each other flicker when turned
import shapely
from shapely.geometry import MultiLineString
outl = {}
for p in META['parts']:
    T = D[p['name'] + '_v'][:p['front']][..., :2]; key = np.round(T.reshape(-1, 2), 5)
    uq, inv = np.unique(key, axis=0, return_inverse=True); F = inv.reshape(-1, 3)
    E = np.sort(np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), 1); e, c = np.unique(E, axis=0, return_counts=True)
    bE = e[c == 1]; pts = np.c_[uq[:, 0] / S + AX, TOP + (2.995 - uq[:, 1]) / S]
    outl[p['name']] = MultiLineString([[pts[a].tolist(), pts[b].tolist()] for a, b in bE])
names_ = [p['name'] for p in META['parts']]
for i, a in enumerate(names_):
    for b in names_[i + 1:]:
        if a == 'core' or b == 'core':
            continue
        sh = outl[a].intersection(outl[b].buffer(1.5)); shared = sh.length
        if shared > 25:                                           # fails on any single run over 30 px; short contacts where
            from shapely.ops import linemerge as _lm, unary_union as _uu   # three outlines meet are unavoidable
            _m = _lm(_uu([g for g in getattr(sh, 'geoms', [sh]) if g.length > 0]))
            if max((g.length for g in getattr(_m, 'geoms', [_m])), default=0) <= 30:
                continue
            parts_ = [g for g in getattr(sh, 'geoms', [sh]) if g.length > 0]
            from shapely.ops import linemerge, unary_union as uu
            runs = sorted([g for g in getattr(linemerge(uu(parts_)), 'geoms', [linemerge(uu(parts_))])], key=lambda g: -g.length)[:3]
            where_ = ', '.join(f'{g.length:.0f} px at ({g.centroid.x:.0f}, {g.centroid.y:.0f})' for g in runs)
            fails.append(f'{a} and {b}: outlines run together for {shared:.0f} px (side walls in the same place): {where_}')
# per pixel stack check at 1x mockup pixels
xs = np.arange(BOX[0], BOX[2], 2.0); ys = np.arange(BOX[1], BOX[3], 2.0); X, Y = np.meshgrid(xs, ys)
MX, MY = (X - AX) * S, 2.995 - (Y - TOP) * S
Z = []; self_overlap = {}
H_, W_ = X.shape
for p in META['parts']:
    T3 = D[p['name'] + '_v'][:p['front']]
    px = (T3[..., 0] / S + AX - BOX[0]) / 2.0; py = (TOP + (2.995 - T3[..., 1]) / S - BOX[1]) / 2.0
    z = np.full((H_, W_), np.nan); hits = np.zeros((H_, W_), np.int16)
    for (x0, x1, x2), (y0, y1, y2), (z0, z1, z2) in zip(px, py, T3[..., 2]):
        bx0, bx1 = int(max(np.floor(min(x0, x1, x2)), 0)), int(min(np.ceil(max(x0, x1, x2)), W_ - 1))
        by0, by1 = int(max(np.floor(min(y0, y1, y2)), 0)), int(min(np.ceil(max(y0, y1, y2)), H_ - 1))
        if bx1 < bx0 or by1 < by0:
            continue
        gy, gx = np.mgrid[by0:by1 + 1, bx0:bx1 + 1]
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-12:
            continue
        w0 = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / den; w1 = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / den; w2 = 1 - w0 - w1
        ins = (w0 > 1e-6) & (w1 > 1e-6) & (w2 > 1e-6)
        if ins.any():
            z[gy[ins], gx[ins]] = (w0 * z0 + w1 * z1 + w2 * z2)[ins]; hits[gy[ins], gx[ins]] += 1
    Z.append(z); self_overlap[p['name']] = int((hits > 1).sum())
for k, v in self_overlap.items():
    if v > 0:
        fails.append(f'{k}: {v} pixels covered twice by its own front (flicker)')
Z = np.array(Z); covered = ~np.isnan(Z)
order = np.arange(len(Z))[:, None, None] * np.ones_like(Z)
top_part = np.where(covered, order, -1).max(0).astype(int)                         # latest part in the stack covering each pixel
zs = np.where(covered, Z, -np.inf); top_z = zs.max(0)
ok_top = (np.take_along_axis(zs, top_part[None].clip(0), 0)[0] >= top_z - 1e-9) | (top_part < 0)
second = np.sort(zs, 0)[-2]; gap = top_z - second
bad_order = int((~ok_top).sum()); thin = int(((covered.sum(0) >= 2) & (gap < 0.006 - 1e-6)).sum())
names = [p['name'] for p in META['parts']]; high_part = np.argmax(zs, 0)
second_part = np.argsort(zs, 0)[-2]


def where(mask, a, b):
    """Name the pieces and the mockup spots of each problem, largest first."""
    from scipy import ndimage as ndi
    lab, n = ndi.label(mask); out = []
    for i in range(1, n + 1):
        m = lab == i; yy, xx = np.nonzero(m)
        pa = names[int(np.bincount(a[m]).argmax())]; pb = names[int(np.bincount(b[m]).argmax())]
        out.append((int(m.sum()), pa, pb, int(BOX[0] + 2 * xx.mean()), int(BOX[1] + 2 * yy.mean())))
    return sorted(out, reverse=True)[:6]


if bad_order:
    fails.append(f'{bad_order} pixels where an earlier part shows above a later one: ' +
                 '; '.join(f'{n} px, {a} above {b} at ({x}, {y})' for n, a, b, x, y in where(~ok_top, high_part, top_part.clip(0))))
if thin:
    fails.append(f'{thin} pixels where two surfaces are closer than 0.006: ' +
                 '; '.join(f'{n} px, {a} over {b} at ({x}, {y})' for n, a, b, x, y in where((covered.sum(0) >= 2) & (gap < 0.006 - 1e-6), high_part, second_part)))
print(json.dumps(dict(bounds=[lo.round(4).tolist(), hi.round(4).tolist()], triangles=sum(p['triangles'] for p in META['parts']),
                      max_front_z={p['name']: round(float(D[p['name'] + '_v'][:p['front']][..., 2].max()), 3) for p in META['parts']}, failures=fails), indent=1))
sys.exit(1 if fails else 0)
