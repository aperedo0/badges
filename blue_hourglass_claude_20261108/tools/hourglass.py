"""Blue Hourglass, fully 3D (model units, Y up, front +Z). Every round part is a revolved profile traced from
the mockup: x pixel offset from the center line 623 becomes the radius, y pixel becomes height.

Usage: hourglass.py OUT.npz
"""
import sys
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/blue_hourglass_claude_20261108/tools')
from meshkit import Part, merge, unit, revolve, catmull, resample_polyline, sweep, orient

TOP_PX, BOT_PX = 44, 1167
S = 5.45 / (BOT_PX - TOP_PX)


def Y(y):
    return 2.995 - (y - TOP_PX) * S


def R(px):
    return px * S


parts = {}


def add(mat, p):
    parts.setdefault(mat, []).append(p)


def prof(points, n=None, smooth=True):
    """points: (radius px, y px) top to bottom around the outside; returns (r, y) model, resampled."""
    p = np.array([(R(r), Y(y)) for r, y in points])
    if smooth and len(p) > 2:
        p = catmull(p, 8)
    return resample_polyline(p, n or max(8, len(points) * 6))[0]


SEG = 80

# ---------------- marble discs with rounded edges ----------------
def disc(y_top, y_bot, r, fillet, phase=0.0):
    """Marble disc as three parts: flat top and bottom caps (planar texture) and the rounded band (wrapped texture)."""
    from meshkit import grid
    ang = np.linspace(0, np.pi / 2, 7)
    band = [(r - fillet + fillet * np.sin(a), y_top + fillet - fillet * np.cos(a)) for a in ang]
    band += [(r - fillet + fillet * np.cos(a), y_bot - fillet + fillet * np.sin(a)) for a in ang]
    band = resample_polyline(np.array([(R(a), Y(b)) for a, b in band]), 30)[0]
    th = np.linspace(np.pi, 3 * np.pi, SEG + 1)   # texture seam at the back
    P = np.stack([band[:, 0:1] * np.sin(th), np.repeat(band[:, 1:2], SEG + 1, 1), band[:, 0:1] * np.cos(th)], -1)
    t = np.gradient(band, axis=0); n2 = np.stack([-t[:, 1], t[:, 0]], -1)   # outward for a top to bottom profile
    Hn = np.stack([n2[:, 0:1] * np.sin(th), np.repeat(n2[:, 1:2], SEG + 1, 1), n2[:, 0:1] * np.cos(th)], -1)
    arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(band, axis=0), axis=1))]
    uv = np.stack(np.meshgrid(th / (2 * np.pi) * 3 + phase, arc / 1.2 + phase)[::-1], -1)[..., ::-1]
    uv = np.stack([np.repeat((th / (2 * np.pi) * 3 + phase)[None], len(band), 0), np.repeat((arc / 1.2 + phase)[:, None], SEG + 1, 1)], -1)
    add('marble', grid(P, hint=Hn, uv=uv))
    for yy, sgn in ((band[0, 1], 1), (band[-1, 1], -1)):
        rr = np.linspace(0, band[0, 0], 8)[:, None]
        Pc = np.stack([rr * np.sin(th), np.full((8, SEG + 1), yy), rr * np.cos(th)], -1)
        Hc = np.zeros_like(Pc); Hc[..., 1] = sgn
        uvc = np.stack([Pc[..., 0] / 3.2 + 0.5 + phase, Pc[..., 2] / 3.2 + 0.5], -1)
        add('marble', grid(Pc, hint=Hc, uv=uvc))
    return None


