"""solve3.py <out> --base B --s S --calib C --id I [--knee K --slope Q --star-sigma X --leaf-sigma Y --refine PREV]
Writes <out>/tex: star and leaf color + emissive atlases so the app shows the reference at rest.
Star: per face cells, light fitted smooth per face (as solve2). Leaves: per texel, rasterized in UV, light from the calib shot
inside the coverage mask (edges filled from the nearest covered pixel), target = reference at the same front position."""
import sys, argparse, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates, distance_transform_edt
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from common import *
from agx import agx, agx_inv, refine
ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--base', default='src/base106'); ap.add_argument('--s', type=float, default=1.06)
ap.add_argument('--calib', default='c10_calib'); ap.add_argument('--id', default='c11_id'); ap.add_argument('--knee', type=float, default=0.78); ap.add_argument('--slope', type=float, default=0.6)
ap.add_argument('--leaf-calib', default='c13_calib'); ap.add_argument('--leaf-a0', type=float, default=0.12); ap.add_argument('--star-sigma', type=float, default=1.0); ap.add_argument('--leaf-sigma', type=float, default=1.2); ap.add_argument('--refine')
a = ap.parse_args(); out = W / a.out; tex = out / 'tex'; tex.mkdir(parents=True, exist_ok=True); base = W / a.base
def img(p): return np.asarray(Image.open(p).convert('RGB'), float) / 255
def sample(im, x, y, order=1): return np.stack([map_coordinates(im[..., c], [y, x], order=order, mode='nearest') for c in range(3)], -1)
enc = lambda lin: np.uint8(np.clip(srgb_encode(lin), 0, 1) * 255 + .5)
calib, idimg, ref = img(W / a.calib / 'app.png'), img(W / a.id / 'app.png'), img(W / 'src/silver_reference.png')
prev = img(W / a.refine / 'app.png') if a.refine else None
def compress(t): return np.where(t > a.knee, a.knee + (t - a.knee) * a.slope, t)
# ---- screen light per unit albedo, valid only where the id shot is fully covered
light_screen = agx_inv(calib) / 0.5
def covered(channel, others):
    v = idimg[..., channel] - idimg[..., others].max(-1); top = np.percentile(v[v > 0.2], 95) if (v > 0.2).any() else 1
    return v > 0.85 * top
def filled(field, valid, maxd=6):
    d, (iy, ix) = distance_transform_edt(~valid, return_indices=True)
    return field[iy, ix], d <= maxd
leaf_mask = covered(1, [0, 2]); star_mask = covered(0, [1, 2])
def norm_blur(field, mask, sigma):
    m = gaussian_filter(mask.astype(float), sigma); return np.stack([gaussian_filter(field[..., c] * mask, sigma) for c in range(3)], -1) / np.maximum(m, 1e-6)[..., None], m
def smooth_extend(field, mask, small, large):
    near, _ = norm_blur(field, mask, small); far, _ = norm_blur(field, mask, large)
    w = np.clip(gaussian_filter(mask.astype(float), small * 1.5), 0, 1)[..., None]
    return np.where(mask[..., None], near, w * near + (1 - w) * far)
