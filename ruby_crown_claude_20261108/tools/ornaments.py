"""Crown ornaments: rhombus ruby settings, arch stones, circlet beads, scrolls and stones,
acanthus fronds, hub stones and a four sided fleur de lis.

All functions return dicts of material -> list of Parts.
"""
import numpy as np
from meshkit import Part, merge, unit, grid, sweep, cap, catmull, resample_polyline, gem, frame_on_surface, ngon, rhombus, orient
import crown as K


def radial_frame(th):
    out = np.array([np.sin(th), 0.0, np.cos(th)])
    x = np.array([np.cos(th), 0.0, -np.sin(th)])
    return x, np.array([0.0, 1.0, 0.0]), out


def add(d, mat, p):
    d.setdefault(mat, []).append(p)


# ---------------- polygon rings (mitred) ----------------
def polygon_ring(corners2d, profile, ex, ey, ez, origin, back_fn=None, mapping=None):
    """Sweep a (d, h) profile around a closed polygon with mitred corners.

    d: inward offset from the outline, h: height along ez. corners2d (k, 2) counterclockwise.
    back_fn(point3d) -> extra depth for profile points with h < 0 (reach back to a surface).
    """
    c = np.asarray(corners2d, float); k = len(c)
    parts = []
    prof = np.asarray(profile, float)
    for i in range(k):
        p0, p1 = c[i], c[(i + 1) % k]
        prev, nxt = c[i - 1], c[(i + 2) % k]
        def inward_dir(a, b):
            e = unit(b - a); return np.array([-e[1], e[0]])  # left normal (inside for counterclockwise)
        n_e = inward_dir(p0, p1)
        n_prev = inward_dir(prev, p0); n_next = inward_dir(p1, nxt)
        def mitre(nA, nB):
            b = unit(nA + nB); return b / max(np.dot(b, nA), 0.2)
        m0 = mitre(n_prev, n_e); m1 = mitre(n_e, n_next)
        rows = []
        for (dd, hh) in prof:
            q0 = p0 + m0 * dd; q1 = p1 + m1 * dd
            seg = np.array([q0, q1])
            if mapping is not None:
                P = np.array([mapping(q[0], q[1], hh) for q in np.linspace(q0, q1, 6)])
            else:
                P = origin + seg[:, 0:1] * ex + seg[:, 1:2] * ey + max(hh, 0.0) * ez
                if hh < 0:
                    P = np.array([q - ez * (back_fn(q) if back_fn is not None else -hh) for q in P])
            rows.append(P)
        P = np.array(rows)  # (m, 2, 3)
        t = np.gradient(prof, axis=0)
        n2 = np.stack([-t[:, 1], t[:, 0]], -1)          # outward in (d, h)
        in3 = n_e[0] * ex + n_e[1] * ey
        H = np.repeat((n2[:, 0:1] * in3 + n2[:, 1:2] * ez)[:, None, :], P.shape[1], 1)
        parts.append(grid(P, hint=H))
    return merge(parts)


def offset_polygon(corners2d, d):
    c = np.asarray(corners2d, float); k = len(c); out = []
    for i in range(k):
        prev, p, nxt = c[i - 1], c[i], c[(i + 1) % k]
        def inward(a, b):
            e = unit(b - a); return np.array([-e[1], e[0]])
        nA, nB = inward(prev, p), inward(p, nxt)
        b = unit(nA + nB); out.append(p + b / max(np.dot(b, nA), 0.2) * d)
    return np.array(out)


def points_along_polygon(corners2d, n_per_edge):
    c = np.asarray(corners2d, float); k = len(c); pts = []
    for i in range(k):
        for t in (np.arange(n_per_edge) + 0.5) / n_per_edge:
            pts.append(c[i] * (1 - t) + c[(i + 1) % k] * t)
    return np.array(pts)


# ---------------- big rhombus settings ----------------
RH_W, RH_H, RH_Y, RH_R = 1.87, 2.20, -0.66, 2.96