# top disc spans y 78 (its top) to 165; bottom disc 1040 to 1140
disc(58, 168, 325, 22)
disc(1048, 1152, 327, 22, phase=0.37)
# ---------------- gold plates and collars ----------------
def ring(y_top, y_bot, r_out, bevel=4):
    """Flat banded ring: top face, top bevel, vertical front, bottom bevel, bottom face, each shaded flat."""
    from meshkit import merge as _m
    faces = [[(0, y_top), (r_out - bevel, y_top)], [(r_out - bevel, y_top), (r_out, y_top + bevel)],
             [(r_out, y_top + bevel), (r_out, y_bot - bevel)], [(r_out, y_bot - bevel), (r_out - bevel, y_bot)],
             [(r_out - bevel, y_bot), (0, y_bot)]]
    out = []
    for f in faces:
        pts = np.array([(R(a), Y(b)) for a, b in f])
        pts = np.linspace(pts[0], pts[1], 3)
        out.append(revolve(pts, SEG, hint_out=False))
    return _m(out)


add('gold', ring(166, 212, 302, 6))       # top band about 4% of H, sunk 4 px into the disc so faces never coincide
add('gold', ring(210, 220, 288, 3))       # underside step
add('gold', ring(218, 236, 206, 3))       # collar holding the glass lip, about 59% of W
add('gold', ring(1000, 1010, 204, 2))     # shallow round seat hugging the glass base
add('gold', ring(1008, 1052, 302, 6))     # one bottom plate about 4% of H, sunk 4 px into the disc

# ---------------- posts (two, at the sides) ----------------
def post(theta):
    ys = np.linspace(Y(212), Y(1008), 24)
    c = np.array([R(242) * np.sin(theta), 0, R(242) * np.cos(theta)])
    a = np.linspace(0, 2 * np.pi, 20, endpoint=False)
    r = R(27)
    P = np.array([[c + [r * np.cos(t), y, r * np.sin(t)] for t in a] for y in ys])
    H = np.array([[[np.cos(t), 0, np.sin(t)] for t in a] for y in ys])
    from meshkit import grid
    return grid(P, closed_v=True, hint=H)


for th in (np.pi / 2, -np.pi / 2):
    add('gold', post(th))
    # small base and capital collars on each post
    for yc in (1000,):
        c = np.array([R(242) * np.sin(th), Y(yc), R(242) * np.cos(th)])
        a = np.linspace(0, 2 * np.pi, 20, endpoint=False)
        rr = R(36)
        P = np.array([[c + [rr * np.cos(t), dy, rr * np.sin(t)] for t in a] for dy in (R(8), -R(8))])
        H = np.array([[[np.cos(t), 0, np.sin(t)] for t in a] for _ in range(2)])
        from meshkit import grid
        add('gold', grid(P, closed_v=True, hint=H))

# ---------------- glass: hollow shell ----------------
OUTER = [(194, 232), (195, 252), (208, 274), (213, 305), (212, 345), (200, 395), (172, 450), (128, 500), (75, 545),
         (36, 578), (29, 598), (29, 612), (36, 632), (75, 665), (128, 710), (172, 760), (200, 815), (212, 865),
         (213, 910), (207, 950), (196, 980), (194, 1002)]
outer = prof(OUTER, 90)
add('glass', revolve(outer, SEG, hint_out=False))
inner = outer.copy()
wall = R(7) + R(10) * np.exp(-((inner[:, 1] - Y(605)) / R(40)) ** 2)   # thicker glass toward the neck
inner[:, 0] = np.maximum(inner[:, 0] - wall, R(11))
gi = revolve(inner[::-1], SEG, hint_out=False)   # bottom to top profile flipped: normals point inward
add('glass', gi)

# ---------------- sand ----------------
def inner_r(y_px):
    yy = Y(y_px)
    return np.interp(-yy, -inner[:, 1], inner[:, 0])


def revolve_uv(profile, seg, u_repeat, v_scale):
    """Revolve a top to bottom profile with a duplicated seam column and (around, along) texture coordinates."""
    from meshkit import grid
    pr = np.asarray(profile, float)
    th = np.linspace(np.pi, 3 * np.pi, seg + 1)          # seam at the back
    P = np.stack([pr[:, 0:1] * np.sin(th), np.repeat(pr[:, 1:2], seg + 1, 1), pr[:, 0:1] * np.cos(th)], -1)
    t = np.gradient(pr, axis=0); n2 = np.stack([-t[:, 1], t[:, 0]], -1)
    H = np.stack([n2[:, 0:1] * np.sin(th), np.repeat(n2[:, 1:2], seg + 1, 1), n2[:, 0:1] * np.cos(th)], -1)
    arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pr, axis=0), axis=1))]
    uv = np.stack([np.repeat((th - np.pi)[None] / (2 * np.pi) * u_repeat, len(pr), 0),
                   np.repeat((arc * v_scale)[:, None], seg + 1, 1)], -1)
    return grid(P, hint=H, uv=uv)


