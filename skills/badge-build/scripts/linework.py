"""Clean line work from a traced mask: centerline, pruned spurs, smoothed width, redrawn as an even stroke. Python 3.11.

Traced gold lines come out lumpy: shading beside a line moves the traced edge, so widths wander and spirals read as
beaks (Mountain Sunburst cand06, Golden Storm plan check). This thins a line mask to its centerline (Zhang and Suen),
removes spurs, takes the width along the centerline from the distance to the mask's edge, smooths that width over a
stretch of the line, and redraws every centerline pixel as a disk of the smoothed radius. Use it on gold line masks
(spirals, outline rings, hooks) before turning them into pieces.

    from linework import regularize
    clean = regularize(mask, smooth_px=14, min_radius=4, prune_px=10)
"""
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree


def _neighbors(P):
    return [P[:-2, 1:-1], P[:-2, 2:], P[1:-1, 2:], P[2:, 2:], P[2:, 1:-1], P[2:, :-2], P[1:-1, :-2], P[:-2, :-2]]


def thin(mask):
    """Zhang and Suen thinning: a one pixel centerline."""
    img = mask.astype(np.uint8).copy()
    while True:
        changed = False
        for step in (0, 1):
            P = np.pad(img, 1); p2, p3, p4, p5, p6, p7, p8, p9 = _neighbors(P)
            B = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
            seq = [p2, p3, p4, p5, p6, p7, p8, p9, p2]
            A = sum(((seq[i] == 0) & (seq[i + 1] == 1)).astype(np.uint8) for i in range(8))
            c1 = p2 * p4 * p6 if step == 0 else p2 * p4 * p8
            c2 = p4 * p6 * p8 if step == 0 else p2 * p6 * p8
            m = (img == 1) & (B >= 2) & (B <= 6) & (A == 1) & (c1 == 0) & (c2 == 0)
            if m.any():
                img[m] = 0; changed = True
        if not changed:
            return img.astype(bool)


def _endpoints(S):
    n = ndi.convolve(S.astype(np.uint8), np.ones((3, 3), np.uint8), mode='constant') - S
    return S & (n == 1)


def prune(skel, n):
    """Remove spurs up to n pixels long, then regrow the main branches' ends."""
    S = skel.copy()
    for _ in range(n):
        S &= ~_endpoints(S)
    for _ in range(n):
        S |= ndi.binary_dilation(_endpoints(S), structure=np.ones((3, 3))) & skel
    return S


def regularize(mask, smooth_px=14, min_radius=4.0, prune_px=10, max_radius=None):
    """The mask's line work redrawn as even strokes: centerline disks of the width smoothed along the line."""
    mask = mask.astype(bool)
    dt = ndi.distance_transform_edt(mask)
    S = prune(thin(mask), prune_px)
    ys, xs = np.nonzero(S)
    if len(xs) == 0:
        return np.zeros_like(mask)
    pts = np.c_[xs, ys].astype(float); r = dt[ys, xs]
    tree = cKDTree(pts)
    # width smoothed over a stretch of the line: the median radius of centerline pixels within smooth_px
    rs = np.array([np.median(r[idx]) for idx in tree.query_ball_point(pts, smooth_px)])
    rs = np.maximum(rs, min_radius)
    if max_radius:
        rs = np.minimum(rs, max_radius)
    R = float(rs.max()) + 1
    out = np.zeros_like(mask)
    y0, x0 = max(int(ys.min() - R), 0), max(int(xs.min() - R), 0)
    y1, x1 = min(int(ys.max() + R + 1), mask.shape[0]), min(int(xs.max() + R + 1), mask.shape[1])
    gy, gx = np.mgrid[y0:y1, x0:x1]; cand = np.c_[gx.ravel(), gy.ravel()].astype(float)
    near = ndi.distance_transform_edt(~S[y0:y1, x0:x1]).ravel() <= R
    q = cand[near]
    hit = np.zeros(len(q), bool)
    for i, idx in enumerate(tree.query_ball_point(q, R)):
        if idx:
            d = np.hypot(pts[idx, 0] - q[i, 0], pts[idx, 1] - q[i, 1])
            hit[i] = bool((d <= rs[idx]).any())
    flat = np.zeros(len(cand), bool); flat[np.nonzero(near)[0][hit]] = True
    out[y0:y1, x0:x1] = flat.reshape(gy.shape)
    return out