def rhombus_setting(th):
    """Big ruby setting wrapped on a cylinder of radius RH_R so it hugs the crown from every angle."""
    d = {}
    ex, ey, ez = radial_frame(th)
    def mapping(x, y, h):
        a = th + x / RH_R
        return np.array([(RH_R + h) * np.sin(a), RH_Y + y, (RH_R + h) * np.cos(a)])
    outer = np.array([[RH_W / 2, 0], [0, RH_H / 2], [-RH_W / 2, 0], [0, -RH_H / 2]])  # counterclockwise seen from +ez
    # lower frame whose outer edge slopes down to the velvet (a bevel from the side, not a slab)
    prof = [(-0.09, -0.10), (0.0, 0.03), (0.012, 0.08), (0.04, 0.10), (0.062, 0.095), (0.072, 0.07), (0.072, 0.05),
            (0.178, 0.05), (0.182, 0.08), (0.196, 0.10), (0.222, 0.095), (0.236, 0.07), (0.236, -0.10)]
    add(d, 'gold', polygon_ring(outer, prof, ex, ey, ez, None, mapping=mapping))
    inner = offset_polygon(outer, 0.236)
    plate = np.array([mapping(p[0], p[1], -0.03) for p in inner])
    add(d, 'gold', cap(plate, ez))
    mid = offset_polygon(outer, 0.125)
    for p in points_along_polygon(mid, 12):
        a = th + p[0] / RH_R
        fz = np.array([np.sin(a), 0, np.cos(a)]); fx = np.array([np.cos(a), 0, -np.sin(a)])
        add(d, 'clear', gem(ngon(8, 0.042), [(0.55, 0.028)], 0.042, np.stack([fx, ey, fz], 1), mapping(p[0], p[1], 0.05)))
    ruby_out = offset_polygon(outer, 0.244)
    k16 = []
    for i in range(4):
        a_, b_ = ruby_out[i], ruby_out[(i + 1) % 4]
        for t in (0, 0.25, 0.5, 0.75):
            k16.append(a_ * (1 - t) + b_ * t)
    frame = np.stack([ex, ey, ez], 1)
    add(d, 'ruby', gem(np.array(k16), [(0.82, 0.085), (0.58, 0.16), (0.32, 0.205)], 0.215, frame, mapping(0, 0, 0.0)))
    return d


# ---------------- small rhombus settings on the circlet ----------------
def band_setting(th, w=0.26, h=0.34, y=-2.09, r=K.R_BAND):
    d = {}
    ex, ey, ez = radial_frame(th)
    origin = r * ez + y * ey
    outer = np.array([[w / 2 + 0.05, 0], [0, h / 2 + 0.06], [-w / 2 - 0.05, 0], [0, -h / 2 - 0.06]])
    prof = [(0.0, -0.03), (0.0, 0.03), (0.012, 0.05), (0.04, 0.05), (0.055, 0.035), (0.055, 0.0)]
    add(d, 'gold', polygon_ring(outer, prof, ex, ey, ez, origin))
    ro = offset_polygon(outer, 0.058)
    k8 = []
    for i in range(4):
        k8.append(ro[i]); k8.append((ro[i] + ro[(i + 1) % 4]) / 2)
    add(d, 'ruby', gem(np.array(k8), [(0.6, 0.05), (0.3, 0.08)], 0.095, np.stack([ex, ey, ez], 1), origin))
    return d


# ---------------- circlet beads and scrolls ----------------
def bead_rows(n=240, ys=(-2.288, -1.888), r=2.918 * K.CSCALE, rad=0.021):
    parts = []
    # octahedral bead, smooth shaded
    oct_v = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], float)
    oct_t = np.array([[0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4], [2, 0, 5], [1, 2, 5], [3, 1, 5], [0, 3, 5]])
    for y in ys:
        for i in range(n):
            th = 2 * np.pi * (i + 0.5 * (y > -2)) / n
            c = np.array([r * np.sin(th), y, r * np.cos(th)])
            parts.append(orient(Part(c + oct_v * rad, oct_v.copy(), oct_t)))
    return merge(parts)


def band_point(th, y, lift, r=K.R_BAND):
    return np.array([(r + lift) * np.sin(th), y, (r + lift) * np.cos(th)])