# top sand: a gently dished surface (seen from slightly above), then down the glass into the neck
surf = [(0.0, Y(424))] + [(inner_r(410) * f, Y(410 + 14 * (1 - f * f) + 1.5 * np.sin(11 * f))) for f in np.linspace(0.1, 0.985, 14)]
below = [(inner_r(y) - R(1), Y(y)) for y in np.linspace(412, 600, 26)] + [(0.0, Y(602))]
add('sand', revolve_uv(resample_polyline(np.array(surf + below), 70)[0], SEG, 2.0, 0.35))
# falling stream: a fine core thread plus loose grains around it, a small spray near the pile
rng_s = np.random.default_rng(5)
core = [(R(1.6), Y(600)), (R(1.6), Y(852)), (0.0, Y(853))]
add('stream', revolve_uv(np.array([(0.0, Y(599))] + core), 12, 1.0, 0.35))
oct_v = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], float)
oct_t = np.array([[0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4], [2, 0, 5], [1, 2, 5], [3, 1, 5], [0, 3, 5]])
for k in range(110):
    yy = rng_s.uniform(600, 852); depth = (yy - 600) / 252
    spread = R(3.0 + 14.0 * max(0.0, depth - 0.65) / 0.35)
    ang = rng_s.uniform(0, 2 * np.pi); rr = abs(rng_s.normal(0, 1)) * spread
    c = np.array([rr * np.cos(ang), Y(yy), rr * np.sin(ang)])
    g = R(2.2) * rng_s.uniform(0.8, 1.3)
    add('stream', orient(Part(c + oct_v * g, oct_v.copy(), oct_t)))
# bottom pile: cone with a softly rounded peak and slightly concave slopes, meeting the glass
pile = [(0.0, Y(856))] + [(inner_r(966) * f, Y(856 + 110 * (f if f > 0.12 else 0.12 * (f / 0.12) ** 2) - 6 * np.sin(np.pi * f))) for f in np.linspace(0.03, 1.0, 18)]
pile += [(inner_r(y) - R(1), Y(y)) for y in (975, 988, 1000)] + [(0.0, Y(1001))]
add('sand', revolve_uv(resample_polyline(np.array(pile), 56)[0], SEG, 2.0, 0.35))

if __name__ == '__main__':
    data = {}
    for mat, ps in parts.items():
        m = orient(merge(ps))
        data[mat + '_v'] = m.V; data[mat + '_n'] = m.N; data[mat + '_t'] = m.T
        if m.UV is not None:
            data[mat + '_uv'] = m.UV
    for mat in [k[:-2] for k in data if k.endswith('_v')]:
        data[mat + '_v'] = data[mat + '_v'] * [1.07, 1, 1.07]
        n = data[mat + '_n'] / [1.07, 1, 1.07]; data[mat + '_n'] = n / np.linalg.norm(n, axis=1, keepdims=True)
    vs = [k for k in data if k.endswith('_v')]
    lo = min(data[k][:, 1].min() for k in vs); hi = max(data[k][:, 1].max() for k in vs)
    sc = (2.995 + 2.455) / (hi - lo)
    for k in vs:
        v = data[k].copy(); v[:, 1] -= lo; v *= sc; v[:, 1] -= 2.455; data[k] = v
    np.savez(sys.argv[1], **data)
    allv = np.vstack([data[k] for k in data if k.endswith('_v')])
    tris = {k[:-2]: len(data[k]) for k in data if k.endswith('_t')}
    print('triangles', sum(tris.values()), tris, 'bounds', allv.min(0).round(3), allv.max(0).round(3))
