"""Emerald Stag v2: frame, base, rock, moss, leaves, flowers, buds and emeralds (model units).

Usage: stag_parts.py OUT.npz
Model: Y up, front +Z. Mockup pixels map with P(x, y). Skinned parts (stag, antlers, branches)
are built in Blender from the skeletons written next to OUT.npz.
"""
import sys, json
import numpy as np
from scipy.spatial import ConvexHull
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/emerald_stag_claude_20261108/tools')
from meshkit import Part, merge, unit, grid, sweep, cap, catmull, resample_polyline, gem, ngon, orient, revolve

S = 5.405 / 1153.0
TOP = 2.95
CX = 625.0


def P(x, y):
    return np.array([(x - CX) * S, TOP - (y - 42) * S])


def PX(px):
    return px * S


rng = np.random.default_rng(7)
parts = {}


def add(mat, p):
    parts.setdefault(mat, []).append(p)


def flat(V, T, outward=None):
    """Unshared vertices with one normal per triangle (crisp facets)."""
    Vf, Nf, Tf = [], [], []
    for t in T:
        tri = V[list(t)]; n = unit(np.cross(tri[1] - tri[0], tri[2] - tri[0]))
        if outward is not None and np.dot(n, outward(tri.mean(0))) < 0: n = -n
        for q in tri: Vf.append(q); Nf.append(n)
        Tf.append((len(Vf) - 3, len(Vf) - 2, len(Vf) - 1))
    return orient(Part(np.array(Vf), np.array(Nf), np.array(Tf)))


def tube(path3, r, sides=10, taper=None):
    C = resample_polyline(np.asarray(path3, float), max(6, len(path3) * 3))[0]
    T = unit(np.gradient(C, axis=0))
    ref = np.where(np.abs(T[:, 2:3]) < 0.9, np.array([[0, 0, 1.0]]), np.array([[1.0, 0, 0]]))
    A = unit(np.cross(T, ref)); O = unit(np.cross(A, T))
    a = np.linspace(0, 2 * np.pi, sides, endpoint=False)
    prof = np.c_[np.cos(a), np.sin(a)] * r
    sc = np.ones(len(C)) if taper is None else np.linspace(taper[0], taper[1], len(C))
    return sweep(C, A, O, prof, scale_a=sc, scale_o=sc)


# ---------------- crescent frame and left arm ----------------
BLADE = np.array([(-1, -0.45), (-0.1, -1.0), (1, -0.22), (1, 0.22), (-0.1, 1.0), (-1, 0.45)])  # counterclockwise: outward normals


def band_along(path_px, width_px, depth, z0=0.0, taper_end=True, n=90, prof=BLADE):
    pts = np.array([P(*q) for q in path_px])
    c = resample_polyline(catmull(pts, 12), n)[0]
    C = np.c_[c, np.full(len(c), z0)]
    T = unit(np.gradient(C, axis=0)); O = np.repeat(np.array([[0, 0, 1.0]]), len(C), 0); A = unit(np.cross(T, O))
    s = np.linspace(0, 1, len(C))
    w = PX(width_px) / 2 * ((np.clip((1 - s) / 0.45, 0, 1) ** 0.9 * 0.95 + 0.05) if taper_end else np.ones_like(s))
    pr = prof * [1, depth / 2]
    p = sweep(C, A, O, pr, scale_a=w)
    loop0 = C[0] + np.outer(pr[:, 0] * w[0], A[0]) + np.outer(pr[:, 1], O[0])
    parts_ = [p, cap(loop0, -T[0])]
    if not taper_end:
        loop1 = C[-1] + np.outer(pr[:, 0] * w[-1], A[-1]) + np.outer(pr[:, 1], O[-1])
        parts_.append(cap(loop1, T[-1]))
    return merge(parts_)


RIGHT_ARC = [(1022, 845), (1030, 770), (1040, 690), (1043, 600), (1025, 530), (985, 470), (933, 434)]
LEFT_ARC = [(228, 845), (220, 760), (213, 700), (210, 630), (215, 560)]
add('gold', band_along(RIGHT_ARC, 42, 0.19))
add('gold', band_along(LEFT_ARC, 32, 0.19, taper_end=False))


