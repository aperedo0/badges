"""Ruby Crown geometry (model units, Y up, front +Z, theta from +Z toward +X).

Usage: crown.py OUT.npz
Writes one merged mesh per material: gold, gold_recess, velvet, ruby, clear.
"""
import sys
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/ruby_crown_claude_20261108/tools')
from meshkit import Part, merge, unit, grid, revolve, sweep, cap, catmull, resample_polyline, gem, frame_on_surface, ngon, rhombus, orient

BOTTOM = -2.455
CSCALE = 0.955          # circlet radius scale (outer rim 2.87)
R_BAND = 2.905 * CSCALE  # recessed band face radius
N_ARCH = 8
ARCH_TH = 0.10

# ---------------- arch meridian curve ----------------
RSCALE = 0.955
ARCH_CTRL = [(2.93 * RSCALE, -1.70), (3.0 * RSCALE, -1.20), (3.06 * RSCALE, -0.50), (3.0 * RSCALE, 0.25), (2.74 * RSCALE, 0.80),
             (2.15, 1.14), (1.30, 1.33), (0.50, 1.36)]
_c = catmull(ARCH_CTRL, 24)
ARCH2D, _ = resample_polyline(_c, 64)                      # (r, y) inner face of each arch
_t = unit(np.gradient(ARCH2D, axis=0))
ARCH_N2 = np.stack([_t[:, 1], -_t[:, 0]], -1)                # outward normal in (r, y)
ARCH_S = np.linspace(0, 1, len(ARCH2D))


def meridian_point(rr, yy, th):
    return np.stack([rr * np.sin(th), yy, rr * np.cos(th)], -1)


# ---------------- circlet ----------------
def circlet(n=128):
    segs = [
        [(2.78, BOTTOM), (2.96, BOTTOM)],                                   # bottom face
        [(2.96, BOTTOM), (2.995, -2.43), (3.005, -2.39), (2.995, -2.35), (2.965, -2.325), (2.93, -2.315)],  # bottom rim
        [(2.93, -2.315), (2.905, -2.30)],                                   # step into the recess
        [(2.905, -2.30), (2.90, -2.09), (2.905, -1.875)],                   # recessed band face
        [(2.905, -1.875), (2.93, -1.865)],                                  # step out
        [(2.93, -1.865), (2.965, -1.855), (2.995, -1.83), (3.005, -1.79), (2.995, -1.75), (2.965, -1.72), (2.92, -1.707)],  # top rim
        [(2.92, -1.707), (2.78, -1.705)],                                   # top face
        [(2.78, -1.705), (2.78, BOTTOM)],                                   # inner wall
    ]
    segs = [[(r * CSCALE, y) for r, y in sg] for sg in segs]
    gold, recess = [], []
    for i, s in enumerate(segs):
        prof = np.array(s)
        if len(prof) == 2:
            prof = np.linspace(prof[0], prof[1], 3)
        else:
            prof = resample_polyline(catmull(prof, 8), max(5, 2 * len(prof)))[0]
        p = revolve(prof, n)
        (recess if i == 3 else gold).append(p)
    return merge(gold), merge(recess)


# ---------------- velvet ----------------
def pinch(th):
    """1 under an arch, 0 midway between arches."""
    return np.cos(N_ARCH / 2 * th) ** 2


_vb = np.vstack([[(2.84 * CSCALE, -1.98), (2.87 * CSCALE, -1.82)], ARCH2D, [(0.30, 1.37), (0.0, 1.375)]])
VBASE, _ = resample_polyline(_vb, 56)
_vt = unit(np.gradient(VBASE, axis=0)); VN2 = np.stack([_vt[:, 1], -_vt[:, 0]], -1)
_yv = VBASE[:, 1]
VPUFF = 0.19 * np.clip((_yv + 1.85) / 0.45, 0, 1) ** 1.5
VPUFF *= np.where(VBASE[:, 0] < 2.4, 0.55 + 0.45 * np.clip(VBASE[:, 0] / 2.4, 0, 1), 1.0)
VPUFF *= np.clip(VBASE[:, 0] / 0.9, 0, 1)
VFOLD = 0.03 * np.clip((_yv + 1.7) / 0.6, 0, 1) * np.clip(1.15 - _yv, 0, 1) * np.clip(VBASE[:, 0] / 2.0, 0, 1)


