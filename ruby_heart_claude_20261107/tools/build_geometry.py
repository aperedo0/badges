"""Build the Ruby Heart frame and gem meshes (model units, Y up, front +Z).

Usage: build_geometry.py FIT_JSON OUT_NPZ
The frame is a gold band swept along the reference outline, mirrored front and
back. The gem is a faceted crown (front) and its mirror (back) that meet the
frame's seat exactly. Every triangle of one facet shares that facet's normal.
"""
import sys, json
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/tools')
import facets

ROOT = '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107'
O = np.load(ROOT + '/trace/outline.npz')
OUTER = O['outer']
N_RING = 170          # points per half ring
SEAT = 0.39           # band width (gem edge offset from the outer outline)

def profile():
    """(o, z) points from the outer mid plane to the seat mid plane; o scales with SEAT."""
    k = SEAT / 0.375
    pts = [(0.0, 0.0), (0.0, 0.14)]
    r, fz = 0.07, 0.34
    for a in np.linspace(np.pi, np.pi / 2, 7):
        pts.append((r + r * np.cos(a), fz - r + r * np.sin(a)))
    pts += [(0.16 * k, 0.345), (0.25 * k, 0.350), (0.266 * k, 0.360), (0.284 * k, 0.360), (0.300 * k, 0.350),
            (0.330 * k, 0.305), (0.360 * k, 0.262), (0.370 * k, 0.250), (0.375 * k, 0.235), (SEAT, 0.12), (SEAT, 0.0)]
    pts = np.array(pts)
    crease = np.zeros(len(pts), bool)
    crease[[i for i, p in enumerate(pts) if abs(p[0] - 0.360 * k) < 1e-9]] = True   # bevel to lip
    return pts, crease

def resample(q, n):
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(q, axis=0), axis=1))]
    t = np.linspace(0, d[-1], n)
    return np.c_[np.interp(t, d, q[:, 0]), np.interp(t, d, q[:, 1])], t / d[-1]

BASE, _ = resample(OUTER, 600)

def inward_normals(q):
    t = np.gradient(q, axis=0); t /= np.linalg.norm(t, axis=1, keepdims=True)
    n = np.c_[t[:, 1], -t[:, 0]]
    if n[np.argmin(q[:, 0]), 0] < 0: n = -n
    return n

def ring(o):
    """Offset of the left half outline by o, clipped to x <= 0, resampled."""
    if o <= 0:
        q = BASE.copy()
    else:
        q = BASE + inward_normals(BASE) * o
        # clip at the center line from both ends
        inside = q[:, 0] < 0
        i0 = np.argmax(inside); i1 = len(q) - 1 - np.argmax(inside[::-1])
        def cross(a, b): return a + (b - a) * (a[0] / (a[0] - b[0]))
        top = cross(q[i0 - 1], q[i0]) if i0 > 0 else cross(q[i0 + 1], q[i0])
        bot = cross(q[i1], q[i1 + 1]) if i1 < len(q) - 1 else cross(q[i1 - 1], q[i1])
        q = np.vstack([[0, top[1]], q[i0:i1 + 1], [0, bot[1]]])
    q[0, 0] = q[-1, 0] = 0.0
    r, _ = resample(q, N_RING)
    r[0, 0] = r[-1, 0] = 0.0
    return r

def frame_half():
    """Front left quarter of the frame: vertices, normals, uv, quads."""
    prof, crease = profile()
    rings = [ring(o) for o in prof[:, 0]]
    # profile tangents -> outward normals in (o, z)
    V, Nn, UV, quads = [], [], [], []
    seglen = np.linalg.norm(np.diff(prof, axis=0), axis=1)
    vcoord = np.r_[0, np.cumsum(seglen)]
    for s in range(len(prof) - 1):
        # each profile segment gets its own strip of vertices (flat across creases, smooth otherwise)
        for end in (s, s + 1):
            pass
    # Smooth profile normals at points, split at creases.
    def pnormal(i, side):
        # side: -1 uses the incoming segment, +1 outgoing, 0 averaged
        def segn(j):
            do, dz = prof[j + 1] - prof[j]
            v = np.array([-dz, do]); return v / np.linalg.norm(v)
        if i == 0: return segn(0)
        if i == len(prof) - 1: return segn(i - 1)
        if side < 0: return segn(i - 1)
        if side > 0: return segn(i)
        v = segn(i - 1) + segn(i); return v / np.linalg.norm(v)
    base = 0
    for s in range(len(prof) - 1):
        ids = []
        for k, i in enumerate((s, s + 1)):
            side = 0
            if crease[i]: side = +1 if k == 0 else -1
            pn = pnormal(i, side)
            r = rings[i]; inn = inward_normals(r)
            # center line ends: use the mitre plane normal blend (keep the sweep normal)
            for j in range(N_RING):
                V.append([r[j, 0], r[j, 1], prof[i, 1]])
                n3 = np.array([pn[0] * inn[j, 0], pn[0] * inn[j, 1], pn[1]])
                Nn.append(n3 / np.linalg.norm(n3))
                UV.append([j / (N_RING - 1), vcoord[i] / vcoord[-1]])
            ids.append(base); base += N_RING
        a, b = ids
        for j in range(N_RING - 1):
            quads.append([a + j, a + j + 1, b + j + 1, b + j])
    return np.array(V), np.array(Nn), np.array(UV), np.array(quads)

