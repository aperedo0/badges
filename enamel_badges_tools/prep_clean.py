"""Prepare a clean enamel badge for building in the open Blender.

Usage: prep_clean.py BADGE_DIR OUT_DIR [--gem X,Y]

Reads the cleaned gold, enamel and gem masks (trace/carve_masks.npz, written by carve_badge.py) and the mockup.
Writes OUT_DIR/prep.npz with:
  * smooth signed fields (gold walls against enamel cells, and the outline), so every line is a clean curve;
  * vertex rings along the level lines of those fields plus their constraint edges, so the triangles that
    Blender builds follow every gold line instead of crossing it (the November 8 fuzz came from a fixed grid);
  * the height field and its normals, sampled later at each vertex;
  * the gem star (center, tips, inner corners, outline) for flat facets.
And OUT_DIR/textures: enamel colors fitted smoothly per cell (no painted blotches), solved through the app's
measured light, plus roughness and glow maps. Gold, gem and side wall get plain materials in Blender.
"""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from agx import agx
from scipy.spatial import cKDTree

D = Path(sys.argv[1]); OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True); (OUT / 'textures').mkdir(exist_ok=True)
cfg = json.loads((D / 'review.json').read_text()); cx_px, top_px, bot_px = cfg['mockup_box']
img = np.asarray(Image.open(D / 'reference/mockup.png').convert('RGB')).astype(float) / 255
cm = np.load(D / 'trace/carve_masks.npz'); gold0, enamel0, gem0 = cm['gold'], cm['enamel'], cm['gem']
mask = gold0 | enamel0 | gem0
H, W = mask.shape; S = 5.45 / (bot_px - top_px)

# ---------- smooth fields ----------
def sdf(m):
    return ndi.distance_transform_edt(m) - ndi.distance_transform_edt(~m)
o = ndi.gaussian_filter(sdf(mask), 2.0)                    # outline: positive inside
inside = o > 0
gem = np.zeros_like(mask); gold_base = gold0.copy()
if '--gem' in sys.argv:
    # the gem by its own color: its traced cell leaked into the frame's lower arm. Mirrored about its own
    # center column so the star is symmetric, with a solid gold frame band around it
    gx, gy = (int(v) for v in sys.argv[sys.argv.index('--gem') + 1].split(','))
    r_, g_, b_ = img.transpose(2, 0, 1); mx_, mn_ = img.max(2), img.min(2); sat_ = (mx_ - mn_) / np.maximum(mx_, 1e-6)
    dch = np.maximum(mx_ - mn_, 1e-6)
    hue_ = np.where(mx_ == r_, ((g_ - b_) / dch) % 6, np.where(mx_ == g_, (b_ - r_) / dch + 2, (r_ - g_) / dch + 4)) * 60
    lum_ = img @ np.array([0.299, 0.587, 0.114])
    gemc = ((hue_ > 175) & (hue_ < 220) & (sat_ > 0.2)) | ((lum_ > 0.85) & (sat_ < 0.25) & (b_ >= r_))
    win = np.zeros_like(gemc); win[max(0, gy - 220):gy + 220, max(0, gx - 220):gx + 220] = True
    m = ndi.binary_opening(gemc & win, iterations=1)
    lab, n = ndi.label(m)
    seed = lab[gy, gx] if lab[gy, gx] else lab.ravel()[np.argmin(np.where(lab.ravel() > 0, np.hypot(*(np.indices(lab.shape).reshape(2, -1) - [[gy], [gx]])), 1e9))]
    m = ndi.binary_fill_holes(ndi.binary_closing(lab == seed, iterations=3))
    xs_ = np.nonzero(m.any(0))[0]; cxg = (xs_.min() + xs_.max()) / 2
    mir = np.clip(np.round(2 * cxg - np.arange(W)).astype(int), 0, W - 1)
    sg = sdf(m); gem = ((sg + sg[:, mir]) / 2) > 0
    FRAME_W = 0.03 * (bot_px - top_px) * 0.98                # the star frame band, about 3% of the badge width
    frame = (ndi.distance_transform_edt(~gem) < FRAME_W) & mask
    gold_base = (gold0 | frame) & ~gem