def major_window(th, k):
    """1 behind a big ruby setting (front, back, sides, lower half), 0 elsewhere."""
    dth = np.angle(np.exp(1j * th * 4)) / 4          # angle to the nearest major arch
    yv = VBASE[k, 1]
    yw = np.clip((yv + 1.9) / 0.2, 0, 1) * np.clip((0.62 - yv) / 0.22, 0, 1)
    return np.exp(-(dth / 0.40) ** 4) * yw


def velvet_disp(th, k):
    p = (1 - pinch(th)) ** 0.8
    d = VPUFF[k] * p + VFOLD[k] * np.sin(3 * N_ARCH * th + 0.9 * np.sin(5 * th + 1.3))
    return d * (1 - major_window(th, k)) - 0.03 * major_window(th, k)


def velvet(n=120):
    def disp(th, k):
        k = k[:, 0]
        d = velvet_disp(th, k[:, None])
        return d * VN2[k, 0][:, None], d * VN2[k, 1][:, None]
    return revolve(VBASE, n, disp=disp)


def velvet_surface(th, y):
    """Point and outward normal of the velvet at angle th and height y (lower and side region)."""
    k = np.interp(y, VBASE[:, 1], np.arange(len(VBASE)))
    def pt(th_, k_):
        k0 = int(np.clip(np.floor(k_), 0, len(VBASE) - 2)); f = k_ - k0
        b = VBASE[k0] * (1 - f) + VBASE[k0 + 1] * f
        n2 = VN2[k0] * (1 - f) + VN2[k0 + 1] * f
        d = velvet_disp(th_, k0) * (1 - f) + velvet_disp(th_, k0 + 1) * f
        rr, yy = b + d * n2
        return np.array([rr * np.sin(th_), yy, rr * np.cos(th_)])
    p = pt(th, k)
    dt = pt(th + 1e-3, k) - pt(th - 1e-3, k)
    dk = pt(th, min(k + 0.05, len(VBASE) - 1.01)) - pt(th, max(k - 0.05, 0))
    nrm = unit(np.cross(dt, dk))
    if np.dot(nrm, [np.sin(th), 0, np.cos(th)]) < 0: nrm = -nrm
    return p, nrm


# ---------------- arches ----------------
def arch_profile(w):
    """Channel band, counterclockwise in (a, o); o measured outward from the inner face."""
    return np.array([(-w, 0.0), (w, 0.0), (w, 0.07), (w - 0.015, 0.10), (w - 0.05, 0.10), (w - 0.065, 0.07),
                     (-w + 0.065, 0.07), (-w + 0.05, 0.10), (-w + 0.015, 0.10), (-w, 0.07)])


def arch(th, w0=0.30, w1=0.10, y_start=None):
    C = meridian_point(ARCH2D[:, 0], ARCH2D[:, 1], th)
    O = np.stack([ARCH_N2[:, 0] * np.sin(th), ARCH_N2[:, 1], ARCH_N2[:, 0] * np.cos(th)], -1)
    A = np.repeat(np.array([[np.cos(th), 0, -np.sin(th)]]), len(C), 0)
    w = w0 + (w1 - w0) * np.clip((ARCH_S - 0.35) / 0.65, 0, 1) ** 1.3
    if y_start is not None:
        keep = ARCH2D[:, 1] >= y_start
        C, O, A, w = C[keep], O[keep], A[keep], w[keep]
    # build with a unit profile scaled across
    prof = arch_profile(w0)
    p = sweep(C, A, O, prof, scale_a=w / w0)
    ends = []
    for i, sgn in ((0, -1), (-1, 1)):
        loop = C[i] + np.outer(prof[:, 0] * w[i] / w0, A[i]) + np.outer(prof[:, 1], O[i])
        tan = unit(C[i] - C[i + (1 if i == 0 else -1)])
        ends.append(cap(loop, tan))
    return merge([p] + ends), (C, A, O, w)


