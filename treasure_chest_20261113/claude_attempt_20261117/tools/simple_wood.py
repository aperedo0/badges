"""Simple stylised planks: a smooth slab with soft edges, fine straight grain and real fibre detail.
plank_arrays() returns (height, colour, roughness) for one plank; row 0 is the bottom.
"""
import os

import numpy as np

from maps_common import blur, fnoise, fnoise1, sample, smoothstep

DEPTH = 0.06
SCANS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "simple", "scans")

# ---- look settings ------------------------------------------------------------
BASE = np.array([0.234, 0.043, 0.0095], np.float32)  # walnut red brown (linear)
EDGE_R, EDGE_D = 0.022, 0.010                         # soft top edge: width and drop
GAP_W, GAP_D = 0.006, 0.030                           # thin dark seam at the top edge
LIP_R, LIP_D = 0.014, 0.012                           # rounded bottom lip
LAP = 0.022                                           # how far the top tucks in under the plank above
GRAIN = 0.085                                         # colour contrast of the grain streaks
ROUGH = 0.55
SCAN = 0.085                                          # strength of the real wood fibre detail (scan)
SCAN_BUMP = 0.0010



def plank_arrays(L, H, SEED=1, VIS0=0.0, VIS1=None, TOP=True, LIP=False, TONE=1.0, PX=800.0, W=None, HP=None, LIP_TOP=False, LAP_ON=True):
    """TOP: seam and soft edge at the top (a neighbour overlaps it). LIP: rounded proud bottom edge.
    LIP_TOP: rounded proud top edge instead of a seam. LAP_ON: the top tucks in over VIS0..VIS1."""
    VIS1 = H if VIS1 is None else VIS1
    W = int(round(L * PX / 16)) * 16 if W is None else W
    HP = int(round(H * PX / 16)) * 16 if HP is None else HP
    x = ((np.arange(W) + 0.5) / W * L).astype(np.float32)
    y = ((np.arange(HP) + 0.5) / HP * H).astype(np.float32)
    X, Y = np.meshgrid(x, y)

    # grain: long thin streaks, almost straight
    G1 = fnoise((1024, 4096), 0.0045 * PX, 0.14 * PX, SEED + 1)
    G2 = fnoise((1024, 4096), 0.0018 * PX, 0.07 * PX, SEED + 2)
    wave = 0.010 * fnoise((HP, W), 0.25 * PX, 1.2 * PX, SEED + 3)
    g1 = sample(G1, (Y + wave) * PX + 131.0 * SEED, X * PX + 977.0 * SEED)
    g2 = sample(G2, (Y + wave) * PX + 300.0 + 57.0 * SEED, X * PX + 500.0 + 313.0 * SEED)
    broad = fnoise((HP, W), 0.07 * PX, 0.9 * PX, SEED + 4)

    h = 0.0006 * g1 + 0.0003 * g2 - 0.0014
    # real fibre detail from a free wood scan (Poly Haven Wood Cabinet Worn Long, CC0): fine lines only,
    # its broad bands and its colour are not used
    SC = SCANS
    fib = np.zeros_like(X)
    if os.path.exists(os.path.join(SC, "wood_diff.npy")):
        rs = np.random.default_rng(SEED + 99)
        def detail(name):
            a = np.load(os.path.join(SC, name)).T            # grain now runs along x
            a = a - blur(a, 28.0)
            if PX < 700:
                a = blur(a, 0.5 * 800.0 / PX)             # coarser maps: soften the scan so it does not alias
            return a / a.std()
        yy = Y * (2048 / 1.6) + rs.uniform(0, 2048)
        xx = X * (1024 / 1.7) + rs.uniform(0, 1024)
        fib = np.clip(sample(detail("wood_diff.npy"), yy, xx), -2.5, 2.5)
        h += SCAN_BUMP * np.clip(sample(detail("wood_disp.npy"), yy, xx), -3, 3)
    tone = 1 + GRAIN * np.clip(g1, -2.2, 2.2) + 0.035 * np.clip(g2, -2, 2) + 0.05 * np.clip(broad, -2, 2) + SCAN * fib
    # lapped planks: the top of this plank tucks in under the plank above (soft shadow under the seam)
    if LAP_ON:
        h += -LAP * np.clip((Y - VIS0) / max(VIS1 - VIS0, 1e-3), 0, 1) ** 1.5
    if TOP:
        dtop = np.maximum((H - Y) + 0.0025 * fnoise1(W, 0.4 * PX, SEED + 5)[None, :], 0.0)
        h += -EDGE_D * (1 - smoothstep(0.0, EDGE_R, dtop)) ** 2 - GAP_D * (1 - smoothstep(0.3 * GAP_W, GAP_W, dtop))
        tone *= 1 - 0.22 * (1 - smoothstep(0.0, 0.11, dtop))
    if LIP:
        dbot = np.maximum(Y + 0.002 * fnoise1(W, 0.4 * PX, SEED + 6)[None, :], 0.0)
        h += -LIP_D * (1 - smoothstep(0.0, LIP_R, dbot)) ** 2
    if LIP_TOP:
        dt2 = np.maximum((H - Y) + 0.002 * fnoise1(W, 0.4 * PX, SEED + 7)[None, :], 0.0)
        h += -LIP_D * (1 - smoothstep(0.0, LIP_R, dt2)) ** 2
    h = np.clip(h, -DEPTH, 0.0)
    tone = np.clip(tone * TONE, 0.4, 1.6)
    col = BASE[None, None, :] * np.stack([tone, tone ** 1.25, tone ** 1.45], axis=-1)
    rough = np.clip(ROUGH - 0.04 * g1 - 0.035 * fib, 0.3, 0.9)

    return h, col, rough