# ---------- hand corrections to the trace ----------
ov_path = D / 'clean_overrides.json'
if ov_path.exists():
    ov = json.loads(ov_path.read_text())
    lab0, _ = ndi.label(mask & ~gold_base)
    for x, y in ov.get('gold_cells', []):
        k = lab0[int(y), int(x)]
        if k:
            gold_base |= lab0 == k
    print('hand corrections: gold cells', len(ov.get('gold_cells', [])))

# ---------- even walls ----------
# Each enamel cell is smoothed on its own (straight edges, no wobble). Every wall between two cells is then
# redrawn at one width, its own typical width, centered where the traced wall ran. Wide gold (spikes, frames,
# the outer border) keeps its traced shape.
cells0 = mask & ~gold_base
lab, n = ndi.label(cells0); sz = ndi.sum(cells0, lab, range(1, n + 1))
keep_ids = [i + 1 for i in range(n) if sz[i] >= 400]
BIG = 1e4
d1 = np.full((H, W), BIG); d2 = np.full((H, W), BIG); L1 = np.full((H, W), -1); L2 = np.full((H, W), -1)
def push(dist, k):
    global d1, d2, L1, L2
    better = dist < d1
    d2 = np.where(better, d1, np.minimum(d2, dist)); L2 = np.where(better, L1, np.where(dist < d2, k, L2))
    d1 = np.where(better, dist, d1); L1 = np.where(better, k, L1)
push(np.maximum(-ndi.gaussian_filter(sdf(~mask), 2.0), 0), 0)            # label 0: outside the badge
depth = np.full((H, W), -BIG)
for k in keep_ids:
    sk = ndi.gaussian_filter(sdf(lab == k), 3.0); depth = np.maximum(depth, sk)
    push(np.maximum(-sk, 0), k)
gap = d1 + d2
medial = (np.abs(d2 - d1) < 1.5) & (d1 > 0)
pair = L1 * 1000 + L2; pair = np.where(L1 < L2, pair, L2 * 1000 + L1)
wpair = {}
for key in np.unique(pair[medial]):
    a_, b_ = divmod(int(key), 1000)
    if a_ == 0 or b_ == 0:
        continue                                                 # the outer border keeps its traced shape
    g = gap[medial & (pair == key)]
    if len(g) < 15:
        continue
    med = float(np.median(g)); cv = float(np.std(g) / max(med, 1e-6))
    if med < 30 and cv < 0.45:                                   # a wall, not a tapering spike or a solid part
        wpair[int(key)] = max(0.8 * med, 9.0)                 # the traced gold includes the dark edge lines
w_map = np.zeros((H, W))
for key, w in wpair.items():
    w_map[(pair == key) & (gap < 2.2 * w)] = w             # only near that wall: a line inside one cell keeps its own
gold_new = np.where(w_map > 0, (d2 - d1) < w_map, d1 > 0) & mask
# gold lines that run inside a cell without closing it (a snowline, a ridge line) survive the cell smoothing
frag = gold_base & (depth > 0.5)
lab_f, n_f = ndi.label(frag); idf = np.arange(1, n_f + 1)
szf = np.array(ndi.sum(frag, lab_f, idf)); dmx = np.array(ndi.maximum(depth, lab_f, idf))
keep_f = idf[(szf >= 120) & (dmx > 4)]
fr = np.isin(lab_f, keep_f)
fr = ndi.gaussian_filter(sdf(fr), 1.5) > 0                 # smooth the kept lines a little
gold_new |= fr & mask
print('inner gold lines kept', len(keep_f))
print('even walls:', len(wpair), 'walls, widths px', sorted(round(w, 1) for w in wpair.values())[:6], '...', sorted(round(w, 1) for w in wpair.values())[-4:])
if gem.any():
    gold_new &= ~gem