# ---------------- hub and finial ----------------
def hub(n=64):
    segs = [
        [(0.40, 1.30), (0.58, 1.30)],
        [(0.58, 1.30), (0.62, 1.335), (0.615, 1.375), (0.585, 1.40), (0.53, 1.41)],
        [(0.53, 1.41), (0.44, 1.46), (0.34, 1.51), (0.26, 1.56), (0.205, 1.61), (0.18, 1.655)],
        [(0.18, 1.655), (0.215, 1.675), (0.225, 1.71), (0.205, 1.745), (0.165, 1.76)],
        [(0.165, 1.76), (0.125, 1.80), (0.115, 1.90), (0.12, 1.96)],
    ]
    parts = []
    for s in segs:
        prof = np.array(s)
        prof = np.linspace(prof[0], prof[1], 3) if len(prof) == 2 else resample_polyline(catmull(prof, 8), 4 * len(prof))[0]
        parts.append(revolve(prof, n))
    return merge(parts)


def fleur_spear(n=48):
    """Central petal: a broad almond with ridges front, back and sides (reads as a petal from every side)."""
    y0, y1 = 2.12, 3.0
    ys = np.linspace(y0, y1, 34)
    t = (ys - y0) / (y1 - y0)
    r = np.where(t < 0.34, 0.09 + 0.21 * np.sin(np.pi / 2 * t / 0.34),
                 0.30 * np.cos(np.pi / 2 * np.clip((t - 0.34) / 0.66, 0, 1)) ** 1.15)
    r[-1] = 0.0
    prof = np.c_[r, ys]
    def disp(th, k):
        rr = prof[k[:, 0], 0][:, None]
        return rr * 0.30 * np.cos(2 * th) ** 4 - rr * 0.18, np.zeros_like(th * k)
    return revolve(prof, n, theta0=0.0, disp=disp)


def build(out):
    import ornaments as O
    parts = {'gold': [], 'gold_recess': [], 'velvet': [], 'ruby': [], 'clear': []}
    def take(d):
        for m, ps in d.items(): parts[m] += ps
    g, rcs = circlet()
    parts['gold'].append(g); parts['gold_recess'].append(rcs)
    parts['velvet'].append(velvet())
    for k in range(N_ARCH):
        th = k * 2 * np.pi / N_ARCH
        major = k % 2 == 0
        a, _ = arch(th, y_start=0.30 if major else None)
        parts['gold'].append(a)
        take(O.arch_stones(th, major))
        take(O.band_setting(th))
        take(O.acanthus(th, major))
        if major:
            take(O.rhombus_setting(th))
    parts['gold'].append(O.bead_rows())
    parts['gold'].append(O.band_scrolls())
    parts['gold'].append(hub())
    parts['gold'].append(fleur_spear())
    take(O.hub_stones())
    take(O.fleur())
    data = {}
    for mat, ps in parts.items():
        if not ps:
            continue
        m = orient(merge(ps))
        data[mat + '_v'] = m.V; data[mat + '_n'] = m.N; data[mat + '_t'] = m.T
        if m.UV is not None:
            data[mat + '_uv'] = m.UV
    np.savez(out, **data)
    allv = np.vstack([data[k] for k in data if k.endswith('_v')])
    tris = {k[:-2]: len(data[k]) for k in data if k.endswith('_t')}
    print('triangles', sum(tris.values()), tris, 'bounds', allv.min(0).round(3), allv.max(0).round(3))


if __name__ == '__main__':
    build(sys.argv[1])
