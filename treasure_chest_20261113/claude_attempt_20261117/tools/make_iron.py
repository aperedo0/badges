"""Forged iron maps and chamfer profiles for the lower rim.

Texture u = distance along the rim perimeter (17.889 units), v = row across the
swept profile (top face, top chamfer, front face, bottom chamfer, bottom face).
Outputs: iron_height16.png, iron_albedo.png, iron_rough.png, iron_metal.png and
iron_profile.npz (chamfer legs along the perimeter, used by the mesh builder).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from maps_common import blur, fnoise, fnoise1, lin2srgb, smoothstep, to8, to16, write_png  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else "maps"
os.makedirs(OUT, exist_ok=True)

A, BD, RC = 2.73, 1.78, 0.088
PERIM = 4 * (A + BD) - 8 * RC + 2 * np.pi * RC
ROWS = dict(top=46, tch=11, front=110, bch=11, bot=16)
R = sum(ROWS.values())
W, HP = 16384, 720
PXU = W / PERIM                       # pixels per unit along the rim (about 916)
H_LO, H_HI = -0.020, 0.004           # height texture range in units
rng = np.random.default_rng(7)

rowc = (np.arange(HP) + 0.5) / HP * R            # row coordinate of every texture line
r_top, r_tch = ROWS["top"], ROWS["top"] + ROWS["tch"]
r_front = r_tch + ROWS["front"]
r_bch = r_front + ROWS["bch"]
ROWU = 0.004                                      # nominal units per row

# distance (units) from the nearest chamfer, 0 on the chamfers themselves
dist = np.where(rowc < r_top, (r_top - rowc) * ROWU,
        np.where(rowc < r_tch, 0.0,
        np.where(rowc < r_front, np.minimum(rowc - r_tch, r_front - rowc) * ROWU,
        np.where(rowc < r_bch, 0.0, (rowc - r_bch) * ROWU)))).astype(np.float32)
on_ch = (smoothstep(r_top - 1.0, r_top + 0.5, rowc) * (1 - smoothstep(r_tch - 0.5, r_tch + 1.0, rowc))
         + smoothstep(r_front - 1.0, r_front + 0.5, rowc) * (1 - smoothstep(r_bch - 0.5, r_bch + 1.0, rowc)))
on_ch = on_ch.astype(np.float32)[:, None]
DIST = dist[:, None]


def stamps(n, sy, sx, lo, hi, seed):
    r = np.random.default_rng(seed)
    img = np.zeros((HP, W), np.float32)
    np.add.at(img, (r.integers(0, HP, n), r.integers(0, W, n)), r.uniform(lo, hi, n).astype(np.float32))
    return blur(img, sy, sx) * (2 * np.pi * sy * sx)


def NZ(c_units, seed):
    return fnoise((HP, W), c_units * PXU, c_units * PXU, seed)


# ---- relief ------------------------------------------------------------------
dimple = (stamps(300, 0.034 * PXU, 0.040 * PXU, 0.0025, 0.0055, 1)
          + stamps(150, 0.058 * PXU, 0.066 * PXU, 0.0035, 0.0070, 2)
          + stamps(45, 0.095 * PXU, 0.110 * PXU, 0.0035, 0.0070, 3))


def pit_layer(n, sy, sx, lo, hi, seed):
    core = stamps(n, sy * PXU, sx * PXU, lo, hi, seed)
    lip = stamps(n, sy * PXU * 1.9, sx * PXU * 1.9, lo, hi, seed)
    return core, lip


pc1, pl1 = pit_layer(700, 0.0042, 0.0042, 0.005, 0.011, 11)
pc2, pl2 = pit_layer(260, 0.0030, 0.0120, 0.004, 0.009, 12)
pc3, pl3 = pit_layer(260, 0.0120, 0.0030, 0.004, 0.009, 13)
pit = pc1 + pc2 + pc3
lip = pl1 + pl2 + pl3
micro = 0.0002 * fnoise((HP, W), 2.0, 2.0, 21) + 0.0003 * fnoise((HP, W), 9.0, 9.0, 22)
low = 0.0025 * NZ(0.35, 23)
soft = 1 - 0.8 * on_ch
h = -1.3 * dimple + low + (-pit + 0.30 * lip + micro) * soft
h = np.clip(h, H_LO, H_HI)

# ---- wear, colour, roughness, metal -----------------------------------------
brk = NZ(0.03, 31)
mott = 0.6 * NZ(0.14, 32) + 0.4 * NZ(0.035, 33)
spill = np.clip(np.exp(-DIST / 0.006) * (0.55 + 0.75 * brk), 0, 1) * (DIST > 0)
cvx = np.clip((h - blur(h, 0.02 * PXU)) / 0.0022, 0, 1)
nick = np.clip(stamps(900, 1.6, 1.6, 0.5, 1.4, 41) + stamps(250, 1.3, 5.0, 0.5, 1.4, 42), 0, 1)
E = np.clip(on_ch * np.clip(0.75 + 0.3 * brk, 0.4, 1) + 0.35 * spill + 0.15 * cvx * (0.5 + 0.5 * brk) + 0.6 * nick, 0, 1)
pitm = np.clip(pit / 0.004, 0, 1) * soft
rust = smoothstep(0.9, 2.1, NZ(0.22, 34) + 0.5 * brk) * 0.15 + 0.25 * pitm

oxide = np.array([0.040, 0.042, 0.047], np.float32)
rustc = np.array([0.070, 0.042, 0.027], np.float32)
bare = np.array([0.42, 0.38, 0.33], np.float32)
col = oxide[None, None, :] * (1 + 0.30 * np.clip(mott, -2, 2))[..., None]
col = col * (1 - rust[..., None]) + rustc[None, None, :] * rust[..., None]
col *= (1 - 0.6 * pitm)[..., None]
Ew = (E ** 1.3)[..., None]
col = col * (1 - Ew) + bare[None, None, :] * (0.88 + 0.12 * np.clip(brk, -1, 1))[..., None] * Ew

dcen = np.clip(dimple / 0.006, 0, 1)
rough = 0.47 + 0.06 * np.clip(mott, -2, 2) - 0.10 * dcen + 0.25 * pitm + 0.10 * rust
rough = rough * (1 - E) + 0.36 * E
rough = np.clip(rough, 0.2, 0.95)
metal = np.clip(0.90 + 0.10 * E - 0.5 * pitm - 0.35 * rust, 0, 1)

write_png(os.path.join(OUT, "iron_height16.png"), to16((h[::-1] - H_LO) / (H_HI - H_LO)))
write_png(os.path.join(OUT, "iron_albedo.png"), to8(lin2srgb(col[::-1])))
write_png(os.path.join(OUT, "iron_rough.png"), to8(rough[::-1]))
write_png(os.path.join(OUT, "iron_metal.png"), to8(metal[::-1]))

# ---- chamfer legs along the perimeter (chipped edges) ------------------------
s = (np.arange(W) + 0.5) / W * PERIM


def edge_legs(seed):
    r = np.random.default_rng(seed)
    c = 0.022 + 0.004 * fnoise1(W, 0.5 * PXU, seed + 1)
    a = c * (1 + 0.20 * fnoise1(W, 0.3 * PXU, seed + 2))
    b = c * (1 + 0.20 * fnoise1(W, 0.3 * PXU, seed + 3))
    ca = np.zeros(W, np.float32)
    cb = np.zeros(W, np.float32)
    for _ in range(int(PERIM / 0.45)):
        sk, hw, e = r.uniform(0, PERIM), r.uniform(0.012, 0.050), r.uniform(0.008, 0.030)
        d = np.abs(s - sk)
        d = np.minimum(d, PERIM - d)
        shape = np.clip((hw - d) / (0.3 * hw + 0.004), 0, 1)
        np.maximum(ca, e * r.uniform(0.4, 1.2) * shape, out=ca)
        np.maximum(cb, e * r.uniform(0.4, 1.2) * shape, out=cb)
    return np.clip(a + ca, 0.009, 0.12).astype(np.float32), np.clip(b + cb, 0.009, 0.12).astype(np.float32)


at, bt = edge_legs(100)
ab, bb = edge_legs(200)
np.savez(os.path.join(OUT, "iron_profile.npz"), at=at, bt=bt, ab=ab, bb=bb, perim=PERIM,
         rows=np.array(list(ROWS.values())), h_lo=H_LO, h_hi=H_HI, A=A, BD=BD, RC=RC)
print("iron maps written", float(h.min()), float(h.max()), PERIM)
