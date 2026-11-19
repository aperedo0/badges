"""Fit vertex heights and ruby optics so each facet's tone matches the reference.

Only the shape and a few uniform optical constants are fitted; no picture is
painted on the gem. Writes trace/fit.json and preview images.
"""
import sys, json, time
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/tools')
import crown, facets, foilsim
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.optimize import differential_evolution, minimize

ROOT = '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107'
ref = np.asarray(Image.open(ROOT + '/reference.png').convert('RGB')).astype(float) / 255
names, XY, girdle, faces = crown.NAMES, crown.XY, crown.GIRDLE, crown.FACES
half = crown.HALF
free = [i for i in half if not girdle[i]]
ZG = 0.18

# Reference color per facet.
target, area = [], []
for f in faces:
    poly = [tuple(facets.to_ref(XY[i])) for i in f]
    m = Image.new('L', (ref.shape[1], ref.shape[0]), 0)
    ImageDraw.Draw(m).polygon(poly, fill=1)
    m = ndi.binary_erosion(np.asarray(m, bool), iterations=6)
    target.append(ref[m].mean(0)); area.append(m.sum())
target = np.array(target); area = np.array(area, float); wts = area / area.sum()

# Adjacent facet pairs (sharing an edge) for the contrast term.
_edges = {}
for fi, f in enumerate(faces):
    for a, b in zip(f, f[1:] + f[:1]):
        _edges.setdefault(tuple(sorted((a, b))), []).append(fi)
PAIRS = np.array([v for v in _edges.values() if len(v) == 2])
def _lab(c):
    L = c @ np.array([0.2126, 0.7152, 0.0722])
    return np.stack([L * 2.0, c[..., 0] - c[..., 1], (c[..., 2] - c[..., 1]) * 0.8], -1)
TLAB = _lab(target)

# Sample points inside each facet (centroid and points toward each vertex).
samples = []
for f in faces:
    q = XY[list(f)]; c = q.mean(0)
    samples.append(np.vstack([c, c + 0.55 * (q - c)]))

def unpack(x):
    k = len(free)
    zh = np.full(len(half), ZG)
    for j, i in enumerate(free):
        zh[half.index(i)] = x[j]
    a = np.array([x[k], x[k + 1], x[k + 2]])
    prm = dict(foilsim.DEFAULT, absorption=tuple(a), exposure=x[k + 3], tent_gain=x[k + 4], foil=0.92,
               body_level=x[k + 5], spec_clamp=x[k + 6], glow=x[k + 7], spec_gain=x[k + 8])
    return crown.full_heights(zh), prm

def facet_colors(z, prm, deg=0.0, want_facing=False):
    n, w, r = crown.planes(z)
    cols = []
    P, N, F = [], [], []
    for i, s in enumerate(samples):
        pz = (w[i] - n[i, 0] * s[:, 0] - n[i, 1] * s[:, 1]) / n[i, 2]
        P.append(np.c_[s, pz]); N.append(np.repeat(n[i][None], len(s), 0)); F += [i] * len(s)
    P = np.vstack(P); N = np.vstack(N); F = np.array(F)
    Pw = foilsim.yaw(P, deg)
    d = foilsim.yaw(foilsim.unit(Pw - foilsim.EYE), -deg)
    disp = foilsim.display(foilsim.shade(P, N, d, prm, deg))
    out = np.zeros((len(faces), 3))
    np.add.at(out, F, disp)
    out /= np.bincount(F)[:, None]
    if want_facing:
        nw = foilsim.yaw(n, deg); facing = -(nw @ foilsim.unit(-foilsim.EYE))
        return out, n, r, facing
    return out, n, r

TURNS = (-60, -35, -15, 15, 35, 60)
def turn_penalty(z, prm):
    pen = 0.0
    for deg in TURNS:
        c, _, _, facing = facet_colors(z, prm, deg, want_facing=True)
        vis = wts * (facing > 0.1)
        lum = c @ np.array([0.2126, 0.7152, 0.0722])
        dark = np.maximum(0.10 - lum, 0)            # no black facets
        white = np.maximum(c.min(1) - 0.80, 0)      # no pure white slabs
        hue = np.maximum(0.25 - (c[:, 0] - c[:, 1]), 0)  # stays clearly red
        pen += np.sum(vis * (4 * dark ** 2 + 2 * white ** 2 + 1 * hue ** 2))
    return pen / len(TURNS)

def loss(x):
    z, prm = unpack(x)
    cols, n, r = facet_colors(z, prm)
    err = np.sum(wts * np.sum((cols - target) ** 2, 1)) + turn_penalty(z, prm)
    L = _lab(cols)
    dsim = L[PAIRS[:, 0]] - L[PAIRS[:, 1]]; dref = TLAB[PAIRS[:, 0]] - TLAB[PAIRS[:, 1]]
    err += 0.5 * np.mean(np.sum((dsim - dref) ** 2, 1))
    if not np.isfinite(err): return 1e3
    tilt = np.degrees(np.arccos(np.clip(n[:, 2], -1, 1)))
    pen = 4.0 * np.sum(r ** 2) + 1e-3 * np.sum(np.maximum(tilt - 38, 0) ** 2) + 0.005 * np.mean((x[:k] - h0) ** 2)
    tot = err + pen
    return tot if np.isfinite(tot) else 1e3

k = len(free)
H0 = dict(B=.36, C=.30, D=.46, E=.46, H=.32, P1=.44, P2=.50, P3=.30, Q=.38, c1=.44, c2=.56, c3=.48, c4=.34)
h0 = np.array([H0[names[i]] for i in free])
bounds = [(ZG + 0.03, 0.72) for h in h0] + \
         [(0.1, 1.0), (4.0, 12.0), (0.8, 4.0), (0.3, 1.5), (0.2, 0.9), (3.8, 4.2), (3.0, 10.0), (0.0, 0.1), (0.2, 0.7)]
x_start = np.r_[h0, [0.15, 9.0, 2.2, 0.6, 0.6, 4.0, 8.0, 0.06, 0.4]]
if __name__ == '__main__':
    t0 = time.time()
    res = differential_evolution(loss, bounds, seed=int(sys.argv[1]) if len(sys.argv) > 1 else 1,
                                 popsize=8, maxiter=int(sys.argv[2]) if len(sys.argv) > 2 else 100,
                                 tol=1e-7, polish=False, workers=1, updating='immediate', x0=x_start)
    x = res.x
    res2 = minimize(loss, x, method='Powell', bounds=bounds, options=dict(maxiter=4000, xtol=1e-4, ftol=1e-7))
    x = res2.x if res2.fun < res.fun else x
    z, prm = unpack(x)
    cols, n, r = facet_colors(z, prm)
    out = dict(loss=float(loss(x)), color_rms=float(np.sqrt(np.sum(wts * np.mean((cols - target) ** 2, 1)))),
               heights={names[i]: float(z[i]) for i in half}, prm={k2: (list(v) if isinstance(v, tuple) else v) for k2, v in prm.items()},
               max_nonplanar=float(r.max()), max_tilt=float(np.degrees(np.arccos(n[:, 2])).max()), seconds=time.time() - t0)
    json.dump(out, open(sys.argv[3] if len(sys.argv) > 3 else ROOT + '/trace/fit.json', 'w'), indent=1)
    print(json.dumps(out, indent=1))
