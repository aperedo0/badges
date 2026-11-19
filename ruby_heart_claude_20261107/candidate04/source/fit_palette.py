"""Tune uniform ruby optics so the front view's tone mix matches reference2 (front).

Usage: fit_palette.py GEOM.npz START_OPTICS.json OUT_OPTICS.json
Only spatially constant optical constants change; geometry is fixed.
"""
import sys, json
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/tools')
import foilsim, screen_render as SR
from PIL import Image
from scipy.optimize import minimize

g = np.load(sys.argv[1]); prm0 = dict(foilsim.DEFAULT, **json.load(open(sys.argv[2]))['prm'])
V, N, T = g['gem_v'], g['gem_n'], g['gem_t']
# cache per pixel geometry of the front view (front crown only)
box = (300, 250, 906, 856)
x0, y0, x1, y1 = box; W, H = x1 - x0, y1 - y0
zbuf = np.full((H, W), np.inf); pid = np.full((H, W), -1)
P2, Z = SR.project(V)
for t, tri in enumerate(T):
    if N[tri[0], 2] <= 0: continue
    q = P2[tri]; zz = Z[tri]
    bx0, by0 = np.floor(q.min(0)).astype(int); bx1, by1 = np.ceil(q.max(0)).astype(int)
    ys, xs = np.mgrid[max(by0, y0):min(by1, y1 - 1) + 1, max(bx0, x0):min(bx1, x1 - 1) + 1]
    if ys.size == 0: continue
    px = xs + .5; py = ys + .5; a, b, c = q
    den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
    if abs(den) < 1e-9: continue
    w0 = ((b[1] - c[1]) * (px - c[0]) + (c[0] - b[0]) * (py - c[1])) / den
    w1 = ((c[1] - a[1]) * (px - c[0]) + (a[0] - c[0]) * (py - c[1])) / den
    inside = (w0 >= 0) & (w1 >= 0) & (1 - w0 - w1 >= 0)
    z = w0 * zz[0] + w1 * zz[1] + (1 - w0 - w1) * zz[2]
    upd = inside & (z < zbuf[ys - y0, xs - x0])
    zbuf[ys[upd] - y0, xs[upd] - x0] = z[upd]; pid[ys[upd] - y0, xs[upd] - x0] = t
m = pid >= 0; ys, xs = np.nonzero(m)
sel = np.arange(len(ys))[::3]
ys, xs = ys[sel], xs[sel]
dirs = foilsim.unit(SR.F[None] * SR.FOC + SR.RIGHT[None] * ((xs + x0 + .5) - SR.CX)[:, None] + SR.UP[None] * (SR.CY - (ys + y0 + .5))[:, None])
tri = T[pid[ys, xs]]; n = N[tri[:, 0]]; p0 = V[tri[:, 0]]
s = np.sum(n * (p0 - SR.EYE), 1) / np.sum(n * dirs, 1); P = SR.EYE + dirs * s[:, None]

ref = np.asarray(Image.open('/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/reference2/front.png').convert('RGB')).astype(float) / 255
h, w = ref.shape[:2]; yy, xx = np.mgrid[0:h, 0:w]
r_, g_, b_ = ref[..., 0], ref[..., 1], ref[..., 2]
rm = (((xx - w * 0.47) / (w * 0.26)) ** 2 + ((yy - h * 0.42) / (h * 0.32)) ** 2 < 1) & (r_ > g_ + 0.05) & (r_ > b_)
LW = np.array([0.2126, 0.7152, 0.0722])
def quantile_colors(px, k=20):
    o = np.argsort(px @ LW); px = px[o]
    return np.array([c.mean(0) for c in np.array_split(px, k)])
RQ = quantile_colors(ref[rm])

KEYS = ['aG', 'aB', 'exposure', 'glow', 'glowG', 'glowB', 'spec_gain', 'body_level', 'tent_gain', 'path_base']
def make(x):
    q = dict(prm0)
    q['absorption'] = (prm0['absorption'][0], x[0], x[1]); q['exposure'] = x[2]; q['glow'] = x[3]
    q['glow_color'] = (1.0, x[4], x[5]); q['spec_gain'] = x[6]; q['body_level'] = x[7]; q['tent_gain'] = x[8]; q['path_base'] = x[9]
    return q
BOUNDS = [(0.6, 5.0), (0.6, 5.0), (0.3, 2.2), (0.0, 0.4), (0.02, 0.4), (0.02, 0.35), (0.4, 2.2), (2.0, 4.5), (0.15, 1.5), (0.0, 1.5)]
def loss(x):
    x = np.clip(x, [b[0] for b in BOUNDS], [b[1] for b in BOUNDS])
    c = foilsim.display(foilsim.shade(P, n, dirs, make(x)))
    q_ = quantile_colors(c)
    def sat(a): return a.max(1) - a.min(1)
    lo = slice(0, 15)            # the red three quarters: match color and saturation
    reds = np.mean(np.sum((q_[lo] - RQ[lo]) ** 2, 1)) + 2.0 * np.mean((sat(q_[lo]) - sat(RQ[lo])) ** 2)
    hiL = q_[15:] @ LW; refL = RQ[15:] @ LW
    whites = np.mean(np.maximum(refL - hiL, 0) ** 2)   # brightest quarter at least as bright
    return float(reds + whites)

p = prm0
x0v = np.array([p['absorption'][1], p['absorption'][2], p['exposure'], p['glow'], p['glow_color'][1], p['glow_color'][2], p.get('spec_gain', 1), p['body_level'], p['tent_gain'], p.get('path_base', 0.6)])
print('start', round(loss(x0v), 5), flush=True)
best = minimize(loss, x0v, method='Nelder-Mead', options=dict(maxiter=500, xatol=1e-3, fatol=1e-6))
for s0 in (x0v * [1.3, 1.3, .8, 1.5, 1.5, 1.5, 1.2, 1, 1, 1.5], x0v * [.8, .9, 1.1, 2, 2, 2, 1.4, .9, 1.2, .5]):
    r = minimize(loss, s0, method='Nelder-Mead', options=dict(maxiter=500, xatol=1e-3, fatol=1e-6))
    if r.fun < best.fun: best = r
x = np.clip(best.x, [b[0] for b in BOUNDS], [b[1] for b in BOUNDS])
q = make(x); print('end', round(loss(x), 5), {k: round(float(v), 3) for k, v in zip(KEYS, x)})
c = foilsim.display(foilsim.shade(P, n, dirs, q))
print('sim quantiles (every 4th):', (quantile_colors(c)[::4] * 255).round().astype(int).tolist())
print('ref quantiles (every 4th):', (RQ[::4] * 255).round().astype(int).tolist())
json.dump({'prm': {k: (list(v) if isinstance(v, tuple) else v) for k, v in q.items()}}, open(sys.argv[3], 'w'), indent=1)
