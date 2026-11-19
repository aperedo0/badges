"""Small mesh toolkit for the crown: grids, sweeps, revolutions, flat faceted gems.

Model space: Y up, front +Z, angle theta measured from +Z toward +X.
Every builder returns a Part(V, N, T, UV) with per vertex normals; UV may be None.
"""
import numpy as np


class Part:
    def __init__(self, V, N, T, UV=None):
        self.V = np.asarray(V, float)
        self.N = np.asarray(N, float)
        self.T = np.asarray(T, int).reshape(-1, 3)
        self.UV = None if UV is None else np.asarray(UV, float)

    def transformed(self, M, origin):
        """Rotate by 3x3 M (columns = new axes) and move to origin."""
        return Part(self.V @ M.T + origin, self.N @ M.T, self.T, self.UV)


def merge(parts):
    Vs, Ns, Ts, UVs, off = [], [], [], [], 0
    has_uv = any(p.UV is not None for p in parts)
    for p in parts:
        Vs.append(p.V); Ns.append(p.N); Ts.append(p.T + off); off += len(p.V)
        if has_uv:
            UVs.append(p.UV if p.UV is not None else np.zeros((len(p.V), 2)))
    if not parts:
        return Part(np.zeros((0, 3)), np.zeros((0, 3)), np.zeros((0, 3), int))
    return Part(np.vstack(Vs), np.vstack(Ns), np.vstack(Ts), np.vstack(UVs) if has_uv else None)


def unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12)


def orient(p):
    """Wind every triangle so its geometric normal agrees with its vertex normals."""
    if len(p.T) == 0:
        return p
    e = np.cross(p.V[p.T[:, 1]] - p.V[p.T[:, 0]], p.V[p.T[:, 2]] - p.V[p.T[:, 0]])
    flip = np.sum(e * p.N[p.T].mean(1), 1) < 0
    T = p.T.copy(); T[flip] = T[flip][:, ::-1]
    return Part(p.V, p.N, T, p.UV)


def grid(P, closed_v=False, hint=None, uv=None):
    """P (nu, nv, 3): u across the profile, v along the sweep or around.

    Normals from the grid's partial derivatives, flipped to agree with hint
    (nu, nv, 3) when given. closed_v wraps v.
    """
    nu, nv = P.shape[:2]
    Pu = np.gradient(P, axis=0) if nu > 1 else np.zeros_like(P)
    if closed_v:
        Pv = (np.roll(P, -1, axis=1) - np.roll(P, 1, axis=1)) / 2
    else:
        Pv = np.gradient(P, axis=1)
    N = np.cross(Pu, Pv)
    ln = np.linalg.norm(N, axis=-1)
    if hint is not None:
        bad = ln < 1e-10
        N[bad] = hint[bad]
        N = np.where((np.sum(N * hint, -1) < 0)[..., None], -N, N)
    N = unit(N)
    idx = np.arange(nu * nv).reshape(nu, nv)
    T = []
    jmax = nv if closed_v else nv - 1
    for i in range(nu - 1):
        for j in range(jmax):
            a, b = idx[i, j], idx[i, (j + 1) % nv]
            c, d = idx[i + 1, (j + 1) % nv], idx[i + 1, j]
            T += [(a, b, c), (a, c, d)]
    UV = None if uv is None else uv.reshape(-1, 2)
    return orient(Part(P.reshape(-1, 3), N.reshape(-1, 3), np.array(T), UV))


def resample_polyline(pts, n):
    pts = np.asarray(pts, float)
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    t = np.linspace(0, d[-1], n)
    return np.stack([np.interp(t, d, pts[:, k]) for k in range(pts.shape[1])], -1), t