leaf_calib = img(W / a.leaf_calib / 'app.png'); leaf_lin = agx_inv(leaf_calib) / a.leaf_a0
leaf_valid = leaf_mask & (leaf_calib.max(-1) < 0.97)
leaf_light = smooth_extend(leaf_lin, leaf_valid, 0.7, 3.0)
leaf_near = distance_transform_edt(~leaf_mask) <= 6
# reference: only the leaves' inside (background and the outer rim line removed), extended smoothly past their edges
from scipy.ndimage import binary_erosion
ref_in = binary_erosion(ref.mean(-1) > 0.06, iterations=3)
ref_leaf = smooth_extend(ref, ref_in, max(a.leaf_sigma, 0.5), 6.0)
report = []
# ---- leaves
mesh = np.load(W / 'src/mesh33.npz'); P, UV, MAT = mesh['P'], mesh['UV'], mesh['MAT']
for mat in ['Silver2_LeafLit_Satin', 'Silver2_LeafShaded_Satin']:
    base_atlas = srgb_decode(np.asarray(Image.open(base / '0' / f'{mat}_color.png').convert('RGB'), float) / 255)
    pos = np.full((SIZE, SIZE, 3), np.nan); nz = np.zeros((SIZE, SIZE)); cover = np.zeros((SIZE, SIZE), bool)
    sel = np.where(MAT == mat)[0]
    for t in sel:
        tri = P[t]; uv = UV[t]; px = np.stack([uv[:, 0] * SIZE - .5, (1 - uv[:, 1]) * SIZE - .5], -1)
        n = np.cross(tri[1] - tri[0], tri[2] - tri[0]); nn = np.linalg.norm(n)
        if nn < 1e-12: continue
        x0, y0 = np.floor(px.min(0)).astype(int); x1, y1 = np.ceil(px.max(0)).astype(int)
        xs, ys = np.meshgrid(np.arange(max(x0, 0), min(x1, SIZE - 1) + 1), np.arange(max(y0, 0), min(y1, SIZE - 1) + 1))
        w0, w1, w2 = bary(px, xs, ys)
        inside = (w0 >= -1e-3) & (w1 >= -1e-3) & (w2 >= -1e-3)
        if not inside.any(): continue
        X, Y = xs[inside], ys[inside]
        pos[Y, X] = w0[inside, None] * tri[0] + w1[inside, None] * tri[1] + w2[inside, None] * tri[2]
        nz[Y, X] = n[2] / nn; cover[Y, X] = True
    solve = cover & (nz > 0.15)
    q = pos[solve]; scr = model_to_screen(q, a.s)
    L = sample(leaf_light, scr[:, 0] - .5, scr[:, 1] - .5); near = map_coordinates(leaf_near.astype(float), [scr[:, 1] - .5, scr[:, 0] - .5], order=0) > 0.5
    rx, ry = world_to_ref(q[:, 0], q[:, 1]); tgt = compress(sample(ref_leaf, rx, ry))
    lin_t = refine(agx_inv(tgt), tgt)
    if a.refine:
        prevtot = np.load(W / a.refine / f'{mat}_total.npy'); o = sample(prev, scr[:, 0] - .5, scr[:, 1] - .5)
        okp = map_coordinates(leaf_mask.astype(float), [scr[:, 1] - .5, scr[:, 0] - .5], order=0) > 0.5
        ratio = np.where(okp[:, None], lin_t / np.maximum(agx_inv(o), 1e-4), 1.0); total = prevtot * np.clip(ratio, 0.5, 2.0)
    else:
        total = lin_t
    alb = np.clip(total / np.maximum(L, 1e-4), 0.005, 1.0); emi = np.clip(total - alb * L, 0, 1.0)
    keep = ~near   # texels whose screen spot is not near the leaf coverage (hidden or off screen): keep the old color
    alb[keep] = base_atlas[solve][keep]; emi[keep] = 0
    color = base_atlas.copy(); color[solve] = alb; emis = np.zeros((SIZE, SIZE, 3)); emis[solve] = emi
    # fill unused texels from the nearest used texel so filtering never pulls in old colors at island borders
    _, (iy, ix) = distance_transform_edt(~cover, return_indices=True); color = color[iy, ix]; emis = emis[iy, ix]
    Image.fromarray(enc(color)).save(tex / f'{mat}_color.png'); Image.fromarray(enc(emis)).save(tex / f'{mat}_emissive.png')
    tot_full = total; np.save(out / f'{mat}_total.npy', tot_full)
    report.append(f'{mat}: solved texels {int(solve.sum())}, kept {int(keep.sum())}, albedo mean {np.round(alb.mean(0), 2).tolist()}, emissive mean {np.round(emi.mean(0), 2).tolist()}, emissive maxed {float(((total - L) > 1).any(-1).mean()):.2f}')
