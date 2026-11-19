"""Simple plank maps for the panels that hold several planks (back, ends, lid, lid caps).
Usage: python make_simple_panels.py OUTDIR [panel ...]
Each panel matches the size of the mesh panel already in the chest (see tools/build_wood.py).
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from maps_common import lin2srgb, to8, to16, write_png  # noqa: E402
from simple_wood import DEPTH, plank_arrays  # noqa: E402

OUT = sys.argv[1]
ONLY = sys.argv[2:]
MAPS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "maps")
ARC = json.load(open(os.path.join(MAPS, "lid_arc.json")))["arc"]
BODY = [dict(H=1.0405, VIS0=0.5035), dict(H=0.5370, LIP=True), dict(H=0.9875, VIS1=0.536, TOP=False, LIP=True)]
CAP = [dict(H=0.669, VIS0=0.35), dict(H=0.500, LIP=True), dict(H=0.731, TOP=False, LIP=True)]
n = 9
LID = []
for k in range(n):
    d = dict(H=ARC / n)
    if k < n // 2:
        d.update(LIP=k > 0, VIS0=0.30 if k == 0 else 0.0)                 # front half: tucks in toward the top
    elif k == n // 2:
        d.update(TOP=False, LIP=True, LIP_TOP=True, LAP_ON=False)        # the plank over the top
    else:
        d.update(FLIP=True, LIP=k < n - 1, VIS0=0.30 if k == n - 1 else 0.0)   # back half: mirrored
    LID.append(d)
PANELS = {  # name: (length, px per unit, seed, planks bottom to top)
    "back": (5.0910, 400.0, 100, BODY), "end_a": (3.1900, 400.0, 200, BODY), "end_b": (3.1900, 400.0, 300, BODY),
    "lid": (5.1900, 512.0, 400, LID), "cap_a": (3.2000, 448.0, 500, CAP), "cap_b": (3.2000, 448.0, 600, CAP),
}
rng = np.random.default_rng(3)
for name, (L, px, seed, planks) in PANELS.items():
    tones = rng.uniform(0.95, 1.06, len(planks))
    if ONLY and name not in ONLY:
        continue
    W = int(round(L * px / 16)) * 16
    hs, cs, rs = [], [], []
    for k, p in enumerate(planks):
        p = dict(p)
        flip = p.pop("FLIP", False)
        H = p.pop("H")
        h, c, r = plank_arrays(L, H, SEED=seed + 17 * k, TONE=float(tones[k]), PX=px, W=W, HP=int(round(H * px)), **p)
        if flip:
            h, c, r = h[::-1], c[::-1], r[::-1]
        hs.append(h); cs.append(c); rs.append(r)
    h, c, r = np.concatenate(hs), np.concatenate(cs), np.concatenate(rs)
    write_png(os.path.join(OUT, f"{name}_height16.png"), to16(1 + h[::-1] / DEPTH))
    write_png(os.path.join(OUT, f"{name}_albedo.png"), to8(lin2srgb(c[::-1])))
    write_png(os.path.join(OUT, f"{name}_rough.png"), to8(r[::-1]))
    print("simple panel", name, h.shape, len(planks), "planks")