def mirror_x(V, N, F):
    return V * [-1, 1, 1], N * [-1, 1, 1], F[:, ::-1]

def mirror_z(V, N, F):
    return V * [1, 1, -1], N * [1, 1, -1], F[:, ::-1]

def combine(parts):
    Vs, Ns, Us, Fs, off = [], [], [], [], 0
    for V, N, U, F in parts:
        Vs.append(V); Ns.append(N); Us.append(U); Fs.append(F + off); off += len(V)
    return np.vstack(Vs), np.vstack(Ns), np.vstack(Us), np.vstack(Fs)

def frame():
    V, N, U, Q = frame_half()
    parts = [(V, N, U, Q)]
    v2, n2, f2 = mirror_x(V, N, Q); parts.append((v2, n2, U, f2))
    out = []
    for V_, N_, U_, F_ in parts:
        out.append((V_, N_, U_, F_))
        v3, n3, f3 = mirror_z(V_, N_, F_); out.append((v3, n3, U_, f3))
    V, N, U, Q = combine(out)
    # quads -> triangles; flip so the geometric winding faces along the normal
    T = np.vstack([Q[:, [0, 1, 2]], Q[:, [0, 2, 3]]])
    return V, N, U, T

def gem(heights):
    """Front + back crown meeting the frame seat ring."""
    names, xy, girdle, faces = facets.layout()
    seat = ring(SEAT)                       # left half, notch -> tip, x <= 0
    seat_full_left = seat
    z = np.array([heights[k] if k in heights else heights[k[:-1]] for k in names])
    # snap girdle vertices to the seat ring (left), mirrored names to the mirrored ring
    ring_index = {}
    for i, k in enumerate(names):
        if not girdle[i]: continue
        p = xy[i] * ([-1, 1] if k.endswith("'") else [1, 1])
        j = int(np.argmin(np.linalg.norm(seat - p, axis=1)))
        if k == 'c0': j = 0
        if k == 'c5': j = N_RING - 1
        ring_index[i] = j
        xy[i] = seat[j] * ([-1, 1] if k.endswith("'") else [1, 1])
    P = np.c_[xy, z]
    V, N, T = [], [], []
    for f in faces:
        # polygon with seat curve points inserted between consecutive girdle vertices
        poly = []
        for a, b in zip(f, f[1:] + f[:1]):
            poly.append(P[a])
            if a in ring_index and b in ring_index:
                ja, jb = ring_index[a], ring_index[b]
                sgn = -1 if names[a].endswith("'") or names[b].endswith("'") else 1
                if abs(ja - jb) > 1:
                    step = 1 if jb > ja else -1
                    for j in range(ja + step, jb, step):
                        q = seat[j] * [sgn, 1]
                        poly.append(np.array([q[0], q[1], np.nan]))
        poly = np.array(poly)
        # facet plane from its real vertices
        real = P[list(f)]
        c = real.mean(0); u, s, vt = np.linalg.svd(real - c); n = vt[-1]
        if n[2] < 0: n = -n
        miss = np.isnan(poly[:, 2])
        poly[miss, 2] = (n @ c - n[0] * poly[miss, 0] - n[1] * poly[miss, 1]) / n[2]
        # project every point onto the plane so the facet is exactly flat
        poly[:, 2] = (n @ c - n[0] * poly[:, 0] - n[1] * poly[:, 1]) / n[2]
        cen = poly.mean(0); cen[2] = (n @ c - n[0] * cen[0] - n[1] * cen[1]) / n[2]
        base = len(V)
        V.append(cen); N.append(n)
        for p in poly:
            V.append(p); N.append(n)
        m = len(poly)
        for k in range(m):
            a, b = base + 1 + k, base + 1 + (k + 1) % m
            # orient counterclockwise seen from +z
            tri = [base, a, b]
            e1 = V[a] - V[base]; e2 = V[b] - V[base]
            if np.cross(e1, e2)[2] < 0: tri = [base, b, a]
            T.append(tri)
    V = np.array(V); N = np.array(N); T = np.array(T)
    Vb, Nb, Tb = mirror_z(V, N, T)
    V = np.vstack([V, Vb]); N = np.vstack([N, Nb]); T = np.vstack([T, Tb + len(Vb)])
    return V, N, T

def orient(V, N, T):
    """Make each triangle's winding agree with its vertex normals (outward)."""
    e = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    flip = np.sum(e * N[T].mean(1), 1) < 0
    T = T.copy(); T[flip] = T[flip][:, ::-1]
    return T

if __name__ == '__main__':
    fit = json.load(open(sys.argv[1]))
    fV, fN, fU, fT = frame(); fT = orient(fV, fN, fT)
    gV, gN, gT = gem(fit['heights']); gT = orient(gV, gN, gT)
    np.savez(sys.argv[2], frame_v=fV, frame_n=fN, frame_uv=fU, frame_t=fT, gem_v=gV, gem_n=gN, gem_t=gT)
    allv = np.vstack([fV, gV])
    print('frame tris', len(fT), 'gem tris', len(gT))
    print('bounds min', allv.min(0).round(3), 'max', allv.max(0).round(3))