s = ndi.gaussian_filter(sdf(gold_new | ~mask), 1.2)        # walls: positive in gold, negative in cells
cells = inside & (s <= 0)
lab, n = ndi.label(cells); sz = ndi.sum(cells, lab, range(1, n + 1))
tiny = np.isin(lab, 1 + np.nonzero(sz < 400)[0])
thick = np.array(ndi.maximum(ndi.distance_transform_edt(cells), lab, range(1, n + 1)))
tiny |= np.isin(lab, 1 + np.nonzero(thick < 6)[0])          # thin enamel slivers along spikes are gold facets
s = np.where(tiny, np.maximum(s, 1.0), s)                   # tiny enamel islands become gold
if gem.any():
    gem = gem & (s <= 0)

# ---------- heights (pixels) ----------
E0, DOME = 34.0, 1.5                 # enamel nearly flat, gently domed, below the wall tops
BEV, BEV_H, RIDGE0, RIDGE, RIDGE_MAX = 4.5, 5.0, 9.0, 0.40, 8.0
d_g = np.maximum(s, 0); d_e = np.maximum(-s, 0)
tb = np.clip(d_g / BEV, 0, 1)
z = np.where(s > 0, E0 + BEV_H * tb * tb * (3 - 2 * tb) + np.clip((d_g - RIDGE0) * RIDGE, 0, RIDGE_MAX),
             E0 + DOME * (1 - np.exp(-d_e / 10.0)))
z = np.where(gem, E0, z)                                    # flat floor under the gem
RIM_W, EDGE_MIN = 9.0, 0.34                                 # rounded outer edge that ends in a short side wall
te = np.clip(o / RIM_W, 0, 1)
z = z * (EDGE_MIN + (1 - EDGE_MIN) * np.sqrt(np.clip(1 - (1 - te) ** 2, 0, 1)))
z = ndi.gaussian_filter(z, 1.0)
gy_, gx_ = np.gradient(z)

# ---------- rings along level lines ----------
def contours(field, level):
    cs = plt.contour(field, levels=[level]); segs = [np.asarray(p) for p in cs.allsegs[0] if len(p) > 4]; plt.close('all')
    return segs