# ---- star (per face cells, smooth light fit per face)
def basis(u, v): return np.stack([u ** i * v ** j for i in range(4) for j in range(4 - i)], -1)
def smooth_fit(values, w1, w2, mask):
    cu = np.clip(w1, 0.02, 0.98); cv = np.clip(w2, 0.02, 0.98); s = cu + cv; over = s > 0.98
    cu = np.where(over, cu / s * 0.98, cu); cv = np.where(over, cv / s * 0.98, cv)
    B = basis(w1[mask], w2[mask]); Bf = basis(cu, cv); res = np.zeros(values.shape)
    for ch in range(3):
        coef, *_ = np.linalg.lstsq(B, np.log(np.maximum(values[mask][:, ch], 1e-6)), rcond=None); res[..., ch] = np.exp(Bf @ coef)
    return res
star_alb = {m: srgb_decode(np.asarray(Image.open(base / '0' / f'{m}_color.png').convert('RGB'), float) / 255) for m in ['Silver2_StarLit_Satin', 'Silver2_StarShaded_Satin']}
star_emi = {m: np.zeros((SIZE, SIZE, 3)) for m in star_alb}
prevstar = np.load(W / a.refine / 'star_total.npy') if a.refine else None; star_tot = np.zeros((10, CELL, CELL, 3))
for p in range(10):
    tri = TRIS[p]; wx, wy = cell_world(p); wz = plane_z(p, wx, wy); w0, w1, w2 = bary(tri[:, :2], wx, wy)
    scr = model_to_screen(np.stack([wx, wy, wz], -1).reshape(-1, 3), a.s).reshape(CELL, CELL, 2); st = model_to_screen(tri, a.s); c = st.mean(0); ds = []
    for e0, e1 in [(st[0], st[1]), (st[1], st[2]), (st[2], st[0])]:
        e = e1 - e0; n = np.array([-e[1], e[0]]) / np.linalg.norm(e); ds.append(((scr - e0) @ n) * np.sign((c - e0) @ n))
    inner = np.min(ds, axis=0) >= 2.5
    obs = sample(calib, scr[..., 0] - .5, scr[..., 1] - .5); light = smooth_fit(agx_inv(obs) / 0.5, w1, w2, inner & (obs.max(-1) < 0.96))
    rtri = np.stack(world_to_ref(tri[:, 0], tri[:, 1]), -1)
    def height(k):
        q0, q1 = [rtri[i] for i in range(3) if i != k]; e = q1 - q0; n = np.array([-e[1], e[0]]) / np.linalg.norm(e); return abs((rtri[k] - q0) @ n)
    t0 = np.maximum(1 - w1 - w2, 3 / height(0)); t1 = np.maximum(w1, 4 / height(1)); t2 = np.maximum(w2, 4 / height(2)); ss = t0 + t1 + t2
    rq = (t0 / ss)[..., None] * rtri[0] + (t1 / ss)[..., None] * rtri[1] + (t2 / ss)[..., None] * rtri[2]
    tgt = sample(ref, rq[..., 0], rq[..., 1])
    if a.star_sigma > 0: tgt = np.stack([gaussian_filter(tgt[..., ch], a.star_sigma, mode='nearest') for ch in range(3)], -1)
    tgt = compress(tgt); lin_t = refine(agx_inv(tgt), tgt)
    if a.refine:
        o = sample(prev, scr[..., 0] - .5, scr[..., 1] - .5); ratio = smooth_fit(lin_t / np.maximum(agx_inv(o), 1e-4), w1, w2, inner & (o.max(-1) < 0.985))
        total = prevstar[p] * ratio
    else:
        total = lin_t
    star_tot[p] = total
    alb = np.clip(total / light, 0.005, 1.0); emi = np.clip(total - alb * light, 0, 1.0); rs, cs = cell_slice(p)
    for m in star_alb: star_alb[m][rs, cs] = alb; star_emi[m][rs, cs] = emi
    msk = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
    report.append(f'star plane {p}: target {np.round(tgt[msk].mean(0) * 255).astype(int).tolist()} albedo {np.round(alb[msk].mean(0), 2).tolist()} emissive {np.round(emi[msk].mean(0), 2).tolist()}')
for m in star_alb:
    Image.fromarray(enc(star_alb[m])).save(tex / f'{m}_color.png'); Image.fromarray(enc(star_emi[m])).save(tex / f'{m}_emissive.png')
np.save(out / 'star_total.npy', star_tot)
print('\n'.join(report))