def band_scrolls(n_seg=8):
    parts = []
    L = 2 * np.pi / n_seg
    # one C-scroll in local (u in radians from the gem, v height offset from band center y -2.09)
    ctrl = np.array([(0.075, -0.035), (0.13, 0.06), (0.21, 0.09), (0.29, 0.04), (0.33, -0.04), (0.31, -0.10),
                     (0.27, -0.09), (0.26, -0.05), (0.285, -0.04)])
    path = resample_polyline(catmull(ctrl, 10), 34)[0]
    prof = np.array([(-0.034, 0.0), (0.034, 0.0), (0.024, 0.026), (0.0, 0.038), (-0.024, 0.026)])
    for k in range(n_seg):
        for side in (1, -1):
            ths = (k * L) + path[:, 0] if side > 0 else ((k + 1) * L) - path[:, 0]
            C = np.array([band_point(t, -2.09 + v, 0.0) for t, v in zip(ths, path[:, 1])])
            O = np.array([[np.sin(t), 0, np.cos(t)] for t in ths])
            T = unit(np.gradient(C, axis=0)); A = unit(np.cross(T, O))
            taper = np.clip(1.15 - np.linspace(0, 1, len(C)) * 0.5, 0.5, 1)
            parts.append(sweep(C, A, O, prof, scale_a=taper, scale_o=taper))
    return merge(parts)


# ---------------- arch stones ----------------
def arch_stones(th, major):
    d = {}
    C, A, O, w = K.arch(th)[1]
    s = K.ARCH_S
    pos = [0.60, 0.70, 0.80] if major else [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]
    for i, sp in enumerate(pos):
        j = int(round(sp * (len(C) - 1)))
        T = unit(C[min(j + 1, len(C) - 1)] - C[max(j - 1, 0)])
        frame = np.stack([A[j], T, O[j]], 1)
        floor = w[j] - 0.065
        origin = C[j] + O[j] * 0.07
        if i % 2 == 0:
            hw = min(0.13, floor * 0.92)
            add(d, 'ruby', gem(rhombus(hw * 2, hw * 2.7), [(0.6, 0.04), (0.3, 0.065)], 0.08, frame, origin))
        else:
            rr = min(0.10, floor * 0.85)
            add(d, 'clear', gem(ngon(8, rr), [(0.55, 0.035)], 0.055, frame, origin))
    return d


# ---------------- acanthus fronds ----------------
def frond(th0, side, ctrl, w0, lift0, lift1, n=22, lobes=5, cup=0.6):
    """A pointed, lobed leaf following ctrl (arc offset along the circumference, y) over the velvet."""
    path = resample_polyline(catmull(np.asarray(ctrl, float), 10), n)[0]
    pts, nrms = [], []
    for (xa, y) in path:
        r_guess = np.interp(y, K.ARCH2D[:, 1], K.ARCH2D[:, 0]) + 0.10
        th = th0 + side * xa / max(r_guess, 0.5)
        p, nrm = K.velvet_surface(th, max(y, -1.69))
        if y < -1.69:
            p = np.array([2.95 * K.CSCALE * np.sin(th), y, 2.95 * K.CSCALE * np.cos(th)])
            nrm = unit(np.array([np.sin(th), 0.25, np.cos(th)]))
        pts.append(p); nrms.append(nrm)
    pts = np.array(pts); nrms = np.array(nrms)
    s = np.linspace(0, 1, n)
    lift = lift0 + (lift1 - lift0) * s ** 1.5
    C = pts + nrms * lift[:, None]
    T = unit(np.gradient(C, axis=0)); O = unit(nrms - np.sum(nrms * T, -1, keepdims=True) * T); A = unit(np.cross(T, O))
    taper = np.sin(np.pi * np.clip(s * 0.5 + 0.08, 0, 0.5)) * (1 - s) ** 0.6 + 0.02
    width = w0 * taper * (1 + 0.45 * np.abs(np.sin(lobes * np.pi * s)) ** 0.7)
    prof = np.array([(-1, 0.25 * cup), (-0.5, -0.35), (0.5, -0.35), (1, 0.25 * cup), (0.5, 0.65), (-0.5, 0.65)], float)
    prof = prof * [1, 0.05]
    return sweep(C, A, O, prof, scale_a=width, scale_o=np.clip(taper * 1.6, 0.45, 1.2))