# ---------------- emerald settings ----------------
def kite_setting(cx, cy, w_px, h_px, z_front, gem_scale=0.74):
    w, h = PX(w_px), PX(h_px); c = P(cx, cy)
    outer = np.array([[w / 2, 0], [0, h / 2], [-w / 2, 0], [0, -h / 2]])
    def ring(k):
        pts = []
        for i in range(4):
            a, b = outer[i] * k, outer[(i + 1) % 4] * k
            for t in np.linspace(0, 1, 3, endpoint=False):
                pts.append(a * (1 - t) + b * t)
        return np.array(pts)
    # double stepped bevel: outer slope, flat, step down, second slope, seat
    steps = [(1.16, -0.06), (1.10, 0.035), (1.02, 0.045), (0.98, 0.02), (0.90, 0.04), (0.84, 0.045), gem_scale and (gem_scale + 0.02, 0.01)]
    for sz in (1, -1):
        G = np.array([np.c_[ring(k) + c, np.full(12, sz * (z_front + dz))] for k, dz in steps])
        H = np.zeros_like(G); H[..., 2] = sz
        g = grid(G if sz > 0 else G[:, ::-1], closed_v=True, hint=H)
        add('gold', g)
        k8 = []
        inner = outer * gem_scale
        for i in range(4):
            a, b = inner[i], inner[(i + 1) % 4]; k8 += [a, (a + b) / 2]
        frame = np.eye(3) if sz > 0 else np.diag([-1, 1, -1.0])
        add('emerald', gem(np.array(k8), [(0.70, 0.05), (0.38, 0.09)], 0.11, frame, np.r_[c, sz * z_front]))
    # side wall closing the setting
    o = ring(1.16)
    W = np.array([np.c_[o + c, np.full(12, z_front - 0.06)], np.c_[o + c, np.full(12, -(z_front - 0.06))]])
    out2 = np.c_[unit(o), np.zeros(12)]
    add('gold', grid(W, closed_v=True, hint=np.repeat(out2[None], 2, 0)))


kite_setting(210, 598, 46, 64, 0.11)
kite_setting(1043, 598, 46, 64, 0.11)


# ---------------- base: shallow chevron bowl ----------------
CORNER = (225, 840)
OUTLINE = [(225, 840), (262, 905), (302, 964), (400, 1025), (492, 1080), (560, 1140), (CX, 1195)]


def zf(X):
    return 0.40 + 0.12 * (1 - np.abs(X) / 1.9)