def catmull(ctrl, n_per=20):
    """Smooth curve through control points (centripetal enough for our use)."""
    c = np.asarray(ctrl, float)
    c = np.vstack([2 * c[0] - c[1], c, 2 * c[-1] - c[-2]])
    out = []
    for i in range(1, len(c) - 2):
        p0, p1, p2, p3 = c[i - 1], c[i], c[i + 1], c[i + 2]
        for t in np.linspace(0, 1, n_per, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(c[-2])
    return np.array(out)


def revolve(profile, n_around, theta0=0.0, disp=None, hint_out=True):
    """profile (m, 2) of (r, y). disp(theta, k) -> extra radial and vertical offset arrays."""
    profile = np.asarray(profile, float)
    th = theta0 + np.linspace(0, 2 * np.pi, n_around, endpoint=False)
    R = profile[:, 0][:, None] * np.ones((1, n_around))
    Y = profile[:, 1][:, None] * np.ones((1, n_around))
    if disp is not None:
        dr, dy = disp(th[None, :], np.arange(len(profile))[:, None])
        R = R + dr; Y = Y + dy
    P = np.stack([R * np.sin(th), Y, R * np.cos(th)], -1)
    # hint: profile outward normal (rotate tangent) mapped to 3D
    t = np.gradient(profile, axis=0)
    n2 = np.stack([t[:, 1], -t[:, 0]], -1)  # (dr, dy) rotated: right of travel
    if not hint_out:
        n2 = -n2
    H = np.stack([n2[:, 0][:, None] * np.sin(th), np.repeat(n2[:, 1][:, None], n_around, 1), n2[:, 0][:, None] * np.cos(th)], -1)
    return grid(P, closed_v=True, hint=H)


def frames_along(C, up_fn):
    """Tangent T, across A, out O along curve C; O is up_fn(point) made perpendicular to T."""
    T = unit(np.gradient(C, axis=0))
    O = unit(np.array([up_fn(p) for p in C]))
    O = unit(O - np.sum(O * T, -1, keepdims=True) * T)
    A = unit(np.cross(T, O))
    return T, A, O


def sweep(C, A, O, profile, scale_a=None, scale_o=None, closed_profile=True, uv_along=None):
    """profile (m, 2) of (a, o); scale_* (n,) per curve point. Returns Part with hint from the profile."""
    profile = np.asarray(profile, float)
    n = len(C)
    sa = np.ones(n) if scale_a is None else np.asarray(scale_a)
    so = np.ones(n) if scale_o is None else np.asarray(scale_o)
    pa = profile[:, 0][:, None] * sa[None, :]
    po = profile[:, 1][:, None] * so[None, :]
    P = C[None] + pa[..., None] * A[None] + po[..., None] * O[None]
    if closed_profile:
        P = np.concatenate([P, P[:1]], 0)
        prof = np.vstack([profile, profile[:1]])
    else:
        prof = profile
    # hint from the profile's outward normal (profile wound counterclockwise in (a, o))
    t = np.gradient(prof, axis=0)
    n2 = np.stack([t[:, 1], -t[:, 0]], -1)
    H = n2[:, 0][:, None, None] * A[None] + n2[:, 1][:, None, None] * O[None]
    uv = None
    if uv_along is not None:
        u = np.linspace(0, 1, P.shape[0])
        uv = np.stack(np.meshgrid(uv_along, u)[::-1], -1)[..., ::-1]
    return grid(P, closed_v=False, hint=H, uv=uv)


def cap(points, normal):
    """Flat fan cap over a closed loop of points (convex-ish)."""
    c = points.mean(0)
    V = np.vstack([c, points]); N = np.repeat(np.asarray(normal, float)[None], len(V), 0)
    m = len(points)
    T = [(0, 1 + k, 1 + (k + 1) % m) for k in range(m)]
    return orient(Part(V, N, np.array(T)))


# ---------- faceted foil gems ----------

def encode_axis(axis):
    """Foil axis in the first UV set: (azimuth / 2 pi, elevation / pi + 0.5); azimuth from +Z toward +X."""
    a = unit(np.asarray(axis, float))
    az = (np.arctan2(a[0], a[2]) / (2 * np.pi)) % 1.0
    el = np.arcsin(np.clip(a[1], -1, 1)) / np.pi + 0.5
    return np.array([az, el])


def gem(outline, rings, apex_h, frame, origin):
    """Flat faceted crown over a 2D outline (k, 2) in the gem plane.

    rings: list of (scale, height) for inner rings; apex at apex_h.
    frame: 3x3 with columns (x, y, axis) in model space. Each facet gets its own
    vertices so every facet is flat. UV holds the encoded foil axis.
    """
    outline = np.asarray(outline, float)
    k = len(outline)
    levels = [(1.0, 0.0)] + list(rings)
    L = [np.c_[outline * s, np.full(k, h)] for s, h in levels]
    apex = np.array([0, 0, apex_h])
    V, N, T = [], [], []

    def add(poly):
        poly = np.asarray(poly)
        nrm = unit(np.cross(poly[1] - poly[0], poly[2] - poly[0]))
        if nrm[2] < 0:
            nrm = -nrm
        base = len(V)
        for p in poly:
            V.append(p); N.append(nrm)
        for j in range(1, len(poly) - 1):
            T.append((base, base + j, base + j + 1))

    for a, b in zip(L[:-1], L[1:]):
        for i in range(k):
            j = (i + 1) % k
            add([a[i], a[j], b[j], b[i]])
    last = L[-1]
    for i in range(k):
        add([last[i], last[(i + 1) % k], apex])
    V = np.array(V); N = np.array(N)
    M = np.asarray(frame, float)
    p = orient(Part(V, N, np.array(T)))
    p = p.transformed(M, np.asarray(origin, float))
    p.UV = np.repeat(encode_axis(M[:, 2])[None], len(p.V), 0)
    return p


def frame_on_surface(normal, up=(0, 1, 0)):
    """Columns (x, y, axis): axis = outward normal, y = up projected, x = y cross axis."""
    z = unit(np.asarray(normal, float))
    y = np.asarray(up, float) - np.dot(up, z) * z
    if np.linalg.norm(y) < 1e-6:
        y = np.array([0, 0, -1.0]) - np.dot([0, 0, -1.0], z) * z
    y = unit(y); x = np.cross(y, z)
    return np.stack([x, y, z], 1)


def ngon(n, rx, ry=None, phase=0.0):
    ry = rx if ry is None else ry
    a = phase + np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.c_[rx * np.cos(a), ry * np.sin(a)]


def rhombus(w, h, mid=True):
    pts = np.array([[0, h / 2], [-w / 2, 0], [0, -h / 2], [w / 2, 0]])
    if not mid:
        return pts
    out = []
    for i in range(4):
        out.append(pts[i]); out.append((pts[i] + pts[(i + 1) % 4]) / 2)
    return np.array(out)
