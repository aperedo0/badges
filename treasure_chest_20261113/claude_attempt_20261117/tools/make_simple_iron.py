"""Simple stylised iron for the lower rim: smooth grey, soft bevels, faint curvy marks, no chips.

Usage: python make_simple_iron.py OUTDIR
Texture u = distance along the rim (17.889 units), v = row across the profile.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from maps_common import fnoise, lin2srgb, smoothstep, to8, to16, write_png  # noqa: E402

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
A, BD, RC = 2.73, 1.78, 0.088
PERIM = 4 * (A + BD) - 8 * RC + 2 * np.pi * RC
ROWS = dict(top=46, tch=11, front=110, bch=11, bot=16)
R = sum(ROWS.values())
W, HP = 8192, 360
PXU = W / PERIM

# ---- look settings ------------------------------------------------------------
BASE = np.array([0.035, 0.032, 0.030], np.float32)   # smoky grey (linear)
CHAMFER = 0.036                                       # bevel size
MARKS = 0.17                                          # contrast of the faint curvy marks
EDGE_LIFT = 0.08                                      # bevels are a touch lighter
ROUGH, METAL = 0.55, 0.30
H_LO, H_HI = -0.004, 0.004

rowc = (np.arange(HP) + 0.5) / HP * R
r_top, r_tch = ROWS["top"], ROWS["top"] + ROWS["tch"]
r_front = r_tch + ROWS["front"]; r_bch = r_front + ROWS["bch"]
on_ch = (smoothstep(r_top - 1.0, r_top + 0.5, rowc) * (1 - smoothstep(r_tch - 0.5, r_tch + 1.0, rowc))
         + smoothstep(r_front - 1.0, r_front + 0.5, rowc) * (1 - smoothstep(r_bch - 0.5, r_bch + 1.0, rowc))).astype(np.float32)[:, None]


def NZ(c, seed):
    return fnoise((HP, W), c * PXU, c * PXU, seed)


# faint curvy marks: thin lines along the zero level of smooth noise
n1, n2 = NZ(0.055, 1), NZ(0.040, 2)
marks = np.exp(-(n1 / 0.10) ** 2) * smoothstep(-0.3, 0.6, NZ(0.12, 3)) + 0.7 * np.exp(-(n2 / 0.09) ** 2) * smoothstep(0.0, 0.9, NZ(0.15, 4))
marks = np.clip(marks, 0, 1) * (1 - on_ch)
cloud = np.clip(NZ(0.30, 5), -2, 2)
fine = fnoise((HP, W), 2.0, 2.0, 6)

tone = 1 + MARKS * marks + 0.05 * cloud + 0.015 * fine + EDGE_LIFT * on_ch
col = BASE[None, None, :] * tone[..., None]
rough = np.clip(ROUGH + 0.03 * cloud - 0.05 * marks - 0.06 * on_ch, 0.2, 0.9)
metal = np.full((HP, W), METAL, np.float32)
h = 0.0005 * marks + 0.00045 * cloud + 0.0001 * fine

write_png(os.path.join(OUT, "rim_height16.png"), to16((h[::-1] - H_LO) / (H_HI - H_LO)))
write_png(os.path.join(OUT, "rim_albedo.png"), to8(lin2srgb(col[::-1])))
write_png(os.path.join(OUT, "rim_rough.png"), to8(rough[::-1]))
write_png(os.path.join(OUT, "rim_metal.png"), to8(metal[::-1]))
leg = np.full(64, CHAMFER, np.float32)
np.savez(os.path.join(OUT, "rim_profile.npz"), at=leg, bt=leg, ab=leg, bb=leg, perim=PERIM,
         rows=np.array(list(ROWS.values())), h_lo=H_LO, h_hi=H_HI, A=A, BD=BD, RC=RC)
print("simple iron written")
