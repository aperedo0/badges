"""Ruby Crown round 2 geometry (model units, Y up, front +Z, theta from +Z toward +X).

Usage: crown2.py OUT.npz [velvet_texture.png]
Rebuilt after the fresh review of version 6: wide low crown, arches standing off pleated
velvet, front and back ruby frames, sculpted leafwork, dark frieze, bigger finial.
Materials: gold, gold_leaf, gold_satin, frieze, velvet (with st UVs), ruby, clear.
"""
import sys
import numpy as np
TOOLS = '/Users/antonioperedo/Desktop/badges/ruby_crown_claude_20261108/tools'
sys.path.insert(0, TOOLS)
from meshkit import Part, merge, unit, grid, revolve, sweep, cap, catmull, resample_polyline, gem, ngon, orient
from ornaments import polygon_ring, offset_polygon, points_along_polygon, radial_frame, bead_rows
import crown as K
K.R_BAND = 2.78

BOTTOM, TIP = -2.455, 2.85
RMAX = 3.35
N_ARCH = 8
ARCH_TH = [k * np.pi / 4 for k in range(8)]
STRAP_TH = (0.0, np.pi)


def add(d, mat, p):
    d.setdefault(mat, []).append(p)


def ball(c, r, n=10):
    a = np.linspace(-np.pi / 2, np.pi / 2, n)
    prof = np.c_[r * np.cos(a), r * np.sin(a)]
    p = revolve(prof, 2 * n)
    return Part(p.V + np.asarray(c), p.N, p.T)


# ---------------- velvet ----------------
_vc = catmull([(2.70, -1.95), (2.74, -1.72), (2.82, -1.30), (2.89, -0.75), (2.92, -0.15), (2.80, 0.28),
               (2.54, 0.50), (2.16, 0.64), (1.70, 0.74), (1.10, 0.82), (0.50, 0.86), (0.0, 0.87)], 12)
VB, _ = resample_polyline(_vc, 64)
_vt = unit(np.gradient(VB, axis=0)); VN2 = np.stack([_vt[:, 1], -_vt[:, 0]], -1)
VT = np.linspace(0, 1, len(VB))
N_PLEAT = 16


def pleat(th):
    """+1 on a fold ridge, -1 in a crease; rounded ridges, sharp creases, slightly irregular spacing and depth."""
    phase = N_PLEAT * (th + 0.035 * np.sin(3 * th + 0.4) + 0.02 * np.sin(7 * th + 1.1))
    amp = 0.85 + 0.15 * np.sin(5 * th + 0.7)
    return amp * (2 * np.abs(np.cos((phase + np.pi) / 2)) - 1)


def velvet_disp(th, k):
    t = VT[k]; y = VB[k, 1]
    side = np.clip((y + 1.75) / 0.45, 0, 1) * np.clip((0.87 - y) / 0.25, 0, 1)
    top = np.clip((VB[k, 0] - 0.45) / 0.8, 0, 1) * (y > 0.55)
    fold_amp = 0.11 * np.maximum(side, 0.8 * top)
    pinch = np.cos(4 * th) ** 2
    puff = 0.04 * side * (1 - pinch)
    under_arch = -0.10 * side * pinch ** 6
    dth = np.angle(np.exp(1j * th * 2)) / 2          # angle to the nearest strap (0 or pi)
    window = np.exp(-(dth / 0.38) ** 4) * np.clip((y + 1.9) / 0.2, 0, 1) * np.clip((0.42 - y) / 0.2, 0, 1)
    strap_band = np.exp(-(dth * np.maximum(VB[k, 0], 0.3) / 0.36) ** 4) * (y > 0.2)
    window = np.maximum(window, strap_band)
    d = (fold_amp * pleat(th) + puff + under_arch) * (1 - window) - 0.06 * window * (y <= 0.2)
    return d


def velvet_point(th, k):
    d = velvet_disp(th, k)
    rr = VB[k, 0] + d * VN2[k, 0]; yy = VB[k, 1] + d * VN2[k, 1]
    return np.stack([rr * np.sin(th), yy, rr * np.cos(th)], -1)


def velvet(n=192):
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    K_, TH = np.meshgrid(np.arange(len(VB)), th, indexing='ij')
    P = velvet_point(TH, K_)
    Pu = np.gradient(P, axis=0)
    Pv = (np.roll(P, -1, 1) - np.roll(P, 1, 1)) / 2
    N = unit(np.cross(Pu, Pv))
    out = np.stack([np.sin(TH), np.zeros_like(TH), np.cos(TH)], -1)
    hint = out * (VB[K_, 0][..., None] > 0.05) + np.array([0, 1.0, 0]) * (VB[K_, 0][..., None] <= 0.05)
    N = np.where((np.sum(N * hint, -1) < 0)[..., None], -N, N)
    N[np.linalg.norm(np.cross(Pu, Pv), axis=-1) < 1e-9] = (0, 1, 0)
    # open the seam: duplicate the first column at u = 1
    P = np.concatenate([P, P[:, :1]], 1); N = np.concatenate([N, N[:, :1]], 1)
    u = np.linspace(0, 1, n + 1)
    UV = np.stack(np.meshgrid(u, VT, indexing='xy'), -1)
    nu, nv = P.shape[:2]
    idx = np.arange(nu * nv).reshape(nu, nv)
    T = []
    for i in range(nu - 1):
        for j in range(nv - 1):
            a, b, c, dd = idx[i, j], idx[i, j + 1], idx[i + 1, j + 1], idx[i + 1, j]
            T += [(a, b, c), (a, c, dd)]
    return orient(Part(P.reshape(-1, 3), N.reshape(-1, 3), np.array(T), UV.reshape(-1, 2)))


