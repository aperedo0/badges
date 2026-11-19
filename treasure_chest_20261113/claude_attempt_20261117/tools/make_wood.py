"""Carved plank maps for the bottom front wood region (two stacked planks).

Region: 5.091 units long (along the chest front) by 1.3608 tall. Row 0 of the
arrays is the bottom; images are flipped on save so UV v = 0 is the bottom.
Outputs: wood_height16.png (1 = surface, carved inward over DEPTH units),
wood_albedo.png, wood_rough.png.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from maps_common import (blur, fnoise, fnoise1, lin2srgb, ramp, sample,  # noqa: E402
                         smoothstep, to8, to16, write_png)

OUT = sys.argv[1] if len(sys.argv) > 1 else "maps"
os.makedirs(OUT, exist_ok=True)

L, HH = 5.0910, 1.3608
W, HP = 4096, 1088
DEPTH = 0.08          # height texture range in scene units
SEAM = 0.93           # plank seam height in the region
PX = W / L            # pixels per unit (about 804)
rng = np.random.default_rng(71)

x = (np.arange(W) + 0.5) / W * L
y = (np.arange(HP) + 0.5) / HP * HH
X, Y = np.meshgrid(x.astype(np.float32), y.astype(np.float32))
COL = np.broadcast_to(np.arange(W), (HP, W))


def N(cx, cy, seed):
    return fnoise((HP, W), cy * PX, cx * PX, seed)


ys = SEAM + 0.007 * fnoise1(W, 0.35 * PX, 5)          # seam line, slightly wavy
lower = Y < ys[None, :]

# ---- grain flow coordinate per plank -------------------------------------
KNOT = (1.36, 0.705, 0.100, 1.45)                      # x, y, radius, elongation
xk, yk, R, ael = KNOT
rho2 = ((X - xk) / ael) ** 2 + (Y - yk) ** 2
rho = np.sqrt(rho2)
q = R * R / np.maximum(rho2, R * R)

psi_lo = (Y + 0.048 * N(1.5, 0.5, 11) + 0.015 * N(0.42, 0.14, 12)
          - 0.010 * (X - L / 2) - (Y - yk) * q)
psi_up = (Y + 0.044 * N(1.3, 0.5, 21) + 0.016 * N(0.40, 0.14, 22)
          + 0.014 * (X - L / 2))
psi = np.where(lower, psi_lo, psi_up)
psi = psi + 0.0045 * np.where(lower, N(0.5, 0.045, 13), N(0.5, 0.045, 23))


def bands(psi, seed):
    """Variable width grain bands along the flow coordinate."""
    r = np.random.default_rng(seed)
    widths = np.clip(np.exp(r.normal(np.log(0.068), 0.45, 80)), 0.030, 0.150)
    bounds = -0.5 + np.concatenate([[0.0], np.cumsum(widths)])
    nb = len(bounds)
    idx = np.clip(np.searchsorted(bounds, psi) - 1, 1, nb - 3)
    b0 = bounds[idx]
    wd = bounds[idx + 1] - b0
    f = np.clip((psi - b0) / wd, 0.0, 1.0).astype(np.float32)
    base = r.uniform(0.4, 1.0, nb)
    base[r.random(nb) < 0.25] *= 0.3
    G = np.clip(0.5 + 0.95 * fnoise((nb, W), 0.0, 0.55 * PX, seed + 1), 0.0, 1.0) * base[:, None]
    D0 = G[idx, COL]
    D1 = G[idx + 1, COL]
    lift = r.normal(0.0, 1.0, nb)
    tint = r.normal(0.0, 1.0, nb)
    hue = r.normal(0.0, 1.0, nb)

    def interp(v):
        up = v[idx] + (f - 0.5) * (v[idx + 1] - v[idx])
        dn = v[idx] + (f - 0.5) * (v[idx] - v[idx - 1])
        return np.where(f >= 0.5, up, dn).astype(np.float32)

    return dict(bounds=bounds, idx=idx, f=f, wd=wd.astype(np.float32), D0=D0, D1=D1,
                lift=interp(lift), tint=interp(tint), hue=interp(hue))


Blo = bands(psi_lo + (psi - np.where(lower, psi_lo, psi_up)), 31)
Bup = bands(psi, 41)
B = {k: np.where(lower, Blo[k], Bup[k]) for k in ("f", "wd", "D0", "D1", "lift", "tint", "hue")}
f, wd, D0, D1 = B["f"], B["wd"], B["D0"], B["D1"]

P = 1.0 - np.abs(2 * f - 1) ** 2.2                      # rounded ridge profile
Dm = D0 * (1 - f) + D1 * f
h = -0.026 * Dm * (1 - P) + 0.005 * B["lift"]
h += 0.008 * (f - 0.5) * Dm                             # slight shingle tilt
d0 = f * wd
d1 = (1 - f) * wd
groove = D0 * np.exp(-(d0 / 0.0045) ** 2) + D1 * np.exp(-(d1 / 0.0045) ** 2)
h -= 0.013 * groove

# ---- fibers that follow the flow -----------------------------------------
T1 = fnoise((1024, 4096), 3.0, 150.0, 51)
T2 = fnoise((1024, 4096), 11.0, 320.0, 52)
fib1 = sample(T1, psi * PX, X * PX * 0.9)
fib2 = sample(T2, psi * PX * 0.9, X * PX * 0.7 + 900.0)
h += -0.0026 * np.abs(fib1) - 0.0022 * np.clip(fib2, -2, 2)

# ---- knot -----------------------------------------------------------------
kin = 1.0 - smoothstep(0.86 * R, 1.06 * R, rho)
rr = np.clip(rho / R, 0, 1.2)
ang_n = 0.18 * fnoise((HP, W), 0.03 * PX, 0.03 * PX, 61)
rings = 0.5 - 0.5 * np.cos(2 * np.pi * 4.2 * (rr + 0.05 * ang_n))
knot_h = -0.007 - 0.0045 * rings + 0.004 * (1 - rr) ** 2
th = np.deg2rad(8.0)
dl = np.abs((X - xk) * np.cos(th) + (Y - yk) * np.sin(th))
knot_h -= 0.030 * np.exp(-(dl / 0.0042) ** 2) * np.clip(1 - (rho / (0.92 * R)) ** 2, 0, 1) ** 0.6
h = h * (1 - kin) + knot_h * kin
h -= 0.012 * np.exp(-((rho - R) / 0.0055) ** 2)        # dark ring around the knot

# ---- cracks along the grain ----------------------------------------------
crack = np.zeros_like(h)


def add_cracks(Bd, mask, seed, n_long, n_short, vis_psi):
    r = np.random.default_rng(seed)
    bnd = Bd["bounds"]
    cand = bnd[(bnd > vis_psi[0] + 0.05) & (bnd < vis_psi[1] - 0.05)]
    specs = [(r.uniform(0.28, 0.85), r.uniform(0.0045, 0.008), r.uniform(0.030, 0.050)) for _ in range(n_long)]
    specs += [(r.uniform(0.07, 0.2), r.uniform(0.0028, 0.0045), r.uniform(0.016, 0.028)) for _ in range(n_short)]
    for hl, wdt, dep in specs:
        pc = r.choice(cand)
        xc = r.choice([r.uniform(0.45, 2.15), r.uniform(2.95, 4.6)])
        tp = np.clip(1 - ((X - xc) / hl) ** 2, 0, 1)
        dc = np.abs(psi - pc)
        c = dep * tp ** 0.8 * np.exp(-(dc / (wdt * (0.35 + 0.65 * tp))) ** 2)
        np.maximum(crack, c * mask, out=crack)


add_cracks(Blo, lower, 91, 4, 9, (0.50, SEAM))
add_cracks(Bup, ~lower, 92, 4, 9, (SEAM, HH))
crack *= (1 - kin)
h -= crack

# ---- plank edges, chips and the seam gap ---------------------------------


def edge_profile(dist, seed, chips):
    """Rounded, chipped plank edge; dist = distance from the seam line."""
    r = np.random.default_rng(seed)
    ew = 0.042 + 0.014 * np.clip(fnoise1(W, 0.25 * PX, seed + 3), -1, 2)
    dp = np.full(W, 0.028, np.float32)
    for _ in range(chips):
        xc, hw = r.uniform(0.3, L - 0.3), r.uniform(0.07, 0.22)
        bump = smoothstep(0.0, 0.35, np.clip(1 - np.abs(x - xc) / hw, 0, 1))
        ew = ew + r.uniform(0.012, 0.03) * bump
        dp = dp + r.uniform(0.006, 0.02) * bump
    t = 1 - smoothstep(0.0, 1.0, dist / ew[None, :])
    return -dp[None, :] * t ** 1.6


dseam = np.abs(Y - ys[None, :])
edge = np.where(lower, edge_profile(dseam, 101, 6), edge_profile(dseam, 102, 6))
dtop = HH - Y
edge += np.where(lower, 0.0, edge_profile(np.abs(dtop - 0.010), 103, 6))
gap = -0.060 * (1 - smoothstep(0.005, 0.014, dseam)) - 0.060 * (1 - smoothstep(0.003, 0.009, np.abs(dtop - 0.010)))
# cupping: each plank is a touch lower toward its long edges
fp = np.where(lower, Y / ys[None, :], (Y - ys[None, :]) / (HH - ys[None, :]))
cup = -0.004 * (2 * fp - 1) ** 2

h = h + edge + cup + 0.0025 * N(0.6, 0.25, 71)
h = np.minimum(h, 0.0045) - 0.0045
h = h + gap
h = np.clip(h, -DEPTH, 0.0)

# ---- colour ----------------------------------------------------------------
cav = np.clip((h - blur(h, 0.014 * PX)) / 0.006, -1.5, 0.8)
deep = np.clip(-(h + 0.016) / 0.030, 0, 1)
blot = N(0.9, 0.3, 81)
t = (0.485 + 0.14 * B["tint"] + 0.30 * (P - 0.55) * (0.35 + Dm) + 0.050 * np.clip(fib2, -2, 2)
     - 0.055 * np.abs(fib1) + 0.085 * blot + 0.24 * cav)
t -= 0.10 * kin * (0.6 + 0.8 * rings)
t -= 0.06 * (1 - smoothstep(0.0, 0.05, dseam))
stops = [(0.00, (0.010, 0.003, 0.0015)),
         (0.25, (0.045, 0.010, 0.0035)),
         (0.50, (0.150, 0.036, 0.009)),
         (0.72, (0.300, 0.085, 0.020)),
         (1.00, (0.500, 0.190, 0.055))]
col = ramp(t, stops)
hj = np.clip(B["hue"], -2, 2)
col[..., 1] *= 1 + 0.07 * hj
col[..., 2] *= 1 + 0.12 * hj
col *= (1 - 0.80 * deep)[..., None]

rough = np.clip(0.60 - 0.22 * (t - 0.5) + 0.25 * deep + 0.03 * fib1, 0.36, 0.92)

write_png(os.path.join(OUT, "wood_height16.png"), to16(1 + h[::-1] / DEPTH))
write_png(os.path.join(OUT, "wood_albedo.png"), to8(lin2srgb(col[::-1])))
write_png(os.path.join(OUT, "wood_rough.png"), to8(rough[::-1]))
print("wood maps written", h.min(), h.max(), float(t.mean()))