def simplify(p, tol):
    """Douglas Peucker on a polyline (x, y). A closed ring is split at its farthest point first."""
    if len(p) < 3:
        return p
    if np.hypot(*(p[0] - p[-1])) < 1e-6:
        k = int(np.argmax(np.hypot(*(p - p[0]).T)))
        return np.vstack([simplify(p[:k + 1], tol)[:-1], simplify(p[k:], tol)])
    keep = np.zeros(len(p), bool); keep[0] = keep[-1] = True; stack = [(0, len(p) - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        ab = p[b] - p[a]; L = np.hypot(*ab) + 1e-12
        d = np.abs(ab[0] * (p[a + 1:b, 1] - p[a, 1]) - ab[1] * (p[a + 1:b, 0] - p[a, 0])) / L
        i = int(np.argmax(d))
        if d[i] > tol:
            k = a + 1 + i; keep[k] = True; stack += [(a, k), (k, b)]
    return p[keep]

def resample(p, step, tol, maxstep):
    dd = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    t = np.arange(0, dd[-1], step)
    q = np.c_[np.interp(t, dd, p[:, 0]), np.interp(t, dd, p[:, 1])]
    if np.hypot(*(p[0] - p[-1])) < 1e-6 and len(q) > 2:
        q = np.vstack([q, q[:1]])
    q = simplify(q, tol)
    out = [q[0]]                                            # cap the gap between kept points
    for a, b in zip(q[:-1], q[1:]):
        L = np.hypot(*(b - a)); k = int(np.ceil(L / maxstep))
        for j in range(1, k + 1):
            out.append(a + (b - a) * j / k)
    return np.array(out)

pts, edges = [], []
def add_ring(p, closed_ok=True):
    base = sum(len(q) for q in pts)
    closed = np.hypot(*(p[0] - p[-1])) < 1e-6
    if closed:
        p = p[:-1]
    if len(p) < 2:
        return
    pts.append(p)
    m = len(p); e = [(base + i, base + i + 1) for i in range(m - 1)]
    if closed and m > 2:
        e.append((base + m - 1, base))
    edges.extend(e)

o_in = lambda p: ndi.map_coordinates(o, [p[:, 1], p[:, 0]], order=1)
for lv in (0.0,):                                           # the outline itself
    for p in contours(o, lv):
        add_ring(resample(p, 1.5, 0.12, 6.0))
for lv in (1.5, 4.0, 7.0):                                  # rounded outer edge
    for p in contours(o, lv):
        add_ring(resample(p, 2.0, 0.15, 8.0))
for lv in (-4.0, -1.2, 0.0, 1.5, 3.0, 4.5, 9.0, 15.0):   # enamel side, wall base, wall bevel, ridge zone
    for p in contours(np.where(inside, s, -50), lv):
        keep = o_in(p) > 1.0                                # stay inside the outline rings
        if keep.mean() < 0.999:                              # split where it leaves the inside
            runs = np.split(np.arange(len(p)), np.nonzero(np.diff(keep.astype(int)))[0] + 1)
            for r in runs:
                if keep[r[0]] and len(r) > 3:
                    add_ring(resample(p[r], 2.5 if abs(lv) < 5 else 4.0, 0.2, 10.0 if abs(lv) < 5 else 16.0))
        else:
            add_ring(resample(p, 2.5 if abs(lv) < 5 else 4.0, 0.2, 10.0 if abs(lv) < 5 else 16.0))
n_outline = len(pts[0])
ring_pts = np.vstack(pts); edges = np.array(edges, np.int64)
# sparse free points far from every line
yy, xx = np.mgrid[8:H - 8:20, 8:W - 8:20]
far = (np.abs(s) > 16) & (o > 14)
free = np.c_[xx[far[yy, xx]], yy[far[yy, xx]]].astype(float)
allp = np.vstack([ring_pts, free])
print('ring points', len(ring_pts), 'free points', len(free), 'edges', len(edges))

# ---------- gem star ----------
star = {}
if gem.any():
    gs = ndi.gaussian_filter(sdf(gem), 1.5)
    ring = max(contours(gs, 0.0), key=len)
    xs_, ys_ = np.nonzero(gem.any(0))[0], np.nonzero(gem.any(1))[0]
    c = np.array([(xs_.min() + xs_.max()) / 2, (ys_.min() + ys_.max()) / 2])
    ang = np.arctan2(-(ring[:, 1] - c[1]), ring[:, 0] - c[0]); rad = np.hypot(*(ring - c).T)
    tips, corners = [], []
    for k in range(4):                                       # tips right, top, left, bottom; corners between
        a0 = k * np.pi / 2
        sel = np.abs(np.angle(np.exp(1j * (ang - a0)))) < np.pi / 4
        i = np.nonzero(sel)[0][np.argmax(rad[sel])]; tips.append(ring[i])
        a1 = a0 + np.pi / 4
        sel = np.abs(np.angle(np.exp(1j * (ang - a1)))) < np.pi / 4
        i = np.nonzero(sel)[0][np.argmin(rad[sel])]; corners.append(ring[i])
    star = dict(star_center=c, star_tips=np.array(tips), star_corners=np.array(corners),
                star_outline=resample(np.vstack([ring, ring[:1]]), 2.0, 0.12, 5.0))
    print('gem center', c.round(1), 'tips', np.array(tips).round(0).tolist())

# ---------- enamel colors: one smooth fit per cell ----------
lumc = img @ np.array([0.299, 0.587, 0.114])
cells = inside & (s <= 0) & ~gem
lab, n = ndi.label(cells)
from scipy.cluster.vq import kmeans2
base = np.stack([ndi.median_filter(img[..., k], size=9) for k in range(3)], -1)   # thin glints removed
col = np.zeros((H, W, 3))


def fit(ys, xs, sel_y, sel_x):
    u, v = (sel_x - xs.mean()) / 100.0, (sel_y - ys.mean()) / 100.0
    A = np.c_[np.ones_like(u), u, v, u * u, u * v, v * v]
    coef, *_ = np.linalg.lstsq(A, base[sel_y, sel_x], rcond=None)
    U, Vv = (xs - xs.mean()) / 100.0, (ys - ys.mean()) / 100.0
    return np.c_[np.ones_like(U), U, Vv, U * U, U * Vv, Vv * Vv] @ coef


for i in range(1, n + 1):
    m = lab == i; ys, xs = np.nonzero(m)
    if len(ys) < 600:
        col[ys, xs] = np.median(base[ys, xs], 0); continue
    X = base[ys, xs]; L = lumc[ys, xs]
    ok = L < np.percentile(L, 97)                              # leave out the brightest glare when choosing colors
    best = np.zeros(len(ys), int)
    for k in (4, 3, 2):                                        # split into color areas only when they truly differ
        cent, lb = kmeans2(X[ok], k, seed=1, minit='++')
        dist = np.linalg.norm(cent[:, None] - cent[None], axis=2) + np.eye(k)
        share = np.bincount(lb, minlength=k) / ok.sum()
        if dist.min() > 0.16 and share.min() > 0.06:
            best = np.argmin(np.linalg.norm(X[:, None] - cent[None], axis=2), 1); break
    lm = np.full((H, W), -1); lm[ys, xs] = best                 # tidy the area map: majority in a small window
    votes = np.stack([ndi.uniform_filter((lm == j).astype(float), 13) for j in range(best.max() + 1)], -1)
    best = np.argmax(votes[ys, xs], 1)
    for j in np.unique(best):
        sel = best == j
        core = sel & (L <= np.percentile(L[sel], 90))
        if core.sum() < 50:
            core = sel
        col[ys[sel], xs[sel]] = fit(ys[sel], xs[sel], ys[core], xs[core]) if sel.sum() > 400 else np.median(base[ys[core], xs[core]], 0)
col = np.clip(col, 0, 1)
fill = ndi.distance_transform_edt(~cells, return_distances=False, return_indices=True)
col = col[fill[0], fill[1]]                                 # spread under the walls and outside
cal = json.loads((Path(__file__).resolve().parent / 'calibration.json').read_text())
gain, off = np.array(cal['gain']), np.array(cal['offset'])
lv = np.r_[0.0, np.geomspace(0.003, 10.0, 72)]
L3 = np.stack(np.meshgrid(lv, lv, lv, indexing='ij'), -1).reshape(-1, 3)
shown = np.clip(agx(L3), 0, 1)
q = np.round(col * 63).astype(int); keys = q[..., 0] * 4096 + q[..., 1] * 64 + q[..., 2]
uniq, inv = np.unique(keys.ravel(), return_inverse=True)
pal = np.stack([uniq // 4096, (uniq // 64) % 64, uniq % 64], -1) / 63.0
_, nn = cKDTree(shown).query(pal)
alb = np.clip((L3[nn] - off) / gain, 0, 1); emi = np.clip(L3[nn] - off - gain * alb, 0, 1)
alb = alb[inv].reshape(col.shape); emi = emi[inv].reshape(col.shape)
mx, mn = col.max(2), col.min(2); white = ((mx - mn) / np.maximum(mx, 1e-6) < 0.25) & (col @ [0.299, 0.587, 0.114] > 0.55)
rough = np.where(white, 0.28, 0.12)
tw, th = 1024, int(round(1024 * H / W))
Image.fromarray(np.uint8(np.clip(alb ** (1 / 2.2), 0, 1) * 255)).resize((tw, th), Image.LANCZOS).save(OUT / 'textures/enamel_color.png')
Image.fromarray(np.uint8(emi * 255)).resize((tw, th), Image.BILINEAR).save(OUT / 'textures/enamel_glow.png')
Image.fromarray(np.uint8(rough * 255)).resize((tw, th), Image.BILINEAR).save(OUT / 'textures/enamel_rough.png')
np.save(OUT / 'predicted.npy', np.clip(agx(alb * gain + off + emi), 0, 1).astype(np.float16))

np.savez_compressed(OUT / 'prep.npz', pts=allp, edges=edges, n_ring=len(ring_pts), n_outline=n_outline, mockup=str(D / 'reference/mockup.png'), z=z.astype(np.float32),
                    gx=gx_.astype(np.float32), gy=gy_.astype(np.float32), s=s.astype(np.float32), o=o.astype(np.float32),
                    gem=gem, S=S, cx_px=cx_px, top_px=top_px, H=H, W=W, E0=E0, **star)
print('saved', OUT / 'prep.npz')