def velvet_texture(path, w=1024, h=128):
    from PIL import Image
    th = np.linspace(0, 2 * np.pi, w, endpoint=False)
    t = np.linspace(0, 1, h)
    ridge = (pleat(th) + 1) / 2                                  # 0 in creases, 1 on ridges
    k = np.clip((t * (len(VB) - 1)).round().astype(int), 0, len(VB) - 1)
    y = VB[k, 1]
    fold_w = np.clip((y + 1.75) / 0.45, 0, 1)[:, None] * np.clip((0.85 - y) / 0.3, 0.25, 1)[:, None]
    shade = 1 - fold_w * (1 - (0.14 + 0.86 * np.clip(ridge[None, :], 0, 1) ** 0.8))
    base_shadow = 0.45 + 0.55 * np.clip((y + 1.75) / 0.5, 0, 1)
    f = shade * base_shadow[:, None]
    base = np.array([0.085, 0.0018, 0.008])
    lin = base[None, None, :] * f[..., None]
    srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * np.power(lin, 1 / 2.4) - 0.055)
    img = (np.clip(srgb, 0, 1) * 255).round().astype(np.uint8)[::-1]   # row 0 = top of the texture = v 1
    Image.fromarray(img).save(path)


# ---------------- arches ----------------
def _arch_path(ctrl):
    a2, _ = resample_polyline(catmull(ctrl, 14), 100)
    t = unit(np.gradient(a2, axis=0))
    return a2, np.stack([t[:, 1], -t[:, 0]], -1)


ARCH_PATHS = {
    'diag': _arch_path([(2.80, -1.72), (2.85, -1.40), (2.96, -0.95), (3.08, -0.45), (3.15, -0.05), (3.09, 0.30), (2.90, 0.56),
                        (2.58, 0.72), (2.18, 0.84), (1.78, 0.92), (1.30, 0.97), (0.80, 0.99), (0.28, 0.99)]),
    'side': _arch_path([(2.80, -1.72), (2.85, -1.40), (2.96, -0.95), (3.08, -0.45), (3.15, -0.05), (3.08, 0.28), (2.88, 0.52),
                        (2.56, 0.68), (2.16, 0.80), (1.76, 0.88), (1.28, 0.95), (0.78, 0.98), (0.28, 0.99)]),
}
ARCH2D, ARCH_N2 = ARCH_PATHS['diag']
ARCH_S = np.linspace(0, 1, len(ARCH2D))
SY = 0.89          # final vertical squeeze: the width is capped at 6.7, so height follows the mockup's 1.27 ratio


def arch_frames(th):
    global ARCH2D, ARCH_N2
    C = np.stack([ARCH2D[:, 0] * np.sin(th), ARCH2D[:, 1], ARCH2D[:, 0] * np.cos(th)], -1)
    O = np.stack([ARCH_N2[:, 0] * np.sin(th), ARCH_N2[:, 1], ARCH_N2[:, 0] * np.cos(th)], -1)
    A = np.repeat(np.array([[np.cos(th), 0, -np.sin(th)]]), len(C), 0)
    T = unit(np.gradient(C, axis=0))
    return C, A, O, T


def arch_width(s):
    return 0.24 - 0.08 * np.clip((s - 0.66) / 0.3, 0, 1)


def arch_profile(thick_side):
    """Unit width profile (a in -1..1 times half width, o absolute): thick rail on thick_side (+1/-1), 0 = both medium."""
    def rail(a_edge, inward, rad, h):
        ang = np.linspace(0, np.pi, 7)
        c = a_edge - inward * rad
        return [(c + inward * rad * np.cos(t_), h - rad + rad * np.sin(t_)) for t_ in ang]
    rt = {1: 0.30, -1: 0.30, 0: 0.24}
    big, small = 0.075, 0.05
    rr = big if thick_side == 1 else small if thick_side == -1 else 0.06
    rl = big if thick_side == -1 else small if thick_side == 1 else 0.06
    pts = [(-1.0, 0.0), (1.0, 0.0), (1.0, 0.10)]
    # right rail from the outer edge over to the channel (a in units of half width 0.2)
    for t_ in np.linspace(0, np.pi, 7):
        pts.append((1.0 - (rr / 0.2) * (1 - np.cos(t_)), 0.10 + rr * np.sin(t_) * 0.9))
    pts.append((1.0 - 2 * rr / 0.2, 0.085))
    pts.append((-1.0 + 2 * rl / 0.2, 0.085))
    for t_ in np.linspace(np.pi, 0, 7):
        pts.append((-1.0 + (rl / 0.2) * (1 - np.cos(t_)), 0.10 + rl * np.sin(t_) * 0.9))
    pts.append((-1.0, 0.10))
    return np.array(pts)


def use_path(kind):
    global ARCH2D, ARCH_N2
    ARCH2D, ARCH_N2 = ARCH_PATHS[kind]


def arch(th, thick_side):
    C, A, O, T = arch_frames(th)
    w = arch_width(ARCH_S)
    prof = arch_profile(thick_side)
    # split: the rails and walls are polished gold, the channel floor is satin
    P = C[None] + (prof[:, 0][:, None] * w[None, :])[..., None] * A[None] + prof[:, 1][:, None, None] * O[None]
    P = np.concatenate([P, P[:1]], 0)
    pr = np.vstack([prof, prof[:1]])
    t = np.gradient(pr, axis=0); n2 = np.stack([t[:, 1], -t[:, 0]], -1)
    H = n2[:, 0][:, None, None] * A[None] + n2[:, 1][:, None, None] * O[None]
    g = grid(P, hint=H)
    ends = []
    for i in (0, -1):
        loop = C[i] + np.outer(prof[:, 0] * w[i], A[i]) + np.outer(prof[:, 1], O[i])
        ends.append(cap(loop, unit(C[i] - C[i + (1 if i == 0 else -1)])))
    return merge([g] + ends), (C, A, O, T, w)


