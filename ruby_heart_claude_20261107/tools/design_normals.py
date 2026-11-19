"""Choose each facet's tilt from the tone it shows under the app light, then solve heights.

Usage: design_normals.py OPTICS.json OUT_FIT.json [rounds]
Alternates: (1) per facet, search normals near the current one for the best
match to the reference facet tone; (2) least squares heights realizing those
normals (girdle fixed, mirror symmetric); (3) small optics refinement.
"""
import sys, json
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/tools')
import crown, foilsim
import fit_crown as F
from scipy.optimize import minimize

names, XY, girdle, faces = crown.NAMES, crown.XY, crown.GIRDLE, crown.FACES
half = crown.HALF; free = F.free; ZG = F.ZG
prm = dict(foilsim.DEFAULT, **json.load(open(sys.argv[1]))['prm']); prm['absorption'] = tuple(prm['absorption'])
rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 6
target = F.target; wts = F.wts

def lab(c):
    # rough perceptual weighting in display space: luminance and two chroma axes
    L = c @ np.array([0.2126, 0.7152, 0.0722])
    return np.stack([L * 2.0, (c[..., 0] - c[..., 1]), (c[..., 2] - c[..., 1]) * 0.8], -1)

# candidate normals: tilt 0..42 deg, azimuth every 7.5 deg
tilts = np.radians(np.arange(0, 43, 2.0)); azs = np.radians(np.arange(0, 360, 7.5))
TT, AA = np.meshgrid(tilts, azs)
CAND = np.stack([np.sin(TT) * np.cos(AA), np.sin(TT) * np.sin(AA), np.cos(TT)], -1).reshape(-1, 3)
CAND = np.unique(np.round(CAND, 6), axis=0)

def facet_points(z):
    n, w, _ = crown.planes(z)
    cents = []
    for i, f in enumerate(faces):
        c = XY[list(f)].mean(0)
        cents.append([c[0], c[1], (w[i] - n[i, 0] * c[0] - n[i, 1] * c[1]) / n[i, 2]])
    return np.array(cents), n

def solve_heights(nt, z_prev, lam=0.05):
    """Least squares heights so each facet's edges follow its target normal."""
    idx = {i: j for j, i in enumerate(free)}
    rows, rhs = [], []
    nf = len(free)
    def var(v):
        # full index -> (free column or None, fixed value)
        base = names.index(names[v][:-1]) if names[v].endswith("'") else v
        return (idx.get(base), ZG if girdle[v] else None)
    for fi, f in enumerate(faces):
        gx, gy = -nt[fi, 0] / nt[fi, 2], -nt[fi, 1] / nt[fi, 2]
        for a, b in zip(f, f[1:] + f[:1]):
            dz = gx * (XY[b, 0] - XY[a, 0]) + gy * (XY[b, 1] - XY[a, 1])
            row = np.zeros(nf); r = dz
            for v, s in ((b, 1), (a, -1)):
                col, fixed = var(v)
                if col is None: r -= s * (fixed if fixed is not None else 0)
                else: row[col] += s
            rows.append(row * np.sqrt(wts[fi] * len(faces))); rhs.append(r * np.sqrt(wts[fi] * len(faces)))
    for j, v in enumerate(free):
        row = np.zeros(nf); row[j] = lam; rows.append(row); rhs.append(lam * z_prev[v])
    sol = np.linalg.lstsq(np.array(rows), np.array(rhs), rcond=None)[0]
    zh = np.array([ZG if girdle[i] else float(np.clip(sol[idx[i]], ZG + 0.03, 0.85)) for i in half])
    return crown.full_heights(zh)

H0 = dict(B=.36, C=.30, D=.46, E=.46, H=.32, P1=.44, P2=.50, P3=.30, Q=.38, c1=.44, c2=.62, c3=.48, c4=.34)
z = crown.full_heights(np.array([ZG if girdle[i] else H0[names[i]] for i in half]))
radius = np.radians(30)
for it in range(rounds):
    cents, ncur = facet_points(z)
    chosen = []
    for fi in range(len(faces)):
        near = CAND[np.arccos(np.clip(CAND @ ncur[fi], -1, 1)) < radius]
        p = np.repeat(cents[fi][None], len(near), 0)
        d = foilsim.unit(p - foilsim.EYE)
        col = foilsim.display(foilsim.shade(p, near, d, prm))
        cost = np.sum((lab(col) - lab(target[fi])) ** 2, 1) + 0.02 * np.sum((near - ncur[fi]) ** 2, 1)
        chosen.append(near[np.argmin(cost)])
    chosen = np.array(chosen)
    z = solve_heights(chosen, z)
    cols, nreal, res = F.facet_colors(z, prm)
    err = np.sqrt(np.sum(wts * np.mean((cols - target) ** 2, 1)))
    print(f'round {it}: rms {err:.4f} max nonplanar {res.max():.3f} max tilt {np.degrees(np.arccos(nreal[:, 2])).max():.1f}', flush=True)
    radius = max(np.radians(10), radius * 0.8)

def opt_loss(x):
    q = dict(prm, absorption=(x[0], x[1], x[2]), exposure=x[3], tent_gain=x[4], glow=x[5])
    cols, _, _ = F.facet_colors(z, q)
    return np.sum(wts * np.sum((cols - target) ** 2, 1)) + F.turn_penalty(z, q)
x0 = np.r_[prm['absorption'], prm['exposure'], prm['tent_gain'], prm['glow']]
r = minimize(opt_loss, x0, method='Powell', bounds=[(0.05, 1), (4, 12), (0.8, 4), (0.3, 1.5), (0.2, 1.0), (0.0, 0.12)], options=dict(maxiter=600))
prm.update(absorption=tuple(r.x[:3]), exposure=r.x[3], tent_gain=r.x[4], glow=r.x[5])
cols, nreal, res = F.facet_colors(z, prm)
err = np.sqrt(np.sum(wts * np.mean((cols - target) ** 2, 1)))
print('after optics refinement rms', round(err, 4))
out = dict(color_rms=float(err), heights={names[i]: float(z[i]) for i in half},
           prm={k: (list(v) if isinstance(v, tuple) else v) for k, v in prm.items()},
           max_nonplanar=float(res.max()), max_tilt=float(np.degrees(np.arccos(nreal[:, 2])).max()))
json.dump(out, open(sys.argv[2], 'w'), indent=1)
print(json.dumps({k: round(v, 3) for k, v in out['heights'].items() if not k.startswith('g')}))
print(json.dumps({k: v for k, v in out['prm'].items()}))