def base():
    ns = 30
    s = np.linspace(0, 1, ns)
    rim = np.array([P(225 + 400 * t, 840 + 101 * (1 - (1 - t) ** 1.8)) for t in s])
    bot = resample_polyline(np.array([P(*q) for q in OUTLINE]), ns)[0]
    ts = np.array([0.0, 0.25, 0.5, 0.70, 0.74, 0.86, 1.0])
    chamfer = lambda t: np.where(t > 0.72, -0.20 * (t - 0.72) / 0.28, 0.0)
    for sx in (1, -1):
        for sz in (1, -1):
            G = np.zeros((len(ts), ns, 3))
            for i, t in enumerate(ts):
                xy = rim * (1 - t) + bot * t
                G[i, :, :2] = xy * [sx, 1]
                G[i, :, 2] = sz * (zf(xy[:, 0]) + chamfer(t))
            H = np.zeros_like(G); H[..., 2] = sz
            add('marble', grid(G if sx * sz > 0 else G[:, ::-1], hint=H if sx * sz > 0 else H[:, ::-1]))
            # gold: rim band, middle strip, bottom band
            def band_on(curve_xy, width_px, zoff, depth=0.05):
                xy = curve_xy * [sx, 1]
                C = np.c_[xy, sz * (zf(xy[:, 0]) + zoff)]
                T = unit(np.gradient(C, axis=0)); O = np.repeat(np.array([[0, 0, sz * 1.0]]), len(C), 0); A = unit(np.cross(T, O))
                prof = np.array([(1, -0.5), (1, 0.35), (0.7, 1.0), (-0.7, 1.0), (-1, 0.35), (-1, -0.5)]) * [PX(width_px) / 2, depth]  # counterclockwise flat top with bevels
                return sweep(C, A, O, prof)
            add('gold', band_on(rim + np.array([0, -PX(14)]), 36, 0.02, 0.06))
            mid = rim * 0.28 + bot * 0.72
            add('gold', band_on(mid, 24, 0.025, 0.045))
            add('gold', band_on(bot, 26, -0.17, 0.06))
            # keel: two converging lines from the bezel to the point
            if sx > 0:
                line = np.linspace(P(CX, 1040), P(CX, 1192), 8)
                zline = sz * (zf(line[:, 0]) + chamfer(np.linspace(0.55, 1.0, 8)) + 0.02)
                C = np.c_[line, zline]; T = unit(np.gradient(C, axis=0)); O = np.repeat(np.array([[0, 0, sz * 1.0]]), 8, 0); A = unit(np.cross(T, O))
                kp = np.array([(1, -0.5), (1, 0.3), (0, 1.0), (-1, 0.3), (-1, -0.5)]) * [PX(13), 0.05]
                add('gold', sweep(C, A, O, kp, scale_a=np.linspace(1.0, 0.35, 8)))
    # underside walls along the outline (between the front and back chamfer edges)
    for sx in (1, -1):
        xy = bot * [sx, 1]
        zb = zf(xy[:, 0]) - 0.20
        W = np.array([np.c_[xy, zb], np.c_[xy, -zb]])
        tng = np.gradient(xy, axis=0); out2 = unit(np.c_[tng[:, 1], -tng[:, 0]]) * (-sx)
        add('marble', grid(W, hint=np.repeat(np.c_[out2, np.zeros(len(xy))][None], 2, 0)))
    # bowl top behind the rim (hidden by rock and moss)
    ytop = P(0, 840)[1]
    for sx in (1, -1):
        q = rim * [sx, 1]
        rows = [np.c_[q, zf(q[:, 0])], np.c_[q[:, 0], np.full(ns, ytop), np.full(ns, 0.28)],
                np.c_[q[:, 0], np.full(ns, ytop), np.full(ns, -0.28)], np.c_[q, -zf(q[:, 0])]]
        G = np.array(rows); H = np.zeros_like(G); H[..., 1] = 1
        add('marble', grid(G, hint=H))
    # pointed, slightly upturned corner tips
    for sx in (1, -1):
        c = P(225, 840) * [sx, 1]
        tip = c + np.array([-0.07 * sx, 0.17])
        for sz in (1, -1):
            V = np.array([np.r_[c + [0.03 * sx, -0.06], sz * 0.30], np.r_[c + [0.03 * sx, 0.06], sz * 0.30],
                          np.r_[c + [0.03 * sx, 0.0], sz * 0.50], np.r_[tip, sz * 0.38]])
            add('gold', flat(V, [(0, 1, 3), (1, 2, 3), (2, 0, 3)], outward=lambda m: np.r_[(m[:2] - c) * 0 + [-sx, 0.3], sz * 0.5]))
    for sx in (1, -1):
        q = rim[:12] * [sx, 1]
        add('gold', tube(np.c_[q[:, 0], np.full(12, ytop + 0.01), np.full(12, -0.28)], PX(9), sides=8))
    kite_setting(CX, 968, 112, 156, 0.55, gem_scale=0.68)


base()


# ---------------- rock: big flat facets ----------------
def rock():
    pts = [(390, 890, 0.44), (400, 800, 0.36), (470, 782, 0.38), (520, 760, 0.35), (700, 705, 0.32), (770, 680, 0.28), (895, 676, 0.22),
           (898, 870, 0.40), (700, 930, 0.46), (420, 860, -0.30), (520, 770, -0.30), (760, 690, -0.24), (890, 690, -0.22),
           (890, 860, -0.26), (650, 920, -0.30), (640, 728, 0.05), (830, 672, 0.0)]
    V = np.array([np.r_[P(x, y), z] for x, y, z in pts])
    hull = ConvexHull(V)
    c = V.mean(0)
    for simplex, eq in zip(hull.simplices, hull.equations):
        mat = 'marble_top' if eq[1] > 0.55 else 'marble'
        add(mat, flat(V, [tuple(simplex)], outward=lambda m: m - c))


