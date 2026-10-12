"""solve2.py <out_name> [--refine <prev_name>] [--sigma S] [--knee K] [--slope Q]
Target: reference star colors per face (sampled inside each face, smoothed per face), highlights softly compressed above the knee.
Light per unit albedo from c00_calib (albedo 0.5). Albedo = min(1, target/light); emissive = the rest (max 1).
--refine: scale the total by target/observed measured in <prev_name>/app.png (smooth fit per face)."""
import sys, argparse, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from common import *
ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--refine'); ap.add_argument('--sigma', type=float, default=1.0)
ap.add_argument('--knee', type=float, default=0.78); ap.add_argument('--slope', type=float, default=0.6); ap.add_argument('--warm', type=float, default=1.0)
a = ap.parse_args()
from agx import agx, agx_inv, refine
def sample(img, x, y): return np.stack([map_coordinates(img[..., c], [y, x], order=1) for c in range(3)], -1)
def basis(u, v): return np.stack([u ** i * v ** j for i in range(4) for j in range(4 - i)], -1)
def smooth_fit(values, w1, w2, mask):
    cu = np.clip(w1, 0.02, 0.98); cv = np.clip(w2, 0.02, 0.98); s = cu + cv; over = s > 0.98
    cu = np.where(over, cu / s * 0.98, cu); cv = np.where(over, cv / s * 0.98, cv)
    B = basis(w1[mask], w2[mask]); Bf = basis(cu, cv); out = np.zeros(values.shape)
    for ch in range(3):
        coef, *_ = np.linalg.lstsq(B, np.log(np.maximum(values[mask][:, ch], 1e-6)), rcond=None); out[..., ch] = np.exp(Bf @ coef)
    return out
calib = np.asarray(Image.open(W / 'c00_calib/app.png').convert('RGB'), float) / 255
ref = np.asarray(Image.open(W / 'src/silver_reference.png').convert('RGB'), float) / 255
prev = np.asarray(Image.open(W / a.refine / 'app.png').convert('RGB'), float) / 255 if a.refine else None
prevtot = np.load(W / a.refine / 'total.npz')['planes'] if a.refine else None
alb_out = np.zeros((10, CELL, CELL, 3)); emi_out = np.zeros((10, CELL, CELL, 3)); tot_out = np.zeros((10, CELL, CELL, 3)); rep = []
for p in range(10):
    tri = TRIS[p]; wx, wy = cell_world(p); wz = plane_z(p, wx, wy); w0, w1, w2 = bary(tri[:, :2], wx, wy)
    scr = to_screen(np.stack([wx, wy, wz], -1).reshape(-1, 3)).reshape(CELL, CELL, 2); st = to_screen(tri); c = st.mean(0); ds = []
    for e0, e1 in [(st[0], st[1]), (st[1], st[2]), (st[2], st[0])]:
        e = e1 - e0; n = np.array([-e[1], e[0]]) / np.linalg.norm(e); ds.append(((scr - e0) @ n) * np.sign((c - e0) @ n))
    inner = np.min(ds, axis=0) >= 2.5
    obs = sample(calib, scr[..., 0] - .5, scr[..., 1] - .5)
    fitmask = inner & (obs.max(-1) < 0.96)
    light = smooth_fit(agx_inv(obs) / 0.5, w1, w2, fitmask)
    rtri = np.stack(world_to_ref(tri[:, 0], tri[:, 1]), -1)
    def height(k):
        q0, q1 = [rtri[i] for i in range(3) if i != k]; e = q1 - q0; n = np.array([-e[1], e[0]]) / np.linalg.norm(e); return abs((rtri[k] - q0) @ n)
    t0 = np.maximum(1 - w1 - w2, 3 / height(0)); t1 = np.maximum(w1, 4 / height(1)); t2 = np.maximum(w2, 4 / height(2)); ss = t0 + t1 + t2
    rq = (t0 / ss)[..., None] * rtri[0] + (t1 / ss)[..., None] * rtri[1] + (t2 / ss)[..., None] * rtri[2]
    tgt = sample(ref, rq[..., 0], rq[..., 1])
    if a.sigma > 0: tgt = np.stack([gaussian_filter(tgt[..., ch], a.sigma, mode='nearest') for ch in range(3)], -1)
    grey = tgt.mean(-1, keepdims=True); tgt = grey + (tgt - grey) * a.warm
    tgt = np.where(tgt > a.knee, a.knee + (tgt - a.knee) * a.slope, tgt)
    lin_t = refine(agx_inv(tgt), tgt)
    if a.refine:
        o = sample(prev, scr[..., 0] - .5, scr[..., 1] - .5); okm = inner & (o.max(-1) < 0.985)
        ratio = smooth_fit(lin_t / np.maximum(agx_inv(o), 1e-4), w1, w2, okm)
        total = prevtot[p] * ratio
    else:
        total = lin_t
    alb = np.clip(total / light, 0.005, 1.0)
    emi = np.clip(total - alb * light, 0, 1.0)
    alb_out[p], emi_out[p], tot_out[p] = alb, emi, total
    m = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
    rep.append(f'plane {p}: target display {np.round(tgt[m].mean(0) * 255).astype(int).tolist()} albedo {np.round(alb[m].mean(0), 2).tolist()} emissive {np.round(emi[m].mean(0), 2).tolist()} emissive maxed {float((total[m] - light[m] > 1).any(-1).mean()):.2f}')
out = W / a.out; out.mkdir(exist_ok=True)
np.savez(out / 'albedo.npz', planes=alb_out); np.savez(out / 'emissive.npz', planes=emi_out); np.savez(out / 'total.npz', planes=tot_out)
print('\n'.join(rep))
