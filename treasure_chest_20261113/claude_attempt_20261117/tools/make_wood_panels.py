"""Carved plank maps for every wood panel except the approved bottom front one.

Same look and settings as make_wood.py (which stays as the approved benchmark),
restructured so a panel can hold any number of planks. Row 0 of the arrays is
the bottom of the panel; images are flipped on save so UV v = 0 is the bottom.
Usage: python make_wood_panels.py maps [panel ...]
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from maps_common import (blur, fnoise, fnoise1, lin2srgb, ramp, sample,  # noqa: E402
                         smoothstep, to8, to16, write_png)

OUT = sys.argv[1] if len(sys.argv) > 1 else "maps"
ONLY = sys.argv[2:]
os.makedirs(OUT, exist_ok=True)
DEPTH = 0.08
T1 = fnoise((1024, 4096), 3.0, 150.0, 51)
T2 = fnoise((1024, 4096), 11.0, 320.0, 52)
STOPS = [(0.00, (0.010, 0.003, 0.0015)),
         (0.25, (0.045, 0.010, 0.0035)),
         (0.50, (0.150, 0.036, 0.009)),
         (0.72, (0.300, 0.085, 0.020)),
         (1.00, (0.500, 0.190, 0.055))]

# seams of the body, measured from the body bottom (z = -2.2175); they line up with the front
BODY_SEAMS = [0.9475, 1.3775, 1.7675, 2.1675]
BODY_H = 2.565
LID_ARC = 5.4276          # replaced by the builder's measured value when present
if os.path.exists(os.path.join(OUT, "lid_arc.json")):
    LID_ARC = json.load(open(os.path.join(OUT, "lid_arc.json")))["arc"]
_r = np.random.default_rng(5)
_w = _r.uniform(0.40, 0.50, 12)
LID_SEAMS = list(np.cumsum(_w / _w.sum() * LID_ARC)[:-1])

PANELS = {
    #  name          L       H        seams                                  W     HP    seed  bottom
    "front_upper": (5.0910, 1.1875, [0.39, 0.79],                          4096, 952, 300, "continue_gap"),
    "back":        (5.0910, BODY_H, BODY_SEAMS,                            2608, 1312, 400, "none"),
    "end_a":       (3.1900, BODY_H, BODY_SEAMS,                            1640, 1312, 500, "none"),
    "end_b":       (3.1900, BODY_H, BODY_SEAMS,                            1640, 1312, 600, "none"),
    "lid":         (5.1900, LID_ARC, LID_SEAMS,                            4096, 4288, 700, "none"),
    "cap_a":       (3.2000, 1.9000, [0.42, 0.84, 1.26, 1.68],              2048, 1216, 800, "none"),
    "cap_b":       (3.2000, 1.9000, [0.42, 0.84, 1.26, 1.68],              2048, 1216, 900, "none"),
}


def edge_profile(dist, x, L, W, PX, seed, chips):
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


def gap_profile(dist):
    return -0.060 * (1 - smoothstep(0.005, 0.014, dist))


def gen_panel(name, L, H, seams, W, HP, seed, bottom_mode):
    PX, PY = W / L, HP / H
    x = ((np.arange(W) + 0.5) / W * L).astype(np.float32)
    yfull = ((np.arange(HP) + 0.5) / HP * H).astype(np.float32)
    bounds = [0.0] + list(seams) + [H]
    nP = len(bounds) - 1
    lines = [np.zeros(W, np.float32)]
    for k in range(1, nP):
        lines.append((bounds[k] + 0.007 * fnoise1(W, 0.35 * PX, seed + 7 * k)).astype(np.float32))
    lines.append(np.full(W, H, np.float32))
    chips_n = max(2, int(round(L * 1.2)))

    h_full = np.zeros((HP, W), np.float32)
    t_full = np.zeros((HP, W), np.float32)
    hj_full = np.zeros((HP, W), np.float32)
    fib_full = np.zeros((HP, W), np.float32)
    dse_full = np.ones((HP, W), np.float32)

    for k in range(nP):
        sd = seed + 31 * (k + 1)
        r = np.random.default_rng(sd)
        y0, y1 = bounds[k], bounds[k + 1]
        ph = y1 - y0
        ra, rb = max(0, int((y0 - 0.03) * PY)), min(HP, int((y1 + 0.03) * PY) + 1)
        rows = rb - ra
        Y = np.broadcast_to(yfull[ra:rb][:, None], (rows, W))
        X = np.broadcast_to(x[None, :], (rows, W))
        COL = np.broadcast_to(np.arange(W), (rows, W))
        lo, hi = lines[k][None, :], lines[k + 1][None, :]
        mask = (Y >= lo) & (Y < hi)
        Yl = Y - y0

        def N(cx, cy, s):
            return fnoise((rows, W), cy * PY, cx * PX, sd + s)

        psi = (Yl + r.uniform(0.038, 0.050) * N(1.4, 0.5, 1) + 0.015 * N(0.41, 0.14, 2)
               + r.uniform(-0.014, 0.014) * (X - L / 2))
        kin = np.zeros((rows, W), np.float32)
        knot_h = np.zeros((rows, W), np.float32)
        ring_t = np.zeros((rows, W), np.float32)
        ringline = np.zeros((rows, W), np.float32)
        n_knots = int(r.random() < 0.30) + int(r.random() < 0.08)
        for _ in range(n_knots):
            xk = r.uniform(0.35, L - 0.35)
            yk = y0 + r.uniform(0.36, 0.64) * ph
            R = r.uniform(0.050, min(0.105, 0.25 * ph))
            ael = r.uniform(1.3, 1.6)
            rho2 = ((X - xk) / ael) ** 2 + (Y - yk) ** 2
            rho = np.sqrt(rho2)
            psi = psi - (Y - yk) * (R * R / np.maximum(rho2, R * R))
            ki = 1.0 - smoothstep(0.86 * R, 1.06 * R, rho)
            rr = np.clip(rho / R, 0, 1.2)
            rings = 0.5 - 0.5 * np.cos(2 * np.pi * (3.0 + 12 * R) * (rr + 0.05 * 0.18 * N(0.03, 0.03, 61)))
            kh = -0.007 - 0.0045 * rings + 0.004 * (1 - rr) ** 2
            th = np.deg2rad(r.uniform(-25, 25))
            dl = np.abs((X - xk) * np.cos(th) + (Y - yk) * np.sin(th))
            kh -= 0.030 * np.exp(-(dl / 0.0042) ** 2) * np.clip(1 - (rho / (0.92 * R)) ** 2, 0, 1) ** 0.6
            knot_h = knot_h * (1 - ki) + kh * ki
            ring_t = np.maximum(ring_t, ki * (0.6 + 0.8 * rings))
            kin = np.maximum(kin, ki)
            ringline += np.exp(-((rho - R) / 0.0055) ** 2)
        psi = psi + 0.0045 * N(0.5, 0.045, 3)

        # grain bands
        widths = np.clip(np.exp(r.normal(np.log(0.068), 0.45, 80)), 0.030, 0.150)
        bnd = -0.5 + np.concatenate([[0.0], np.cumsum(widths)])
        nb = len(bnd)
        idx = np.clip(np.searchsorted(bnd, psi) - 1, 1, nb - 3)
        b0 = bnd[idx]
        wd = (bnd[idx + 1] - b0).astype(np.float32)
        f = np.clip((psi - b0) / wd, 0.0, 1.0).astype(np.float32)
        base = r.uniform(0.4, 1.0, nb)
        base[r.random(nb) < 0.25] *= 0.3
        G = np.clip(0.5 + 0.95 * fnoise((nb, W), 0.0, 0.55 * PX, sd + 4), 0.0, 1.0) * base[:, None]
        D0, D1 = G[idx, COL], G[idx + 1, COL]

        def interp(v):
            up = v[idx] + (f - 0.5) * (v[idx + 1] - v[idx])
            dn = v[idx] + (f - 0.5) * (v[idx] - v[idx - 1])
            return np.where(f >= 0.5, up, dn).astype(np.float32)

        lift, tint, hue = interp(r.normal(0, 1, nb)), interp(r.normal(0, 1, nb)), interp(r.normal(0, 1, nb))
        P = 1.0 - np.abs(2 * f - 1) ** 2.2
        Dm = D0 * (1 - f) + D1 * f
        h = -0.026 * Dm * (1 - P) + 0.005 * lift + 0.008 * (f - 0.5) * Dm
        d0, d1 = f * wd, (1 - f) * wd
        h -= 0.013 * (D0 * np.exp(-(d0 / 0.0045) ** 2) + D1 * np.exp(-(d1 / 0.0045) ** 2))
        fib1 = sample(T1, psi * 800.0 + 37.0 * sd, X * 720.0 + 211.0 * sd)
        fib2 = sample(T2, psi * 720.0 + 91.0 * sd, X * 560.0 + 900.0 + 173.0 * sd)
        h += -0.0026 * np.abs(fib1) - 0.0022 * np.clip(fib2, -2, 2)
        h = h * (1 - kin) + knot_h * kin
        h -= 0.012 * np.clip(ringline, 0, 1)

        # cracks along the grain
        crack = np.zeros((rows, W), np.float32)
        cand = bnd[(bnd > 0.05) & (bnd < ph - 0.05)]
        specs = [(r.uniform(0.28, 0.85), r.uniform(0.0045, 0.008), r.uniform(0.030, 0.050))
                 for _ in range(max(2, int(L * 0.8)))]
        specs += [(r.uniform(0.07, 0.2), r.uniform(0.0028, 0.0045), r.uniform(0.016, 0.028))
                  for _ in range(int(L * 1.8))]
        if len(cand):
            for hl, wdt, dep in specs:
                pc, xc = r.choice(cand), r.uniform(0.3, L - 0.3)
                c0, c1 = max(0, int((xc - hl) * PX)), min(W, int((xc + hl) * PX) + 1)
                tp = np.clip(1 - ((x[c0:c1] - xc) / hl) ** 2, 0, 1)[None, :]
                dc = np.abs(psi[:, c0:c1] - pc)
                c = dep * tp ** 0.8 * np.exp(-(dc / (wdt * (0.35 + 0.65 * tp))) ** 2)
                np.maximum(crack[:, c0:c1], c, out=crack[:, c0:c1])
        h -= crack * (1 - kin)

        # plank edges and seam gaps
        db = np.maximum(Y - lo, 0.0)
        dt = np.maximum(hi - Y, 0.0)
        dse = np.full((rows, W), 1.0, np.float32)
        if k > 0:
            h += edge_profile(db, x, L, W, PX, sd + 5, chips_n) + gap_profile(db)
            dse = np.minimum(dse, db)
        elif bottom_mode == "continue_gap":
            h += edge_profile(db + 0.010, x, L, W, PX, sd + 5, chips_n) + gap_profile(db + 0.010)
            dse = np.minimum(dse, db + 0.010)
        if k < nP - 1:
            h += edge_profile(dt, x, L, W, PX, sd + 6, chips_n) + gap_profile(dt)
            dse = np.minimum(dse, dt)
        fp = np.clip((Y - lo) / np.maximum(hi - lo, 1e-3), 0, 1)
        h += -0.004 * (2 * fp - 1) ** 2 + 0.0025 * N(0.6, 0.25, 8)

        t = (0.485 + r.normal(0, 0.030) + 0.14 * tint + 0.30 * (P - 0.55) * (0.35 + Dm)
             + 0.050 * np.clip(fib2, -2, 2) - 0.055 * np.abs(fib1) + 0.085 * N(0.9, 0.3, 9))
        t -= 0.10 * ring_t
        hj = np.clip(hue + r.normal(0, 0.5), -2, 2)

        h_full[ra:rb][mask] = h[mask]
        t_full[ra:rb][mask] = t[mask]
        hj_full[ra:rb][mask] = hj[mask]
        fib_full[ra:rb][mask] = fib1[mask]
        dse_full[ra:rb][mask] = dse[mask]

    h = np.clip(np.minimum(h_full, 0.0045) - 0.0045, -DEPTH, 0.0)
    cav = np.clip((h - blur(h, 0.014 * PY, 0.014 * PX)) / 0.006, -1.5, 0.8)
    deep = np.clip(-(h + 0.016) / 0.030, 0, 1)
    t = t_full + 0.24 * cav - 0.06 * (1 - smoothstep(0.0, 0.05, dse_full))
    col = ramp(t, STOPS)
    col[..., 1] *= 1 + 0.07 * hj_full
    col[..., 2] *= 1 + 0.12 * hj_full
    col *= (1 - 0.80 * deep)[..., None]
    rough = np.clip(0.60 - 0.22 * (t - 0.5) + 0.25 * deep + 0.03 * fib_full, 0.36, 0.92)
    write_png(os.path.join(OUT, f"{name}_height16.png"), to16(1 + h[::-1] / DEPTH))
    write_png(os.path.join(OUT, f"{name}_albedo.png"), to8(lin2srgb(col[::-1])))
    write_png(os.path.join(OUT, f"{name}_rough.png"), to8(rough[::-1]))
    print("panel", name, W, HP, nP, "planks", float(h.min()), float(t.mean()))


for name, spec in PANELS.items():
    if not ONLY or name in ONLY:
        gen_panel(name, *spec)
json.dump({k: {"L": v[0], "H": v[1], "seams": [float(s) for s in v[2]]} for k, v in PANELS.items()},
          open(os.path.join(OUT, "wood_panels.json"), "w"), indent=1)