rock()


# ---------------- moss mounds ----------------
def icosphere(level):
    t = (1 + 5 ** 0.5) / 2
    V = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
         (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    V = [np.array(v, float) / np.linalg.norm(v) for v in V]
    for _ in range(level):
        cache, F2 = {}, []
        def mid(a, b):
            key = tuple(sorted((a, b)))
            if key not in cache:
                m = V[a] + V[b]; V.append(m / np.linalg.norm(m)); cache[key] = len(V) - 1
            return cache[key]
        for a, b, c in F:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            F2 += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        F = F2
    return np.array(V), np.array(F)


ICO_V, ICO_T = icosphere(2)


def moss_mound(cx, cy, w_px, h_px, z, depth, lumps):
    c = np.r_[P(cx, cy), z]
    for k in range(lumps):
        off = np.array([rng.uniform(-0.42, 0.42) * PX(w_px), rng.uniform(-0.1, 0.35) * PX(h_px), rng.uniform(-0.4, 0.4) * depth])
        r = np.array([PX(w_px) * rng.uniform(0.22, 0.34), PX(h_px) * rng.uniform(0.55, 0.8), depth * rng.uniform(0.3, 0.45)])
        V = ICO_V.copy()
        # lumpy, with small tufts: low frequency lumps plus small bumps no smaller than a few screen pixels
        lump = 1 + 0.15 * np.sin(3 * V[:, 0] + 2 * V[:, 1] + rng.uniform(0, 6)) + 0.10 * rng.standard_normal(len(V)) * (V[:, 1] > -0.2)
        Vd = V * lump[:, None] * r + c + off
        Vd[:, 1] = np.maximum(Vd[:, 1], c[1] + off[1] - r[1] * 0.25)
        add('moss', orient(Part(Vd, unit(V), ICO_T)))


MOSS = [(383, 845, 230, 90, 0.20, 0.75, 8), (300, 860, 120, 60, -0.10, 0.5, 3), (674, 722, 180, 70, 0.14, 0.5, 6),
        (525, 760, 100, 50, 0.16, 0.4, 3), (765, 880, 150, 65, 0.30, 0.5, 5), (880, 872, 110, 50, -0.05, 0.45, 3)]
for m in MOSS:
    moss_mound(*m)


# ---------------- skeletons (also used for leaf stems) ----------------
def sk(points):
    return [[float(v) for v in np.r_[P(x, y), z]] + [float(PX(r))] for (x, y, z, r) in points]


SKELETON = {
    'stag': {
        'spine': sk([(518, 570, 0, 60), (565, 560, 0, 66), (630, 538, 0, 64), (700, 512, 0, 68), (765, 495, 0, 72)]),
        'neck': sk([(770, 495, 0, 70), (790, 430, 0, 64), (797, 370, 0, 56), (802, 325, 0, 48), (806, 302, 0, 40)]),
        'head': sk([(790, 306, 0, 40), (812, 298, 0, 38), (840, 287, 0, 29), (866, 282, 0, 19), (891, 286, 0, 9)]),
        'tail': sk([(522, 560, 0, 15), (500, 546, 0, 13), (482, 540, 0, 10), (466, 540, 0, 7), (458, 546, 0, 3)]),
        'hind_near': sk([(525, 595, 0.13, 44), (495, 640, 0.14, 22), (458, 695, 0.14, 15), (420, 765, 0.14, 10), (395, 810, 0.14, 12), (381, 826, 0.14, 12)]),
        'hind_far': sk([(572, 600, -0.12, 38), (566, 648, -0.13, 20), (600, 700, -0.13, 15), (576, 735, -0.13, 10), (563, 757, -0.13, 12)]),
        'fore_raised': sk([(790, 525, 0.11, 30), (850, 532, 0.12, 15), (905, 540, 0.12, 14), (882, 600, 0.12, 10), (858, 650, 0.12, 11), (851, 666, 0.12, 12)]),
        'fore_down': sk([(765, 535, -0.11, 30), (752, 590, -0.12, 15), (740, 640, -0.12, 13), (730, 675, -0.12, 10), (724, 700, -0.12, 12)]),
    },
    'ears': [sk([(795, 284, 0.12, 12), (752, 280, 0.14, 19), (700, 284, 0.15, 3)]), sk([(795, 284, -0.12, 12), (756, 286, -0.14, 19), (708, 290, -0.15, 3)])],
    'antlers': [
        sk([(808, 274, 0.09, 16), (775, 238, 0.10, 15), (730, 212, 0.10, 14), (680, 200, 0.11, 13), (630, 200, 0.11, 12), (580, 208, 0.11, 11.5),
            (535, 222, 0.11, 10.5), (500, 236, 0.11, 9.5), (474, 230, 0.11, 8.5), (461, 204, 0.11, 7), (465, 174, 0.11, 5.5), (478, 155, 0.11, 4), (490, 146, 0.11, 2.5)]),
        sk([(802, 278, -0.09, 15), (765, 268, -0.10, 14), (715, 266, -0.10, 13), (660, 270, -0.11, 12.5), (605, 276, -0.11, 12), (552, 283, -0.12, 11),
            (508, 288, -0.12, 9), (476, 292, -0.12, 6), (458, 290, -0.12, 4), (452, 284, -0.12, 2)]),
        sk([(790, 248, 0.10, 13), (782, 205, 0.10, 11), (786, 160, 0.10, 8.5), (798, 122, 0.10, 6), (810, 100, 0.10, 4), (818, 90, 0.10, 2.5)]),
        sk([(768, 262, -0.10, 12.5), (752, 222, -0.10, 10.5), (744, 184, -0.10, 8), (748, 156, -0.10, 5.5), (760, 136, -0.10, 3)]),
        sk([(700, 202, 0.11, 11), (684, 172, 0.11, 9), (680, 142, 0.11, 7), (690, 118, 0.11, 5), (708, 104, 0.11, 3), (724, 100, 0.11, 2)]),
        sk([(620, 201, 0.11, 10), (604, 178, 0.11, 8.5), (598, 156, 0.11, 6.5), (606, 138, 0.11, 4), (620, 130, 0.11, 2)]),
        sk([(548, 218, 0.11, 9.5), (530, 198, 0.11, 8), (524, 180, 0.11, 6), (532, 166, 0.11, 3.5), (544, 160, 0.11, 2)]),
        sk([(660, 270, -0.11, 10), (646, 246, -0.11, 8), (642, 222, -0.11, 6), (650, 206, -0.11, 3.5), (662, 200, -0.11, 2)]),
        sk([(575, 279, -0.12, 9), (556, 260, -0.12, 7), (550, 240, -0.12, 5), (556, 226, -0.12, 2.5)]),
    ],
    'branches': [
        sk([(215, 562, 0.0, 15), (226, 520, 0.03, 15), (262, 452, 0.06, 14), (306, 388, 0.08, 13), (352, 312, 0.09, 11.5), (385, 240, 0.09, 10),
            (432, 165, 0.07, 8.5), (478, 128, 0.06, 7), (545, 110, 0.05, 6), (612, 100, 0.04, 4.5), (690, 96, 0.04, 3)]),
        sk([(430, 150, 0.07, 6), (410, 152, 0.08, 4.5), (397, 160, 0.08, 4)]),
        sk([(372, 236, 0.09, 6), (377, 224, 0.0, 5), (379, 218, -0.05, 4)]),
        sk([(240, 482, 0.04, 7), (228, 464, 0.07, 5.5), (225, 456, 0.10, 4.5)]),
        sk([(290, 408, 0.08, 8), (240, 384, 0.09, 6), (200, 372, 0.10, 4)]),
        sk([(330, 395, 0.08, 9), (370, 368, 0.14, 8), (430, 400, 0.14, 7), (500, 420, 0.10, 6), (560, 432, 0.06, 5), (606, 436, 0.05, 3.5)]),
        sk([(379, 800, 0.20, 10), (360, 722, 0.15, 9), (340, 662, 0.12, 8), (322, 612, 0.10, 6.5), (315, 574, 0.10, 5)]),
        sk([(815, 895, 0.22, 11), (860, 870, 0.20, 10), (905, 840, 0.20, 9.5), (940, 800, 0.20, 9), (960, 760, 0.18, 8), (975, 720, 0.15, 7),
            (987, 676, 0.12, 6), (995, 640, 0.10, 4.5)]),
        sk([(940, 800, 0.20, 6), (924, 812, 0.19, 5)]),
        sk([(470, 122, 0.06, 6), (500, 100, 0.06, 5), (530, 88, 0.06, 4)]),
        sk([(540, 106, 0.05, 5), (575, 125, 0.0, 4), (600, 135, -0.05, 3.5)]),
    ],
}
BRANCH_PTS = np.array([p[:3] for chain in SKELETON['branches'] for p in chain])


def stem_to_branch(base3, max_dist=0.45):
    d = np.linalg.norm(BRANCH_PTS - base3, axis=1); j = int(np.argmin(d))
    if 0.02 < d[j] < max_dist:
        add('gold', tube([BRANCH_PTS[j], (BRANCH_PTS[j] + base3) / 2 + [0, 0.01, 0], base3], PX(4.5), sides=8))


# ---------------- leaves: two tone enamel on a gold plate with a gold midrib ----------------
def leaf(base_px, tip_px, width_px, z0, tilt, curl=0.24, scale=1.2):
    b, t = P(*base_px), P(*tip_px)
    t = b + (t - b) * scale
    L = np.linalg.norm(t - b); W = PX(width_px) * scale * 1.3
    nu, nv = 14, 9
    u = np.linspace(0, 1, nu)[:, None]; v = np.linspace(-1, 1, nv)[None, :]
    half = W / 2 * np.sin(np.pi * np.clip(u, 0, 1)) ** 0.75 * (1 - 0.2 * u)
    X = u * L + 0 * v; Y = v * half
    Z = -0.16 * W * np.abs(v) + curl * L * (u - 0.35) ** 2
    ax = unit(t - b); ay = np.array([-ax[1], ax[0]])
    ca, sa = np.cos(tilt), np.sin(tilt)
    def place(Xl, Yl, Zl, dz):
        Y2 = Yl * ca - Zl * sa; Z2 = Yl * sa + Zl * ca + dz
        pts = b[None, None, :] + Xl[..., None] * ax + Y2[..., None] * ay
        return np.concatenate([pts, (Z2 + z0)[..., None]], -1)
    nrm = lambda s2: np.repeat(np.repeat(np.r_[0, 0, s2][None, None], nu, 0), nv, 1)
    for s2 in (1, -1):
        add('gold', grid(place(X, Y, Z, s2 * 0.004), hint=nrm(s2)))
    k = nv // 2
    for side in (1, -1):
        Xs = L * 0.04 + X * 0.92
        for half_i, mat in ((slice(0, k + 1), 'leaf'), (slice(k, nv), 'leaf_light')):
            G = place(Xs[:, half_i], Y[:, half_i] * 0.91, Z[:, half_i], side * 0.012)
            add(mat, grid(G, hint=nrm(side)[:, half_i]))
    mid = place(X[:, k:k + 1] * 0.9 + L * 0.03, Y[:, k:k + 1] * 0, Z[:, k:k + 1], 0)[:, 0]
    for side in (1, -1):
        add('gold', tube(mid + [0, 0, side * 0.016], PX(2.6), sides=6, taper=(1.0, 0.3)))
    stem_to_branch(np.r_[b, z0])


LEAVES = [  # base px, tip px, width px, z, tilt (radians)
    ((425, 132), (492, 75), 40, 0.10, 0.4), ((600, 104), (634, 46), 44, 0.00, -0.3), ((612, 108), (700, 98), 40, 0.15, 0.3),
    ((585, 140), (678, 126), 40, -0.10, -0.4), ((515, 133), (572, 108), 30, 0.05, 0.2), ((369, 218), (333, 160), 40, 0.12, 0.5),
    ((328, 322), (292, 250), 44, -0.05, -0.4), ((288, 370), (172, 368), 50, 0.10, 0.3), ((418, 405), (497, 368), 40, 0.15, -0.3),
    ((474, 420), (615, 445), 52, 0.05, 0.4), ((470, 405), (572, 396), 40, -0.12, -0.3), ((341, 475), (413, 489), 34, 0.10, 0.4),
    ((225, 460), (155, 456), 34, -0.05, -0.3), ((300, 614), (336, 556), 34, 0.10, 0.3), ((320, 648), (378, 612), 36, -0.08, -0.4),
    ((294, 684), (236, 668), 30, 0.08, 0.3), ((336, 802), (284, 790), 34, 0.10, -0.3), ((947, 670), (978, 618), 32, 0.10, 0.3),
    ((990, 700), (1016, 660), 28, -0.05, -0.3), ((872, 816), (806, 786), 40, 0.15, 0.4), ((928, 795), (890, 758), 30, -0.10, -0.3),
    ((400, 168), (378, 120), 28, -0.12, 0.3), ((260, 676), (224, 650), 30, 0.12, 0.2), ((925, 860), (900, 885), 28, 0.20, 0.3),
    ((880, 805), (820, 800), 36, 0.25, 0.3), ((940, 845), (905, 865), 32, 0.25, -0.3), ((985, 690), (1000, 650), 28, 0.12, 0.2),
    ((950, 700), (942, 640), 30, 0.14, 0.3), ((972, 705), (992, 648), 28, 0.10, -0.2),
]
for b_, t_, w_, z_, tl_ in LEAVES:
    leaf(b_, t_, w_, z_, tl_)


# ---------------- flowers and buds ----------------
def petal_grid(L, W, cup):
    nu, nv = 9, 7
    u = np.linspace(0, 1, nu)[:, None]; v = np.linspace(-1, 1, nv)[None, :]
    half = W / 2 * np.sin(np.pi * np.clip(0.12 + 0.88 * u, 0, 1)) ** 0.6
    return u * L + 0 * v, v * half, cup * (v ** 2) * W + 0.15 * L * u ** 2


def flower(cx, cy, r_px, z, face):
    c = np.r_[P(cx, cy), z]
    fz = unit(np.array(face, float)); fy = unit(np.array([0, 1.0, 0]) - fz[1] * fz); fx = np.cross(fy, fz)
    R = PX(r_px)
    for ring, (count, L, W, el, rot) in enumerate(((6, R, R * 0.92, 0.35, 0.0), (5, R * 0.74, R * 0.80, 0.85, 0.5))):
        for k in range(count):
            ang = 2 * np.pi * (k + rot) / count + 0.2
            d = np.array([np.cos(ang), np.sin(ang)])
            axis3 = unit(d[0] * fx + d[1] * fy + np.tan(el) * 0.75 * fz)
            side3 = unit(np.cross(fz, axis3)); up3 = unit(np.cross(axis3, side3))
            for mat, sc, off in (('petal', 1.0, 0.004), ('petal', 1.0, -0.004)):
                X, Y, Zc = petal_grid(L * sc, W * sc, 0.45)
                pts = c + (X + L * (1 - sc) * 0.3)[..., None] * axis3 + Y[..., None] * side3 + (Zc + off)[..., None] * up3 + fz * 0.01 * ring
                sgn = 1 if off >= 0 else -1
                hint = np.repeat(np.repeat((sgn * up3)[None, None], X.shape[0], 0), X.shape[1], 1)
                if mat == 'gold':
                    add(mat, grid(pts, hint=hint)); add(mat, grid(pts[:, ::-1], hint=-hint[:, ::-1]))
                else:
                    add(mat, grid(pts if sgn > 0 else pts[:, ::-1], hint=hint if sgn > 0 else hint[:, ::-1]))
    prof = np.array([(0.0, 0.0), (R * 0.30, 0.0), (R * 0.33, R * 0.16), (R * 0.22, R * 0.30), (0.0, R * 0.34)])
    cone = revolve(resample_polyline(prof, 10)[0], 18)
    M = np.stack([fx, fz, -fy], 1)
    add('stamen', cone.transformed(M, c))
    stem_to_branch(c - fz * 0.05, max_dist=0.5)


def bud(cx, cy, r_px, z, ang_deg):
    R = PX(r_px); c = np.r_[P(cx, cy), z]
    prof = np.array([(0.0, -R * 1.1), (R * 0.55, -R * 0.8), (R * 0.75, -R * 0.1), (R * 0.55, R * 0.6), (R * 0.2, R * 1.05), (0.0, R * 1.2)])
    b = revolve(resample_polyline(catmull(prof, 6), 18)[0], 18)
    a = np.radians(ang_deg); up = np.array([np.cos(a), np.sin(a), 0.0]); side = np.array([-up[1], up[0], 0.0])
    M = np.stack([side, up, np.array([0, 0, 1.0])], 1)
    add('petal', b.transformed(M, c))
    # three gold sepals hugging the lower half
    for k in range(3):
        ang = 2 * np.pi * k / 3 + 0.3
        n = np.cos(ang) * side + np.sin(ang) * np.array([0, 0, 1.0])
        base3 = c - up * R * 0.95 + n * R * 0.25
        tip3 = c + up * R * 0.15 + n * R * 0.80
        add('gold', tube([base3, (base3 + tip3) / 2 + n * R * 0.25, tip3], R * 0.28, sides=8, taper=(1.0, 0.25)))
    stem_to_branch(c - up * R * 1.1, max_dist=0.4)


flower(370, 353, 88, 0.22, face=(0.40, 0.62, 0.68))
flower(951, 770, 80, 0.24, face=(-0.40, 0.62, 0.68))
for (bx, by, br, bz, ba) in ((397, 157, 20, 0.08, 60), (379, 215, 19, -0.05, 75), (225, 446, 20, 0.10, 100), (924, 803, 17, 0.20, 40), (990, 655, 15, 0.12, 80)):
    bud(bx, by, br, bz, ba)


# ---------------- hooves and eyes (only for the skeleton built stag) ----------------
import os
for k in (() if os.environ.get('CARVED') else ('hind_near', 'hind_far', 'fore_raised', 'fore_down')):
    end = np.array(SKELETON['stag'][k][-1][:3])
    prev = np.array(SKELETON['stag'][k][-2][:3])
    d = unit(end - prev)
    add('antler', tube([end - d * 0.02, end + d * 0.045, end + d * 0.07], PX(13), sides=10, taper=(1.0, 0.55)))
for sz in (() if os.environ.get('CARVED') else (1, -1)):
    eye = np.r_[P(818, 274), sz * 0.085]
    add('antler', tube([eye - [0.012, 0, 0], eye + [0.012, 0.004, 0]], PX(3.2), sides=8))


if __name__ == '__main__':
    data = {}
    for mat, ps in parts.items():
        m = orient(merge(ps))
        data[mat + '_v'] = m.V; data[mat + '_n'] = m.N; data[mat + '_t'] = m.T
        if m.UV is not None:
            data[mat + '_uv'] = m.UV
    np.savez(sys.argv[1], **data)
    json.dump(SKELETON, open(sys.argv[1].replace('.npz', '_skeleton.json'), 'w'))
    tris = {k[:-2]: len(data[k]) for k in data if k.endswith('_t')}
    allv = np.vstack([data[k] for k in data if k.endswith('_v')])
    print('triangles', sum(tris.values()), tris, 'bounds', allv.min(0).round(2), allv.max(0).round(2))
