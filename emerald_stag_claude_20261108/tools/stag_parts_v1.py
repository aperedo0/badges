"""Emerald Stag: frame, base, rock, moss, leaves, flowers, buds and emeralds as meshes (model units).

Usage: stag_parts.py OUT.npz [design.json]
Model: Y up, front +Z. Mockup pixels map with P(x, y). Skinned parts (stag, antlers, branches)
are built in Blender from the skeletons in skeleton.json, which this script also writes.
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


# ---------------- crescent frame ----------------
def band_along(path_px, width_px, depth, z0=0.0, taper_end=True, n=80):
    pts = np.array([P(*q) for q in path_px])
    c = resample_polyline(catmull(pts, 12), n)[0]
    C = np.c_[c, np.full(len(c), z0)]
    T = unit(np.gradient(C, axis=0))
    O = np.repeat(np.array([[0, 0, 1.0]]), len(C), 0)
    A = unit(np.cross(T, O))
    s = np.linspace(0, 1, len(C))
    w = PX(width_px) / 2 * (np.clip((1 - s) / 0.35, 0, 1) ** 0.8 * 0.92 + 0.08 if taper_end else np.ones_like(s))
    d = depth / 2
    prof = np.array([(-1, -0.6), (-1, 0.6), (-0.7, 1.0), (0.7, 1.0), (1, 0.6), (1, -0.6), (0.7, -1.0), (-0.7, -1.0)])
    prof = prof * [1, d]
    p = sweep(C, A, O, prof, scale_a=w)
    loop0 = C[0] + np.outer(prof[:, 0] * w[0], A[0]) + np.outer(prof[:, 1], O[0])
    return merge([p, cap(loop0, -T[0])])


RIGHT_ARC = [(1020, 840), (1040, 760), (1047, 680), (1043, 600), (1025, 530), (985, 470), (933, 434)]
LEFT_ARC = [(228, 840), (212, 760), (206, 700), (208, 630), (215, 572)]
add('gold', band_along(RIGHT_ARC, 36, 0.17))
add('gold', band_along(LEFT_ARC, 28, 0.17, taper_end=False))


# ---------------- emerald settings ----------------
def kite_setting(cx, cy, w_px, h_px, z_front, mat_gem='emerald'):
    w, h = PX(w_px), PX(h_px)
    c = P(cx, cy)
    outer = np.array([[w / 2, 0], [0, h / 2], [-w / 2, 0], [0, -h / 2]])
    rim = 0.30 * min(w, h)
    # gold frame: a sloped kite ring
    inner = outer * (1 - rim / (min(w, h) / 2) * 0.55)
    loops = [(outer * 1.12, z_front - 0.04), (outer * 1.06, z_front + 0.03), (outer, z_front + 0.05), (inner, z_front + 0.02)]
    rows = []
    for o, z in loops:
        pts = []
        for i in range(4):
            a, b = o[i], o[(i + 1) % 4]
            for t in np.linspace(0, 1, 4, endpoint=False):
                pts.append(a * (1 - t) + b * t)
        pts = np.array(pts)
        rows.append(np.c_[pts + c, np.full(len(pts), z)])
    G = np.array(rows)
    hint = np.zeros_like(G); hint[..., 2] = 1
    add('gold', grid(G, closed_v=True, hint=hint))
    k8 = []
    for i in range(4):
        a, b = inner[i], inner[(i + 1) % 4]
        k8 += [a, (a + b) / 2]
    frame = np.eye(3)
    add(mat_gem, gem(np.array(k8) * 0.98, [(0.72, 0.05), (0.40, 0.09)], 0.115, frame, np.r_[c, z_front + 0.0]))
    # back copy (finished from behind)
    back = np.diag([1, 1, -1.0])
    add(mat_gem, gem(np.array(k8) * 0.98, [(0.72, 0.05), (0.40, 0.09)], 0.115, np.diag([-1, 1, -1.0]), np.r_[c, -z_front]))
    G2 = G.copy(); G2[..., 2] *= -1
    hint2 = hint.copy(); hint2[..., 2] = -1
    add('gold', grid(G2[:, ::-1], closed_v=True, hint=hint2[:, ::-1]))


kite_setting(210, 598, 42, 60, 0.09)
kite_setting(1043, 598, 42, 60, 0.09)


# ---------------- base ----------------
BASE_TL, BASE_TR = (225, 837), (1025, 837)
def v_rim(n=24):
    xs = np.linspace(BASE_TL[0], CX, n)
    t = (xs - BASE_TL[0]) / (CX - BASE_TL[0])
    ys = BASE_TL[1] + (941 - BASE_TL[1]) * (t ** 1.35)
    return np.c_[xs, ys]


def base():
    left_top = v_rim()
    left_side = np.array([(225, 837), (236, 905), (250, 975)])
    bottom = np.array([(250, 975), (440, 1088), (CX, 1195)])
    zf = lambda X: 0.40 + 0.12 * (1 - np.abs(X) / 1.85)
    half = []
    # left half polygon (front view): top V rim, keel, bottom edge, left side
    poly = np.vstack([left_top, [(CX, 1195)], bottom[::-1][1:-1], left_side[::-1][:-1]])
    pts = np.array([P(*q) for q in poly])
    ctr = pts.mean(0)
    for sgn_x in (1, -1):
        for sgn_z in (1, -1):
            V = [np.r_[ctr * [sgn_x, 1], sgn_z * zf(ctr[0])]]
            for q in pts:
                qq = q * [sgn_x, 1]
                V.append(np.r_[qq, sgn_z * zf(qq[0])])
            V = np.array(V); m = len(pts)
            T = np.array([(0, 1 + k, 1 + (k + 1) % m) for k in range(m)])
            # flat faceted look: per facet normals
            Vf, Nf, Tf = [], [], []
            for t in T:
                tri = V[t]; nrm = unit(np.cross(tri[1] - tri[0], tri[2] - tri[0]))
                if nrm[2] * sgn_z < 0: nrm = -nrm
                for q in tri: Vf.append(q); Nf.append(nrm)
                Tf.append((len(Vf) - 3, len(Vf) - 2, len(Vf) - 1))
            add('marble', orient(Part(np.array(Vf), np.array(Nf), np.array(Tf))))
    # side walls (left side and bottom edge), both halves
    edge = np.vstack([left_side, bottom[1:]])
    e = np.array([P(*q) for q in edge])
    for sgn_x in (1, -1):
        ee = e * [sgn_x, 1]
        W = np.array([[np.r_[q, zf(q[0])] for q in ee], [np.r_[q, -zf(q[0])] for q in ee]])
        out2 = np.c_[np.gradient(ee, axis=0)[:, 1], -np.gradient(ee, axis=0)[:, 0]] * (-sgn_x)
        H = np.repeat(np.c_[unit(out2), np.zeros(len(ee))][None], 2, 0)
        add('marble', grid(W, hint=H))
    # top bowl: from the front V rim back and up to a flat top at y(834), then down to the back V rim
    ytop = P(0, 834)[1]
    vr = np.array([P(*q) for q in left_top])
    for sgn_x in (1, -1):
        q = vr * [sgn_x, 1]
        rows = [np.c_[q, zf(q[:, 0])], np.c_[q[:, 0], np.full(len(q), ytop), 0.25 * np.ones(len(q))],
                np.c_[q[:, 0], np.full(len(q), ytop), -0.25 * np.ones(len(q))], np.c_[q, -zf(q[:, 0])]]
        G = np.array(rows); H = np.zeros_like(G); H[..., 1] = 1
        add('marble', grid(G, hint=H))
    # gold rims: front and back V rim, keel, outline edges
    def rim_tube(path3, r):
        C = resample_polyline(path3, max(12, len(path3) * 3))[0]
        T = unit(np.gradient(C, axis=0)); ref = np.array([0, 0, 1.0])
        O = unit(np.cross(T, np.cross(ref, T)) + 1e-9)
        O = np.where((np.linalg.norm(np.cross(ref, T), axis=1) < 1e-6)[:, None], np.array([[1.0, 0, 0]]), O)
        A = unit(np.cross(T, O))
        prof = np.c_[np.cos(np.linspace(0, 2 * np.pi, 10, endpoint=False)), np.sin(np.linspace(0, 2 * np.pi, 10, endpoint=False))] * r
        return sweep(C, A, O, prof)
    for sgn_z in (1, -1):
        for sgn_x in (1, -1):
            q = vr * [sgn_x, 1]
            add('gold', rim_tube(np.c_[q, sgn_z * (zf(q[:, 0]) + 0.01)], PX(12)))
            q2 = e * [sgn_x, 1]
            add('gold', rim_tube(np.c_[q2, sgn_z * zf(q2[:, 0])], PX(10)))
            # upper inner band line parallel to the V rim (the mockup's double rim)
            q3 = np.array([P(x, y - 46) for x, y in np.vstack([left_side[1:], bottom[1:-1], [(CX, 1150)]])]) * [sgn_x, 1]
            add('gold', rim_tube(np.c_[q3, sgn_z * (zf(q3[:, 0]) + 0.005)], PX(6)))
        keel = np.array([P(CX, 1040), P(CX, 1195)])
        keel = np.linspace(keel[0], keel[1], 8)
        add('gold', rim_tube(np.c_[keel, sgn_z * (zf(keel[:, 0]) + 0.01)], PX(8)))
    kite_setting(CX, 968, 109, 150, 0.53)


base()


# ---------------- rock ----------------
def rock():
    outline = [(370, 872), (392, 800), (470, 768), (560, 748), (650, 718), (730, 690), (790, 676), (850, 682),
               (888, 720), (895, 790), (880, 860), (760, 890), (600, 905), (470, 905)]
    pts = []
    for (x, y) in outline:
        p2 = P(x, y)
        for z in (-0.32, 0.0, 0.36):
            j = rng.normal(0, 0.03, 2)
            shrink = 0.86 if abs(z) > 0.2 else 1.0
            c = P(640, 800)
            pts.append(np.r_[c + (p2 - c) * shrink + j, z + rng.normal(0, 0.03)])
    pts += [np.r_[P(800, 690), 0.15], np.r_[P(720, 700), 0.30], np.r_[P(560, 760), 0.28], np.r_[P(840, 720), -0.2]]
    pts = np.array(pts)
    hull = ConvexHull(pts)
    V, N, T = [], [], []
    for simplex, eq in zip(hull.simplices, hull.equations):
        tri = pts[simplex]; nrm = eq[:3]
        for q in tri: V.append(q); N.append(nrm)
        T.append((len(V) - 3, len(V) - 2, len(V) - 1))
    add('marble', orient(Part(np.array(V), np.array(N), np.array(T))))


rock()


# ---------------- moss ----------------
def moss_clump(cx, cy, w_px, h_px, z, depth, count):
    from meshkit import Part as _P
    base_ico = icosphere(2)
    c = P(cx, cy)
    for k in range(count):
        off = np.array([rng.uniform(-0.5, 0.5) * PX(w_px), rng.uniform(-0.2, 0.4) * PX(h_px), rng.uniform(-0.5, 0.5) * depth])
        r = np.array([PX(w_px) * rng.uniform(0.18, 0.30), PX(h_px) * rng.uniform(0.35, 0.55), depth * rng.uniform(0.25, 0.4)])
        V = base_ico.copy()
        bump = 1 + 0.18 * rng.standard_normal(len(V))
        Vd = V * bump[:, None] * r + np.r_[c, z] + off
        add('moss', orient(Part(Vd, unit(V), ICO_T)))


def icosphere(level):
    global ICO_T
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
    ICO_T = np.array(F)
    return np.array(V)


icosphere(2)
MOSS = [(383, 852, 200, 60, 0.15, 0.6, 10), (300, 865, 110, 40, -0.15, 0.5, 5), (674, 728, 170, 45, 0.15, 0.4, 8),
        (525, 765, 90, 35, 0.15, 0.3, 4), (765, 888, 136, 40, 0.25, 0.4, 6), (880, 880, 100, 32, -0.05, 0.4, 4)]
for m in MOSS:
    moss_clump(*m)


# ---------------- leaves ----------------
def leaf(base_px, tip_px, width_px, z0, tilt, curl=0.12):
    b, t = P(*base_px), P(*tip_px)
    L = np.linalg.norm(t - b); W = PX(width_px)
    nu, nv = 14, 7
    u = np.linspace(0, 1, nu)[:, None]; v = np.linspace(-1, 1, nv)[None, :]
    half = W / 2 * np.sin(np.pi * np.clip(u, 0, 1)) ** 0.75 * (1 - 0.25 * u)
    X = u * L + 0 * v; Y = v * half
    Z = -0.18 * W * np.abs(v) + curl * L * (u - 0.5) ** 2
    ax = unit(t - b); ay = np.array([-ax[1], ax[0]])
    ca, sa = np.cos(tilt), np.sin(tilt)
    def place(Xl, Yl, Zl, dz):
        Y2 = Yl * ca - Zl * sa; Z2 = Yl * sa + Zl * ca + dz
        pts = b[None, None, :] + Xl[..., None] * ax + Y2[..., None] * ay
        return np.concatenate([pts, (Z2 + z0)[..., None]], -1)
    out = []
    for mat, scale, dz, side in (('gold', 1.0, 0.0, 0), ('leaf', 0.88, 0.012, 1), ('leaf', 0.88, -0.012, -1)):
        Yl = Y * scale
        Xl = X * (0.06 + 0.92 * scale) / (0.98) if scale < 1 else X
        Xl = Xl + (L * (1 - scale) * 0.5 if scale < 1 else 0)
        if side == 0:
            # thin gold plate: two surfaces
            for s2 in (1, -1):
                G = place(Xl, Yl, Z, s2 * 0.004)
                H = np.zeros_like(G); H[..., 2] = s2 * np.cos(tilt); H[..., 1] = 0
                Hn = np.repeat(np.repeat(np.r_[0, 0, s2][None, None], nu, 0), nv, 1)
                add(mat, grid(G, hint=Hn))
        else:
            G = place(Xl, Yl, Z, dz)
            Hn = np.repeat(np.repeat(np.r_[0, 0, side][None, None], nu, 0), nv, 1)
            add(mat, grid(G, hint=Hn))


LEAVES = [  # base px, tip px, width px, z, tilt (radians)
    ((425, 132), (492, 75), 40, 0.10, 0.4), ((592, 86), (678, 48), 44, 0.00, -0.3), ((606, 106), (706, 110), 42, 0.15, 0.3),
    ((585, 140), (678, 126), 40, -0.10, -0.4), ((515, 133), (572, 108), 30, 0.05, 0.2), ((369, 218), (333, 160), 40, 0.12, 0.5),
    ((328, 322), (292, 250), 44, -0.05, -0.4), ((288, 370), (172, 368), 50, 0.10, 0.3), ((418, 405), (497, 368), 40, 0.15, -0.3),
    ((474, 420), (615, 445), 52, 0.05, 0.4), ((470, 405), (572, 396), 40, -0.12, -0.3), ((341, 475), (413, 489), 34, 0.10, 0.4),
    ((225, 460), (155, 456), 34, -0.05, -0.3), ((300, 614), (336, 556), 34, 0.10, 0.3), ((320, 648), (378, 612), 36, -0.08, -0.4),
    ((294, 684), (236, 668), 30, 0.08, 0.3), ((336, 802), (284, 790), 34, 0.10, -0.3), ((947, 670), (978, 618), 32, 0.10, 0.3),
    ((990, 700), (1016, 660), 28, -0.05, -0.3), ((872, 816), (806, 786), 40, 0.15, 0.4), ((928, 795), (890, 758), 30, -0.10, -0.3),
    ((400, 168), (378, 120), 28, -0.12, 0.3),
]
for b_, t_, w_, z_, tl_ in LEAVES:
    leaf(b_, t_, w_, z_, tl_)


# ---------------- flowers and buds ----------------
def petal(L, W, cup):
    nu, nv = 9, 7
    u = np.linspace(0, 1, nu)[:, None]; v = np.linspace(-1, 1, nv)[None, :]
    half = W / 2 * np.sin(np.pi * np.clip(0.15 + 0.85 * u, 0, 1)) ** 0.6
    return u * L + 0 * v, v * half, cup * (v ** 2) * W + 0.12 * L * u ** 2


def flower(cx, cy, r_px, z, face=(0, 0.25, 1.0)):
    c = np.r_[P(cx, cy), z]
    fz = unit(np.array(face, float)); fy = unit(np.array([0, 1.0, 0]) - fz[1] * fz); fx = np.cross(fy, fz)
    R = PX(r_px)
    for ring, (count, L, W, lift, rot) in enumerate(((6, R, R * 0.62, 0.95, 0.0), (5, R * 0.8, R * 0.55, 1.25, 0.5))):
        for k in range(count):
            ang = 2 * np.pi * (k + rot) / count + 0.2
            X, Y, Zc = petal(L, W, 0.35)
            d = np.array([np.cos(ang), np.sin(ang)])
            # petal axis tilted up out of the flower plane by lift
            el = 0.55 if ring == 0 else 0.95
            axis3 = unit(d[0] * fx + d[1] * fy + np.tan(el) * 0.6 * fz)
            side3 = unit(np.cross(fz, axis3)); up3 = unit(np.cross(axis3, side3))
            pts = c + X[..., None] * axis3 + Y[..., None] * side3 + Zc[..., None] * up3 + fz * 0.01 * ring
            hint = np.repeat(np.repeat(up3[None, None], X.shape[0], 0), X.shape[1], 1)
            add('petal', grid(pts, hint=hint))
            pts2 = pts - up3 * 0.006
            add('petal', grid(pts2[:, ::-1], hint=-hint[:, ::-1]))
    # center: stamen cone
    prof = np.array([(0.0, 0.0), (R * 0.22, 0.0), (R * 0.25, R * 0.12), (R * 0.16, R * 0.22), (0.0, R * 0.26)])
    cone = revolve(resample_polyline(prof, 10)[0], 16)
    M = np.stack([fx, fz, -fy], 1)
    add('stamen', cone.transformed(M, c))


def bud(cx, cy, r_px, z, ang_deg):
    R = PX(r_px)
    prof = np.array([(0.0, -R * 1.1), (R * 0.55, -R * 0.8), (R * 0.75, -R * 0.1), (R * 0.55, R * 0.6), (R * 0.2, R * 1.05), (0.0, R * 1.2)])
    b = revolve(resample_polyline(catmull(prof, 6), 18)[0], 18)
    a = np.radians(ang_deg); up = np.array([np.cos(a), np.sin(a), 0.0]); side = np.array([-up[1], up[0], 0.0])
    M = np.stack([side, up, np.array([0, 0, 1.0])], 1)
    add('petal', b.transformed(M, np.r_[P(cx, cy), z]))
    for k in (-1, 1):
        sep_b = P(cx, cy) - up[:2] * R * 0.9
        sep_t = P(cx, cy) + (up[:2] * 0.3 + side[:2] * 0.5 * k) * R * 1.4
        # small green sepal leaves hugging the bud
    return


flower(370, 353, 66, 0.20, face=(0.25, 0.35, 1.0))
flower(951, 734, 60, 0.20, face=(-0.25, 0.35, 1.0))
for (bx, by, br, bz, ba) in ((397, 157, 16, 0.08, 60), (379, 215, 15, -0.05, 75), (225, 446, 16, 0.10, 100), (924, 803, 13, 0.18, 40)):
    bud(bx, by, br, bz, ba)


# ---------------- skeletons for Blender (stag, antlers, branches) ----------------
def sk(points):
    return [[float(v) for v in np.r_[P(x, y), z]] + [float(PX(r))] for (x, y, z, r) in points]


SKELETON = {
    'stag': {
        'spine': sk([(515, 567, 0, 44), (580, 550, 0, 50), (650, 520, 0, 53), (720, 490, 0, 54), (770, 478, 0, 52)]),
        'neck': sk([(770, 478, 0, 50), (790, 420, 0, 44), (800, 360, 0, 38), (805, 315, 0, 32), (808, 290, 0, 26)]),
        'head': sk([(808, 290, 0, 26), (835, 280, 0, 20), (862, 278, 0, 13), (886, 282, 0, 7)]),
        'tail': sk([(520, 555, 0, 11), (492, 545, 0, 9), (470, 540, 0, 6), (461, 532, 0, 3)]),
        'hind_near': sk([(525, 590, 0.11, 38), (495, 640, 0.12, 24), (455, 700, 0.12, 13), (415, 770, 0.12, 9), (380, 824, 0.12, 7)]),
        'hind_far': sk([(570, 600, -0.11, 34), (565, 650, -0.12, 21), (585, 700, -0.12, 12), (570, 735, -0.12, 9), (561, 757, -0.12, 7)]),
        'fore_raised': sk([(790, 520, 0.10, 28), (850, 530, 0.11, 17), (906, 540, 0.11, 12), (880, 600, 0.11, 9), (851, 664, 0.11, 7)]),
        'fore_down': sk([(765, 530, -0.10, 28), (752, 590, -0.11, 16), (738, 640, -0.11, 11), (728, 675, -0.11, 8), (724, 699, -0.11, 7)]),
    },
    'ears': [sk([(790, 282, 0.07, 6), (745, 284, 0.09, 9), (700, 284, 0.10, 2)]), sk([(790, 282, -0.07, 6), (750, 288, -0.09, 9), (708, 290, -0.10, 2)])],
    'antlers': [
        sk([(788, 250, 0.09, 9), (740, 236, 0.10, 8.5), (680, 226, 0.10, 8), (620, 222, 0.11, 7.5), (560, 226, 0.11, 7), (515, 236, 0.11, 6.5),
            (485, 246, 0.11, 6), (465, 232, 0.11, 5.5), (458, 200, 0.11, 5), (466, 170, 0.11, 4), (488, 146, 0.11, 2.5)]),
        sk([(780, 258, -0.09, 9), (730, 252, -0.10, 8.5), (670, 250, -0.11, 8), (610, 254, -0.11, 7.5), (555, 262, -0.12, 7), (505, 272, -0.12, 6),
            (475, 280, -0.12, 4.5), (452, 286, -0.12, 2.5)]),
        sk([(790, 245, 0.09, 8), (795, 200, 0.09, 7), (803, 150, 0.09, 5.5), (810, 115, 0.09, 4), (815, 88, 0.09, 2)]),
        sk([(768, 252, -0.09, 7.5), (762, 210, -0.09, 6.5), (758, 170, -0.09, 5), (760, 134, -0.09, 2)]),
        sk([(690, 227, 0.10, 6), (685, 200, 0.10, 5), (690, 175, 0.10, 3.5), (700, 160, 0.10, 1.8)]),
        sk([(600, 223, 0.11, 6), (592, 195, 0.11, 5), (596, 172, 0.11, 3.5), (608, 158, 0.11, 1.8)]),
        sk([(640, 252, -0.11, 5.5), (632, 226, -0.11, 4.5), (636, 205, -0.11, 3), (645, 192, -0.11, 1.5)]),
        sk([(560, 262, -0.12, 5), (548, 238, -0.12, 4), (550, 218, -0.12, 2.5), (560, 205, -0.12, 1.5)]),
    ],
    'branches': [
        sk([(215, 575, 0.0, 12), (222, 530, 0.02, 11), (255, 455, 0.05, 10), (306, 388, 0.08, 9), (340, 312, 0.08, 8.5), (370, 240, 0.08, 8),
            (420, 160, 0.06, 7), (470, 122, 0.05, 6), (540, 106, 0.04, 5), (610, 98, 0.03, 4), (690, 96, 0.03, 2.5)]),
        sk([(430, 150, 0.06, 4), (410, 152, 0.07, 3), (397, 158, 0.08, 2.5)]),
        sk([(372, 236, 0.08, 4.5), (376, 224, 0.0, 3.5), (379, 215, -0.05, 3)]),
        sk([(240, 480, 0.04, 5), (228, 462, 0.07, 4), (225, 450, 0.10, 3)]),
        sk([(290, 405, 0.07, 5.5), (240, 382, 0.08, 4.5), (200, 372, 0.10, 3)]),
        sk([(330, 395, 0.08, 6), (370, 368, 0.14, 5), (430, 400, 0.14, 5), (500, 420, 0.10, 4), (560, 432, 0.06, 3), (606, 436, 0.05, 2)]),
        sk([(379, 795, 0.20, 7), (360, 720, 0.15, 6), (340, 660, 0.12, 5), (322, 610, 0.10, 4), (315, 572, 0.10, 3)]),
        sk([(815, 895, 0.22, 8), (860, 870, 0.20, 7), (905, 840, 0.20, 7), (940, 800, 0.20, 6), (960, 760, 0.18, 6), (975, 720, 0.15, 5),
            (987, 676, 0.12, 4), (995, 640, 0.10, 3)]),
        sk([(940, 800, 0.20, 4), (924, 810, 0.19, 3)]),
    ],
}


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