def arch_index_at_y(y, upper=False):
    idx = np.arange(len(ARCH2D))
    top = int(np.argmax(ARCH2D[:, 1]))
    sel = idx[top:] if upper else idx[:top + 1]
    return int(sel[np.argmin(np.abs(ARCH2D[sel, 1] - y))])


def arch_stones(th, thick_side, frames):
    d = {}
    C, A, O, T, w = frames
    rubies = [arch_index_at_y(-0.35), arch_index_at_y(0.55), int(np.argmax(ARCH2D[:, 1])) - 6]
    whites = [arch_index_at_y(-0.70), arch_index_at_y(0.05), arch_index_at_y(0.25), arch_index_at_y(0.85), int(np.argmax(ARCH2D[:, 1])) + (len(ARCH2D) - int(np.argmax(ARCH2D[:, 1]))) // 2]
    for j in rubies:
        ex, ey, ez = A[j], T[j], O[j]
        origin = C[j] + ez * 0.085
        hw, hh = 0.16, 0.21
        outer = np.array([[hw, 0], [0, hh], [-hw, 0], [0, -hh]])
        prof = [(0.0, 0.0), (0.0, 0.07), (0.012, 0.095), (0.035, 0.10), (0.05, 0.08), (0.05, 0.03)]
        add(d, 'gold', polygon_ring(outer, prof, ex, ey, ez, origin))
        add(d, 'gold', cap(np.array([origin + p[0] * ex + p[1] * ey + 0.03 * ez for p in offset_polygon(outer, 0.05)]), ez))
        ro = offset_polygon(outer, 0.05)
        k8 = np.array([q for i in range(4) for q in (ro[i], (ro[i] + ro[(i + 1) % 4]) / 2)])
        add(d, 'ruby', gem(k8, [(0.66, 0.025), (0.34, 0.04)], 0.048, np.stack([ex, ey, ez], 1), origin + ez * 0.03))
    for j in whites:
        ex, ey, ez = A[j], T[j], O[j]
        r = min(0.062, w[j] * 0.36)
        origin = C[j] + ez * 0.085
        add(d, 'gold', polygon_ring(ngon(14, r + 0.022), [(0, 0.0), (0, 0.035), (0.01, 0.045), (0.022, 0.035), (0.022, 0.0)], ex, ey, ez, origin))
        add(d, 'clear', gem(ngon(10, r), [(0.62, 0.38 * r)], 0.55 * r, np.stack([ex, ey, ez], 1), origin + ez * 0.005))
    if thick_side == 0:
        return d
    # crest knob: three polished balls on the thick rail where the arch turns over (r about 1.9)
    j = int(np.argmin(np.abs(ARCH2D[:, 0] - 1.9) + 10 * (ARCH2D[:, 1] < 0.5)))
    side = thick_side if thick_side != 0 else 1
    base = C[j] + O[j] * 0.13 + A[j] * side * w[j] * 0.55
    add(d, 'gold', ball(base + O[j] * 0.07, 0.085))
    add(d, 'gold', ball(base + O[j] * 0.035 + T[j] * 0.11, 0.06))
    add(d, 'gold', ball(base + O[j] * 0.035 - T[j] * 0.11, 0.06))
    return d


# ---------------- straps (front and back) ----------------
def strap_path(th):
    ks = np.arange(len(VB))
    sel = (VB[:, 0] > 0.30) & (VB[:, 1] > 0.24)
    k = ks[sel][::-1]                       # from the bell outward and down
    P = velvet_point(np.full(len(k), th), k)
    nrm = np.stack([VN2[k, 0] * np.sin(th), VN2[k, 1], VN2[k, 0] * np.cos(th)], -1)
    C, _ = resample_polyline(P + nrm * 0.02, 70)
    O = unit(np.array([nrm[np.argmin(np.linalg.norm(P - c, axis=1))] for c in C]))
    T = unit(np.gradient(C, axis=0))
    A = np.repeat(np.array([[np.cos(th), 0, -np.sin(th)]]), len(C), 0)
    O = unit(np.cross(T, A)); O = np.where((np.sum(O * nrm[:1], -1) < 0)[:, None], -O, O)
    return C, A, O, T


def strap(th):
    d = {}
    C, A, O, T = strap_path(th)
    prof = np.array([(-0.30, 0), (0.30, 0), (0.30, 0.05), (0.285, 0.09), (0.25, 0.105), (0.215, 0.09), (0.20, 0.05),
                     (-0.20, 0.05), (-0.215, 0.09), (-0.25, 0.105), (-0.285, 0.09), (-0.30, 0.05)])
    add(d, 'gold', sweep(C, A, O, prof))
    # satin engraved panel (raised lyre scrolls) in the lower channel
    j0 = int(len(C) * 0.72)
    for sgn in (1, -1):
        ctrl = np.array([(0.0, 0.0), (0.09 * sgn, 0.05), (0.13 * sgn, 0.16), (0.07 * sgn, 0.24), (0.02 * sgn, 0.20), (0.05 * sgn, 0.15)])
        path = resample_polyline(catmull(ctrl, 8), 24)[0]
        jj = np.clip((j0 - path[:, 1] / np.linalg.norm(C[1] - C[0])).astype(int), 0, len(C) - 1)
        P = np.array([C[j] + A[j] * x + O[j] * 0.05 for j, (x, _) in zip(jj, path)])
        Tn = unit(np.gradient(P, axis=0)); On = O[jj]; An = unit(np.cross(Tn, On))
        add(d, 'gold', sweep(P, An, On, np.array([(-0.018, 0), (0.018, 0), (0.012, 0.025), (-0.012, 0.025)])))
    # stones: strap ruby, white column and one white below
    def at(frac):
        j = int(np.clip(frac * (len(C) - 1), 0, len(C) - 1)); return C[j], A[j], T[j], O[j]
    c, ex, ey, ez = at(0.50)
    origin = c + ez * 0.05; ey = -ey
    outer = np.array([[0.17, 0], [0, 0.22], [-0.17, 0], [0, -0.22]])
    add(d, 'gold', polygon_ring(outer, [(0, 0), (0, 0.07), (0.012, 0.095), (0.035, 0.10), (0.05, 0.08), (0.05, 0.03)], ex, ey, ez, origin))
    ro = offset_polygon(outer, 0.05)
    k8 = np.array([q for i in range(4) for q in (ro[i], (ro[i] + ro[(i + 1) % 4]) / 2)])
    add(d, 'ruby', gem(k8, [(0.62, 0.04), (0.3, 0.06)], 0.075, np.stack([ex, ey, ez], 1), origin + ez * 0.03))
    for frac, r in ((0.18, 0.05), (0.26, 0.05), (0.66, 0.065)):
        c, ex, ey, ez = at(frac)
        add(d, 'clear', gem(ngon(10, r), [(0.62, 0.38 * r)], 0.55 * r, np.stack([ex, -ey, ez], 1), c + ez * 0.05))
    c, ex, ey, ez = at(0.34)
    add(d, 'clear', gem(np.array([[0.05, 0], [0, 0.07], [-0.05, 0], [0, -0.07]]), [(0.5, 0.025)], 0.04, np.stack([ex, -ey, ez], 1), c + ez * 0.05))
    return d


# ---------------- big ruby frames (front and back) ----------------
FR_W, FR_H, FR_Y = 1.60, 2.23, -0.755
RU_W, RU_H = 1.04, 1.52


def frame_radius(y):
    return 2.98 + 0.12 * np.clip((y + 1.87) / 2.23, 0, 1)


def ruby_frame(th):
    d = {}
    ex, ey, ez = radial_frame(th)
    def mapping(x, y, h):
        R = frame_radius(FR_Y + y)
        a = th + x / R
        return np.array([(R + h) * np.sin(a), FR_Y + y, (R + h) * np.cos(a)])
    outer = np.array([[FR_W / 2, 0], [0, FR_H / 2], [-FR_W / 2, 0], [0, -FR_H / 2]])
    # stepped double border, pave channel, inner rail
    prof = [(-0.05, -0.15), (0.0, 0.05), (0.01, 0.12), (0.03, 0.135), (0.045, 0.125), (0.05, 0.10), (0.06, 0.10),
            (0.065, 0.085), (0.07, 0.07), (0.16, 0.07), (0.165, 0.10), (0.18, 0.115), (0.195, 0.10), (0.20, 0.07), (0.20, -0.15)]
    add(d, 'gold', polygon_ring(outer, prof, ex, ey, ez, None, mapping=mapping))
    mid = offset_polygon(outer, 0.115)
    for p in points_along_polygon(mid, 12):
        a = th + p[0] / frame_radius(FR_Y + p[1])
        fz = np.array([np.sin(a), 0, np.cos(a)]); fx = np.array([np.cos(a), 0, -np.sin(a)])
        add(d, 'clear', gem(ngon(10, 0.05), [(0.6, 0.02)], 0.032, np.stack([fx, ey, fz], 1), mapping(p[0], p[1], 0.072)))
    # gold plate between the inner rail and the ruby, then the ruby bezel
    plate_out = offset_polygon(outer, 0.20)
    ruby = np.array([[RU_W / 2, 0], [0, RU_H / 2], [-RU_W / 2, 0], [0, -RU_H / 2]])
    plate = []
    for i in range(4):
        for t in np.linspace(0, 1, 6, endpoint=False):
            plate.append(plate_out[i] * (1 - t) + plate_out[(i + 1) % 4] * t)
    plate = np.array(plate)
    rub = []
    for i in range(4):
        for t in np.linspace(0, 1, 6, endpoint=False):
            rub.append(ruby[i] * (1 - t) + ruby[(i + 1) % 4] * t)
    rub = np.array(rub)
    # plate as a ring between the two outlines at height 0.07
    Pp = np.array([[mapping(q[0], q[1], 0.07) for q in plate], [mapping(q[0], q[1], 0.07) for q in rub]])
    Pp = np.concatenate([Pp, Pp[:, :1]], 1)
    add(d, 'gold', grid(Pp, hint=np.repeat(ez[None, None], Pp.shape[0] * Pp.shape[1], 0).reshape(Pp.shape)))
    add(d, 'gold', polygon_ring(ruby + 0.0, [(-0.03, 0.06), (-0.02, 0.10), (0.0, 0.11), (0.012, 0.09), (0.012, 0.0)], ex, ey, ez, None, mapping=mapping))
    # side spurs
    for sgn in (1, -1):
        base = np.array([sgn * FR_W / 2, 0.0])
        tri = [base + [0, 0.10], base + [sgn * 0.28, 0.0], base + [0, -0.10]]
        top = np.array([mapping(q[0], q[1], 0.14) for q in tri]); bot = np.array([mapping(q[0], q[1], -0.02) for q in tri])
        add(d, 'gold', cap(top, ez));
        for i in range(3):
            j = (i + 1) % 3
            quad = np.array([top[i], top[j], bot[j], bot[i]])
            nrm = unit(np.cross(quad[1] - quad[0], quad[3] - quad[0]))
            if np.dot(nrm, quad.mean(0) - top.mean(0)) < 0: nrm = -nrm
            add(d, 'gold', orient(Part(quad, np.repeat(nrm[None], 4, 0), np.array([(0, 1, 2), (0, 2, 3)]))))
    # the ruby: tall kite with a vertical crest and fanned facets
    add(d, 'ruby', crest_fan(ruby, 0.17, origin=mapping(0, 0, 0.0), frame=np.stack([ex, ey, ez], 1)))
    # pave stone at the bottom point, touching the band ruby
    add(d, 'clear', gem(ngon(10, 0.05), [(0.6, 0.02)], 0.03, np.stack([ex, ey, ez], 1), mapping(0, -FR_H / 2 + 0.06, 0.15)))
    return d


def crest_fan(corners, apex, origin, frame, sub=4):
    """Tall kite: narrow triangular facets fanning from the outline to a vertical crest (top, middle, bottom points)."""
    from meshkit import encode_axis
    k = len(corners)
    out = np.array([corners[i] * (1 - t) + corners[(i + 1) % k] * t for i in range(k) for t in np.arange(sub) / sub])
    hy = np.abs(corners[:, 1]).max()
    crest = {'t': np.array([0, hy * 0.52, apex]), 'm': np.array([0, 0, apex * 1.06]), 'b': np.array([0, -hy * 0.52, apex])}
    out3 = np.c_[out, np.zeros(len(out))]
    def which(y):
        return 't' if y > 0.22 * hy else 'b' if y < -0.22 * hy else 'm'
    V, N, T = [], [], []
    def face(poly):
        poly = np.asarray(poly)
        nrm = unit(np.cross(poly[1] - poly[0], poly[2] - poly[0]))
        if nrm[2] < 0: nrm = -nrm
        b = len(V)
        for p in poly: V.append(p); N.append(nrm)
        for j in range(1, len(poly) - 1): T.append((b, b + j, b + j + 1))
    n = len(out)
    tags = [which((out[i, 1] + out[(i + 1) % n, 1]) / 2) for i in range(n)]
    for i in range(n):
        j = (i + 1) % n
        face([out3[i], out3[j], crest[tags[i]]])
        if tags[j] != tags[i]:
            face([out3[j], crest[tags[i]], crest[tags[j]]])
    p = orient(Part(np.array(V), np.array(N), np.array(T)))
    p = p.transformed(np.asarray(frame), np.asarray(origin))
    p.UV = np.repeat(encode_axis(np.asarray(frame)[:, 2])[None], len(p.V), 0)
    return p


def crest_kite(outline, apex, origin, frame):
    """Kite with an intermediate ring and a vertical crest line; every facet flat. Outline local (x, y)."""
    from meshkit import encode_axis
    out = np.c_[outline, np.zeros(len(outline))]
    ring = np.c_[outline * 0.62, np.full(len(outline), apex * 0.62)]
    hy = np.abs(outline[:, 1]).max()
    R0 = np.array([0, hy * 0.48, apex]); R1 = np.array([0, -hy * 0.48, apex])
    V, N, T = [], [], []
    def face(poly):
        poly = np.asarray(poly)
        nrm = unit(np.cross(poly[1] - poly[0], poly[2] - poly[0]))
        if nrm[2] < 0: nrm = -nrm
        b = len(V)
        for p in poly: V.append(p); N.append(nrm)
        for j in range(1, len(poly) - 1): T.append((b, b + j, b + j + 1))
    k = len(outline)
    for i in range(k):
        j = (i + 1) % k
        face([out[i], out[j], ring[j]]); face([out[i], ring[j], ring[i]])
        mid_y = (ring[i, 1] + ring[j, 1]) / 2
        face([ring[i], ring[j], R0 if mid_y > 0 else R1])
    for i in range(k):
        if abs(ring[i, 1]) < 1e-6:
            face([ring[i], R0, R1])
    p = orient(Part(np.array(V), np.array(N), np.array(T)))
    p = p.transformed(np.asarray(frame), np.asarray(origin))
    p.UV = np.repeat(encode_axis(np.asarray(frame)[:, 2])[None], len(p.V), 0)
    return p


# ---------------- circlet ----------------
def circlet2(n=144):
    R_IN = 2.70
    segs = [('gold', [(R_IN, BOTTOM), (2.84, BOTTOM)]),
            ('gold', [(2.84, BOTTOM), (2.875, -2.43), (2.885, -2.39), (2.875, -2.35), (2.85, -2.33), (2.83, -2.325)]),
            ('gold', [(2.83, -2.325), (2.80, -2.312)]),
            ('frieze', [(2.80, -2.312), (2.78, -2.29), (2.775, -2.10), (2.78, -1.895), (2.80, -1.875)]),
            ('gold', [(2.80, -1.875), (2.83, -1.865)]),
            ('gold', [(2.83, -1.865), (2.86, -1.85), (2.885, -1.815), (2.89, -1.78), (2.875, -1.745), (2.845, -1.725), (2.80, -1.718)]),
            ('gold', [(2.80, -1.718), (R_IN, -1.715)]),
            ('gold', [(R_IN, -1.715), (R_IN, BOTTOM)])]
    out = {'gold': [], 'frieze': []}
    for mat, sg in segs:
        prof = np.array(sg)
        prof = np.linspace(prof[0], prof[1], 3) if len(prof) == 2 else resample_polyline(catmull(prof, 8), 3 * len(prof))[0]
        out[mat].append(revolve(prof, n))
    return out


def band_rubies():
    d = {}
    for k in range(12):
        th = k * np.pi / 6
        big = k in (0, 6)
        ex, ey, ez = radial_frame(th)
        w, h = (0.48, 0.60) if big else (0.30, 0.36)
        y = -2.08 if big else -2.095
        origin = K.R_BAND * ez + y * ey
        outer = np.array([[w / 2 + 0.06, 0], [0, h / 2 + 0.07], [-w / 2 - 0.06, 0], [0, -h / 2 - 0.07]])
        prof = [(0, -0.02), (0, 0.04), (0.012, 0.075), (0.03, 0.08), (0.045, 0.065), (0.05, 0.05), (0.07, 0.05), (0.075, 0.065), (0.085, 0.06), (0.09, 0.03), (0.09, -0.02)]
        add(d, 'gold', polygon_ring(outer, prof, ex, ey, ez, origin))
        ro = offset_polygon(outer, 0.09)
        k8 = np.array([q for i in range(4) for q in (ro[i], (ro[i] + ro[(i + 1) % 4]) / 2)])
        add(d, 'ruby', gem(k8, [(0.6, 0.05), (0.3, 0.08)], 0.095, np.stack([ex, ey, ez], 1), origin + ez * 0.01))
    return d


def frieze_scrolls():
    """Raised gold scroll sprays on the dark frieze: a spiral and two small leaves either side of each band ruby."""
    parts = []
    for k in range(12):
        th0 = k * np.pi / 6
        big = k in (0, 6)
        u0 = 0.32 if big else 0.25
        for sgn in (1, -1):
            beta = lambda s, sgn=sgn: sgn * (np.radians(95) - 6.6 * s ** 2.6)
            parts.append(strip(th0, K.R_BAND, (sgn * u0, -2.17, 0.0), 0.62 if not big else 0.55, beta, lambda s: 0.05 + 0 * s,
                               lambda s: 0.055 * (1 - 0.6 * s) + 0.012, lambda s: 0.04 * (1 - 0.4 * s) + 0.01, cup=0.2, prof=ROUND, n=30, rmax=2.88))
            for b0, L, y0 in ((60, 0.30, -2.06), (130, 0.26, -2.20)):
                beta2 = lambda s, sgn=sgn, b0=b0: sgn * (np.radians(b0) + 1.2 * s ** 2)
                parts.append(strip(th0, K.R_BAND, (sgn * (u0 + 0.04), y0, 0.0), L, beta2, lambda s: 0.05 + 0 * s,
                                   leaf_width(0.08, 2, 0.15), lambda s: 0.035 * (1 - 0.5 * s) + 0.01, cup=0.3, n=16, rmax=2.88))
    return merge(parts)


# ---------------- leafwork on an unrolled cylinder ----------------
LEAF = np.array([(-1, 0.05), (-0.55, -0.4), (0, -0.5), (0.55, -0.4), (1, 0.05), (0.6, 0.55), (0.18, 0.6), (0, 0.38), (-0.18, 0.6), (-0.6, 0.55)], float)
ROUND = np.array([(-1, 0), (-0.7, -0.6), (0, -0.85), (0.7, -0.6), (1, 0), (0.7, 0.6), (0, 0.85), (-0.7, 0.6)], float)


def strip(th0, Rb, start, length, beta, gamma, width, thick, cup=0.5, prof=LEAF, n=26, rmax=3.31):
    s = np.linspace(0, 1, n)
    b = beta(s); g = gamma(s)
    t = np.stack([np.cos(g) * np.sin(b), np.cos(g) * np.cos(b), np.sin(g)], -1)
    pts = np.asarray(start, float) + np.vstack([[0, 0, 0], np.cumsum((t[:-1] + t[1:]) / 2 * length / (n - 1), 0)])
    hmax = rmax - Rb - 0.06
    if pts[:, 2].max() > hmax:
        h0 = pts[0, 2]
        pts[:, 2] = h0 + (pts[:, 2] - h0) * (hmax - h0) / (pts[:, 2].max() - h0)
    Au = np.stack([np.cos(b), -np.sin(b), 0 * b], -1)
    Ou = unit(np.cross(Au, t))
    a = th0 + pts[:, 0] / Rb
    r = Rb + pts[:, 2]
    C = np.stack([r * np.sin(a), pts[:, 1], r * np.cos(a)], -1)
    eu = np.stack([np.cos(a), 0 * a, -np.sin(a)], -1); eh = np.stack([np.sin(a), 0 * a, np.cos(a)], -1); ey = np.array([0, 1.0, 0])
    m = lambda v: v[:, 0:1] * eu + v[:, 1:2] * ey + v[:, 2:3] * eh
    A = unit(m(Au)); O = unit(m(Ou))
    w = np.maximum(width(s), 0.008); th = np.maximum(thick(s), 0.008)
    pa = prof[:, 0][:, None]; po = prof[:, 1][:, None]
    P = C[None] + (pa * w[None])[..., None] * A[None] + (po * th[None] + cup * pa ** 2 * w[None] * 0.5)[..., None] * O[None]
    P = np.concatenate([P, P[:1]], 0)
    pr = np.vstack([prof, prof[:1]])
    tt = np.gradient(pr, axis=0); n2 = np.stack([tt[:, 1], -tt[:, 0]], -1)
    H = n2[:, 0][:, None, None] * A[None] + n2[:, 1][:, None, None] * O[None]
    return grid(P, hint=H)


def leaf_width(W0, lobes=4, amp=0.3):
    return lambda s: W0 * np.clip(((s + 0.04) / 0.38) ** 0.6, 0, 1) * (1 - s) ** 0.75 * (1 + amp * np.abs(np.sin(lobes * np.pi * s)) * (s > 0.12))


def lobe(th, Rb, start, phi_deg, L, W0, side_curl=1.0, lean=0.7, over=0.5, thick=0.10, lobes=3, amp=0.12, cup=0.45, spiral=4.2, rmax=3.31):
    ph = np.radians(phi_deg); sg = np.sign(phi_deg) if phi_deg != 0 else 0
    beta = lambda s: ph + sg * (side_curl * s ** 2.2 + spiral * s ** 6)
    gamma = lambda s: lean * (1 - s) ** 1.6 + over * s ** 4
    width = lambda s: leaf_width(W0, lobes, amp)(s) * (1 - 0.5 * s ** 3) + 0.02 * s
    return strip(th, Rb, start, L, beta, gamma, width, lambda s: thick * (1 - 0.55 * s) + 0.016, cup=cup, n=34, rmax=rmax)


def acanthus_cluster(th):
    """Two layers of curled, lobed acanthus leaves fanning from the arch foot, in front of the arch base."""
    parts = []
    Rb = 2.84
    back = [(-72, 1.00, 0.30), (-38, 1.35, 0.34), (-6, 1.62, 0.36), (38, 1.35, 0.34), (72, 1.00, 0.30)]
    for phi, L, W0 in back:
        parts.append(lobe(th, Rb, (0.06 * np.sign(phi), -1.70, 0.03), phi, L, W0, spiral=0.0 if phi == -6 else 4.2, over=1.1 if phi == -6 else 0.5, rmax=3.24))
    front = [(-24, 0.80, 0.26), (24, 0.80, 0.26)]
    for phi, L, W0 in front:
        parts.append(lobe(th, Rb, (0.04 * np.sign(phi), -1.66, 0.15), phi, L, W0, lean=0.5, spiral=3.6, rmax=3.26))
    return merge(parts)


def volute(th0, Rb, start, heading_deg, turn, L, W0, sgn, y_scale=1.0, n=34):
    beta = lambda s: np.radians(heading_deg) * sgn + sgn * turn * s ** 2.6
    gamma = lambda s: 0.05 + 0 * s
    width = lambda s: W0 * (1 - 0.65 * s) * np.clip((s + 0.05) / 0.15, 0, 1)
    return strip(th0, Rb, start, L, beta, gamma, width, lambda s: 0.06 * (1 - 0.45 * s), cup=0.25, prof=ROUND, n=n)


def leafwork():
    d = {}
    for th in ARCH_TH:
        if any(abs(np.angle(np.exp(1j * (th - s)))) < 1e-6 for s in STRAP_TH):
            continue
        add(d, 'gold_leaf', acanthus_cluster(th))
        add(d, 'gold', ball(np.array([3.10 * np.sin(th), -1.60, 3.10 * np.cos(th)]) + 0.0, 0.09))
        # tendrils toward both neighbours, ending in spirals with a ball
        for sgn in (1, -1):
            nb = th + sgn * np.pi / 4
            toward_frame = any(abs(np.angle(np.exp(1j * (nb - s)))) < 1e-6 for s in STRAP_TH)
            L = 0.95 if toward_frame else 0.62
            start = (sgn * 0.42, -1.62, 0.08)
            add(d, 'gold_leaf', volute(th, 2.95, start, 62, 7.0, L, 0.15, sgn))
            # where the spiral ends, a small polished ball
            s = np.linspace(0, 1, 34); b = np.radians(62) * sgn + sgn * 7.0 * s ** 2.6
            t = np.stack([np.sin(b), np.cos(b)], -1)
            pts = np.vstack([[0, 0], np.cumsum((t[:-1] + t[1:]) / 2 * L / 33, 0)])
            cu = start[0] + pts[-6:, 0].mean(); cy = start[1] + pts[-6:, 1].mean()
            a = th + cu / 2.95
            add(d, 'gold', ball(np.array([3.07 * np.sin(a), cy, 3.07 * np.cos(a)]), 0.05))
    for th in STRAP_TH:
        for sgn in (1, -1):
            R = frame_radius(-0.75)
            # gem side spray from behind the frame corner: three lobed leaves curling outward
            for phi, L, W0, y0 in ((sgn * 50, 0.95, 0.28, -0.70), (sgn * 84, 0.85, 0.26, -0.82), (sgn * 120, 0.62, 0.20, -0.95)):
                add(d, 'gold_leaf', lobe(th, R, (sgn * 0.84, y0, 0.05), phi, L, W0, side_curl=0.9, lean=0.25, over=0.6, spiral=4.0))
            # C scroll under it, ending in a spiral over the band's top rail
            add(d, 'gold_leaf', volute(th, 3.0, (sgn * 0.60, -1.18, 0.10), 115, 7.0, 1.05, 0.16, sgn))
            # leaves over the frame's lower sides
            for phi, L, W0, y0 in ((sgn * 30, 0.65, 0.22, -1.64), (sgn * 62, 0.55, 0.20, -1.66)):
                add(d, 'gold_leaf', lobe(th, 3.0, (sgn * 0.40, y0, 0.14), phi, L, W0, side_curl=0.8, lean=0.35, over=0.6, spiral=3.5))
    return d


# ---------------- bell, neck and fleur de lis ----------------
def bell_and_neck(n=72):
    segs = [
        [(0.30, 0.93), (0.49, 0.94), (0.535, 0.965), (0.54, 1.0), (0.52, 1.03), (0.48, 1.045)],
        [(0.48, 1.045), (0.38, 1.09), (0.29, 1.15), (0.22, 1.23), (0.18, 1.33), (0.16, 1.42)],
        [(0.16, 1.42), (0.215, 1.425), (0.225, 1.445), (0.215, 1.465), (0.165, 1.47)],
        [(0.165, 1.47), (0.21, 1.48), (0.232, 1.50), (0.21, 1.525), (0.155, 1.53)],
        [(0.155, 1.53), (0.13, 1.57), (0.125, 1.70), (0.13, 1.78)],
        [(0.13, 1.78), (0.20, 1.785), (0.215, 1.81), (0.215, 1.88), (0.20, 1.90), (0.12, 1.905)],
    ]
    parts = []
    for s_ in segs:
        prof = resample_polyline(catmull(np.array(s_), 8), 4 * len(s_))[0]
        parts.append(revolve(prof, n))
    return merge(parts)


def fleur_center(n=64):
    y0, y1 = 1.88, TIP
    ys = np.linspace(y0, y1, 40)
    t = (ys - y0) / (y1 - y0)
    r = np.where(t < 0.30, 0.10 + 0.13 * np.sin(np.pi / 2 * t / 0.30),
                 0.23 * np.cos(np.pi / 2 * np.clip((t - 0.30) / 0.70, 0, 1)) ** 1.1)
    r[-1] = 0.0
    prof = np.c_[r, ys]
    def disp(th, k):
        rr = prof[k[:, 0], 0][:, None]
        return rr * 0.32 * np.cos(2 * th) ** 4 - rr * 0.20, np.zeros_like(th * k)
    return revolve(prof, n, disp=disp)


def fleur_petals():
    d = {}
    petal = [(0.13, 1.90), (0.30, 2.05), (0.50, 2.20), (0.68, 2.27), (0.82, 2.22), (0.87, 2.10), (0.82, 1.98), (0.74, 1.93), (0.70, 1.97)]
    curl = [(0.12, 1.77), (0.24, 1.70), (0.36, 1.62), (0.43, 1.56), (0.46, 1.61), (0.42, 1.66), (0.38, 1.63)]
    lens = np.array([(-1, 0), (-0.6, -0.55), (0, -0.7), (0.6, -0.55), (1, 0), (0.6, 0.55), (0, 0.7), (-0.6, 0.55)], float)
    for k in range(4):
        th = np.pi / 4 + k * np.pi / 2
        for ctrl, wprof, t0 in ((petal, (0.15, 0.21, 0.18, 0.05), 0.075), (curl, (0.075, 0.075, 0.055, 0.02), 0.06)):
            path = resample_polyline(catmull(np.array(ctrl), 10), 34)[0]
            C = np.stack([path[:, 0] * np.sin(th), path[:, 1], path[:, 0] * np.cos(th)], -1)
            A = np.repeat(np.array([[np.cos(th), 0, -np.sin(th)]]), len(C), 0)
            T = unit(np.gradient(C, axis=0)); O = unit(np.cross(A, T))
            s_ = np.linspace(0, 1, len(C))
            wa = np.interp(s_, [0, 0.35, 0.7, 1.0], wprof)
            add(d, 'gold', sweep(C, A, O, lens * [t0, 1], scale_a=0.6 + 0.4 * wa / max(wprof), scale_o=wa))
        # gold bead at each side of the collar
        add(d, 'gold', ball(np.array([0.215 * np.sin(th), 1.845, 0.215 * np.cos(th)]), 0.045))
    for k in range(4):
        th = k * np.pi / 2
        ex, ey, ez = radial_frame(th)
        c = 0.215 * ez + 1.845 * ey
        add(d, 'gold', polygon_ring(ngon(14, 0.11), [(0, -0.01), (0, 0.03), (0.01, 0.04), (0.025, 0.03), (0.025, 0.0)], ex, ey, ez, c))
        add(d, 'ruby', gem(ngon(10, 0.09), [(0.62, 0.025)], 0.04, np.stack([ex, ey, ez], 1), c + ez * 0.01))
        # cushion stone on the bell lip, straddling the strap top
        nrm = unit(ez * 0.82 + ey * 0.57)
        from meshkit import frame_on_surface
        fr = frame_on_surface(nrm)
        o = 0.47 * ez + 1.04 * ey
        outer = np.array([[0.19, 0], [0, 0.23], [-0.19, 0], [0, -0.23]])
        add(d, 'gold', polygon_ring(outer, [(0, -0.03), (0, 0.05), (0.012, 0.07), (0.03, 0.07), (0.045, 0.05), (0.045, 0.0)], fr[:, 0], fr[:, 1], fr[:, 2], o))
        ro = offset_polygon(outer, 0.045)
        k8 = np.array([q for i in range(4) for q in (ro[i], (ro[i] + ro[(i + 1) % 4]) / 2)])
        add(d, 'ruby', gem(k8, [(0.66, 0.03), (0.34, 0.045)], 0.055, fr, o + fr[:, 2] * 0.01))
    return d


def build(out, tex=None):
    parts = {}
    def take(dd):
        for m, ps in dd.items(): parts.setdefault(m, []).extend(ps)
    take(circlet2())
    take({'gold': [bead_rows(r=2.80, ys=(-2.31, -1.88), rad=0.02), frieze_scrolls()]})
    take(band_rubies())
    take({'velvet': [velvet()]})
    for th in ARCH_TH:
        if any(abs(np.angle(np.exp(1j * (th - s)))) < 1e-6 for s in STRAP_TH):
            take(strap(th)); take(ruby_frame(th))
            continue
        # thick rail toward the nearest side (90 or 270 degrees); medium on the side arches
        deg = round(np.degrees(th)) % 360
        side = {45: 1, 135: -1, 225: 1, 315: -1}.get(deg, 0)
        use_path('side' if side == 0 else 'diag')
        a, fr = arch(th, side)
        take({'gold': [a]}); take(arch_stones(th, side, fr))
    take(leafwork())
    take({'gold': [bell_and_neck(), fleur_center()]})
    take(fleur_petals())
    from meshkit import encode_axis
    data = {}
    for mat, ps in parts.items():
        m = merge(ps)
        m.V[:, 1] = BOTTOM + (m.V[:, 1] - BOTTOM) * SY
        m.N = unit(m.N * np.array([1, 1 / SY, 1]))
        if mat in ('ruby', 'clear'):
            az = m.UV[:, 0] * 2 * np.pi; el = (m.UV[:, 1] - 0.5) * np.pi
            ax = np.stack([np.cos(el) * np.sin(az), np.sin(el), np.cos(el) * np.cos(az)], -1)
            ax = unit(ax * np.array([1, 1 / SY, 1]))
            m.UV = np.stack([(np.arctan2(ax[:, 0], ax[:, 2]) / (2 * np.pi)) % 1.0, np.arcsin(np.clip(ax[:, 1], -1, 1)) / np.pi + 0.5], -1)
        m = orient(m)
        data[mat + '_v'] = m.V; data[mat + '_n'] = m.N; data[mat + '_t'] = m.T
        if m.UV is not None:
            data[mat + '_uv'] = m.UV
    np.savez(out, **data)
    allv = np.vstack([data[k] for k in data if k.endswith('_v')])
    rr = np.hypot(allv[:, 0], allv[:, 2])
    tris = {k[:-2]: len(data[k]) for k in data if k.endswith('_t')}
    print('triangles', sum(tris.values()), tris)
    print('bounds', allv.min(0).round(3), allv.max(0).round(3), 'max radius', rr.max().round(3))
    if tex:
        velvet_texture(tex)


if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