FROND_MAIN = [(0.10, -1.72), (0.22, -1.48), (0.36, -1.16), (0.48, -0.86), (0.52, -0.62), (0.44, -0.48), (0.33, -0.50), (0.29, -0.60)]
FROND_LOW = [(0.12, -1.72), (0.34, -1.62), (0.60, -1.48), (0.80, -1.30), (0.86, -1.10), (0.78, -1.00), (0.69, -1.06)]
FROND_MID = [(0.12, -1.70), (0.28, -1.52), (0.48, -1.30), (0.64, -1.08), (0.72, -0.86)]


def acanthus(th, major):
    d = {}
    shift = 0.45 if major else 0.0
    for side in (1, -1):
        for ctrl, w0, l1 in ((FROND_MAIN, 0.20, 0.20), (FROND_LOW, 0.17, 0.16), (FROND_MID, 0.13, 0.10)):
            add(d, 'gold', frond(th, side, [(x + shift, y) for x, y in ctrl], w0, 0.03, l1))
    return d


# ---------------- hub stones and fleur de lis ----------------
def hub_stones():
    d = {}
    for k in range(4):
        th = k * np.pi / 2
        ex, ey, ez = radial_frame(th)
        nrm = unit(ez * 0.82 + ey * 0.57)  # bell surface normal near y 1.47
        frame = frame_on_surface(nrm)
        origin = 0.36 * ez + 1.475 * ey
        ring_out = ngon(16, 0.105)
        prof = [(0.0, -0.02), (0.0, 0.03), (0.01, 0.045), (0.03, 0.045), (0.035, 0.03), (0.035, 0.0)]
        add(d, 'gold', polygon_ring(ring_out, prof, frame[:, 0], frame[:, 1], frame[:, 2], origin))
        add(d, 'ruby', gem(ngon(8, 0.072), [(0.55, 0.045)], 0.075, frame, origin + frame[:, 2] * 0.0))
    return d


def fleur():
    d = {}
    from meshkit import revolve
    collar = [(0.12, 2.02), (0.185, 2.03), (0.20, 2.06), (0.20, 2.13), (0.185, 2.16), (0.12, 2.17)]
    add(d, 'gold', revolve(resample_polyline(catmull(collar, 6), 14)[0], 48))
    for k in range(4):
        th = k * np.pi / 2
        ex, ey, ez = radial_frame(th)
        add(d, 'ruby', gem(ngon(8, 0.075), [(0.55, 0.045)], 0.075, np.stack([ex, ey, ez], 1), 0.20 * ez + 2.095 * ey))
    petal = [(0.10, 2.20), (0.26, 2.40), (0.46, 2.56), (0.66, 2.61), (0.84, 2.53), (0.94, 2.37), (0.93, 2.21), (0.87, 2.12), (0.82, 2.17)]
    curl = [(0.12, 2.05), (0.24, 2.02), (0.33, 1.94), (0.33, 1.86), (0.27, 1.84), (0.25, 1.89)]
    lens = np.array([(-1, 0), (-0.6, -0.55), (0, -0.7), (0.6, -0.55), (1, 0), (0.6, 0.55), (0, 0.7), (-0.6, 0.55)], float)
    for k in range(4):
        th = np.pi / 4 + k * np.pi / 2
        for ctrl, wprof, t0 in ((petal, (0.12, 0.15, 0.13, 0.03), 0.065), (curl, (0.055, 0.055, 0.045, 0.015), 0.04)):
            path = resample_polyline(catmull(np.array(ctrl), 10), 30)[0]
            C = np.stack([path[:, 0] * np.sin(th), path[:, 1], path[:, 0] * np.cos(th)], -1)
            A = np.repeat(np.array([[np.cos(th), 0, -np.sin(th)]]), len(C), 0)
            T = unit(np.gradient(C, axis=0)); O = unit(np.cross(A, T))
            s_ = np.linspace(0, 1, len(C))
            wa = np.interp(s_, [0, 0.35, 0.7, 1.0], wprof)
            # a fleur de lis is a flat ornament: width lies in the petal's own plane (O), thickness across it (A)
            add(d, 'gold', sweep(C, A, O, lens * [t0, 1], scale_a=0.6 + 0.4 * wa / max(wprof), scale_o=wa))
    return d
