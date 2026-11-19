"""Build every part of the Radiant Mountain Sunburst as an exact closed solid (plan section 4).

Usage: geometry.py OUT_DIR
Reads design.json, writes OUT_DIR/parts.npz and OUT_DIR/parts.json. Python 3.11 with shapely 2.2.

Each part: a front surface meshed from the faces of its row arrangement (every offset row, crease and color
boundary is an edge), heights from exact distances, a mirrored back, and side walls (a lip row with the face's
normal and material, then the wall in the side material with normals blended 70% toward the face).
Parts stack back to front; each base is the highest earlier front surface under it plus 0.006.
"""
import sys, json
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, Point, box, GeometryCollection
from shapely.ops import unary_union, polygonize
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
D = json.load(open(HERE / 'design.json'))
S = 5.45 / 1161.0; AX = 653.5; LW = D['line_width']
GAP = 0.008; T18 = np.tan(np.radians(18)); T30 = np.tan(np.radians(30))


def geo(shape):
    return unary_union([Polygon(q['exterior'], q['holes']).buffer(0) for q in shape]) if shape else Polygon()


def parts_of(g):
    if g.is_empty:
        return []
    return [q for q in (g.geoms if hasattr(g, 'geoms') else [g]) if isinstance(q, Polygon) and q.area > 1]


def boundary_lines(g):
    out = []
    for q in parts_of(g):
        out.append(LineString(q.exterior.coords))
        out += [LineString(h.coords) for h in q.interiors]
    return out


def offsets(g, ds, inward=False):
    """Rows: outlines of g grown (or shrunk) by each distance in px."""
    rows = []
    for d in ds:
        b = g.buffer(-d if inward else d, quad_segs=6, join_style='round')
        rows += [l.simplify(0.15) for l in boundary_lines(b)]
    return rows


def mesh_faces(region, rows):
    """Faces of the arrangement of the region's boundary and the rows inside it, each triangulated along its edges."""
    lines = boundary_lines(region) + [r.intersection(region.buffer(0.01)) for r in rows]
    lines = [l for l in lines if not l.is_empty]
    noded = unary_union(lines)
    tris = []
    for face in polygonize(noded):
        if face.area < 0.05 or not region.buffer(0.02).contains(face.representative_point()):
            continue
        t = shapely.constrained_delaunay_triangles(face)
        tris += [np.asarray(x.exterior.coords)[:3] for x in t.geoms]
    return np.array(tris)                                        # (n, 3, 2) in px


class Part:
    def __init__(self, name, outline):
        self.name = name; self.outline = outline; self.vis = outline; self.base = 0.0
        self.tris = []; self.mats = []; self.normal_mode = []      # per triangle: material name, 'smooth' or 'flat'

    def z(self, x, y):
        raise NotImplementedError

    def add(self, tris, mat, mode):
        if len(tris):
            self.tris.append(tris); self.mats += [mat] * len(tris); self.normal_mode += [mode] * len(tris)

    def mesh_all(self, rows, classify):
        """One arrangement over the visible region (every row and material border an edge), materials by centroid."""
        t = mesh_faces(self.vis, rows)
        if len(t) == 0:
            return
        c = t.mean(1); mats, modes = classify(c[:, 0], c[:, 1])
        for m_ in sorted(set(mats)):
            sel = mats == m_
            self.add(t[sel], m_, modes[np.nonzero(sel)[0][0]])


def circle(c, r, n=360):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False); pts = np.c_[c[0] + r * np.cos(t), c[1] + r * np.sin(t)]
    return LineString(np.vstack([pts, pts[:1]]))


def dist(g, x, y):
    return shapely.distance(g, shapely.points(np.c_[x, y]))


def arc(d, half, h):
    t = np.clip(d / half, 0, 1); return h * (1 - (1 - t) ** 2)


# ---------------- design ----------------
ring = D['ring']; sun = D['sun']
RC = np.array(ring['center']); RR = ring['r_outer']; RI = ring['r_inner']
SC = np.array(sun['center']); SR = sun['r_enamel']; SRIM = sun['r_rim']
disc = Point(*RC).buffer(RR, quad_segs=96)
silhouette = geo(D['silhouette'])
parts = []

# 1. plate: cells (red, lemon) flat at 0.100, gold lines, the ring profile from the outer circle
class Plate(Part):
    def __init__(self):
        super().__init__('plate', disc)
        self.cells = [(c['color'], geo(c['shape']).buffer(-LW / 2, join_style='mitre', mitre_limit=3).buffer(-2).buffer(2)) for c in D['plate_cells']]
        self.cell_union = unary_union([q for _, q in self.cells])
        self.ring_prof = PchipInterpolator([0, 5, 10, 16, 20, 24, 29.5, 40], [0.080, 0.104, 0.118, 0.124, 0.117, 0.124, 0.100, 0.100])

    def z(self, x, y):
        r = np.hypot(x - RC[0], y - RC[1]); dout = np.clip(RR - r, 0, 40)
        zc = 0.100 + arc(dist(self.cell_union, x, y), LW / 2, 0.0095)
        inside = shapely.contains_xy(self.cell_union, x, y)
        zc = np.where(inside, 0.100, zc)
        return np.maximum(zc, self.ring_prof(dout))

    def build(self):
        rows = offsets(self.cell_union, [1.5, 3.0, 4.5]) + [circle(RC, RR - d, 240) for d in (5, 10, 16, 20, 24, 29.5)]
        rows += [l for _, q in self.cells for l in boundary_lines(q)]

        def classify(x, y):
            m = np.where(np.hypot(x - RC[0], y - RC[1]) > RR - 30, 'GoldRing', 'Gold').astype(object); md = np.full(len(x), 'smooth', dtype=object)
            for col, q in self.cells:
                ins = shapely.contains_xy(q, x, y); m[ins] = 'Red' if col == 'red' else 'Lemon'; md[ins] = 'flat'
            return m, md
        self.mesh_all(rows, classify)


# 2. spike points: four or so flat facets rising at 18 degrees from each edge (lower envelope of the edge planes)
class Spike(Part):
    def __init__(self, name, poly):
        super().__init__(name, poly.convex_hull)
        c = np.asarray(self.outline.exterior.coords)[:-1]
        self.edges = [(c[i], c[(i + 1) % len(c)]) for i in range(len(c)) if np.hypot(*(c[(i + 1) % len(c)] - c[i])) > 4]

    def edge_d(self, x, y):
        ds = []
        for a, b in self.edges:
            t = b - a; n = np.array([-t[1], t[0]]) / np.hypot(*t)
            ds.append(np.abs((x - a[0]) * n[0] + (y - a[1]) * n[1]))
        return np.array(ds)

    def z(self, x, y):
        return self.base + T18 * self.edge_d(x, y).min(0) * S

    def build(self):
        # facet regions, exact: inside a convex outline, edge i is nearest where (n_i - n_j) . p <= n_i . a_i - n_j . a_j
        cen = np.array(self.outline.centroid.coords[0]); NA = []
        for a, b in self.edges:
            t = b - a; n = np.array([-t[1], t[0]]) / np.hypot(*t)
            if np.dot(cen - a, n) < 0:
                n = -n
            NA.append((n, a))
        big = 4000
        for i, (ni, ai) in enumerate(NA):
            reg = self.outline
            for j, (nj, aj) in enumerate(NA):
                if i == j:
                    continue
                w = ni - nj; c = np.dot(ni, ai) - np.dot(nj, aj)
                if np.hypot(*w) < 1e-9:
                    continue
                # half plane w . p <= c as a big polygon
                u = w / np.hypot(*w); p0 = u * c / np.hypot(*w); v = np.array([-u[1], u[0]])
                hp = Polygon([p0 + v * big, p0 - v * big, p0 - v * big - u * big, p0 + v * big - u * big])
                reg = reg.intersection(hp)
            self.facets = getattr(self, 'facets', []) + parts_of(reg)
        rows = [l for q in self.facets for l in boundary_lines(q)]
        self.mesh_all(rows, lambda x, y: (np.full(len(x), 'Gold', dtype=object), np.full(len(x), 'flat', dtype=object)))


# 3. sun: rim and gentle dome
class Sun(Part):
    def __init__(self):
        super().__init__('sun', Point(*SC).buffer(SRIM, quad_segs=96))
        self.prof = PchipInterpolator([0, 6, 11, 15, 23, 40, 120, 218], [0.000, 0.016, 0.020, 0.014, 0.005, 0.012, 0.026, 0.035])

    def z(self, x, y):
        r = np.hypot(x - SC[0], y - SC[1]); return self.base + self.prof(np.clip(SRIM - r, 0, SRIM))

    def build(self):
        rows = [circle(SC, SRIM - d, 240) for d in (3, 6, 9, 11, 13, 15, 19, 23, 40, 80, 140)]
        rows.append(circle(SC, SR, 240))
        self.mesh_all(rows, lambda x, y: (np.where(np.hypot(x - SC[0], y - SC[1]) > SR, 'Gold', 'SunDisc').astype(object), np.full(len(x), 'smooth', dtype=object)))


# 4, 5. mountains: two planar facets split at the peak; colored cells; gold lines and the outline band
class Mountain(Part):
    def __init__(self, name, m, rise):
        super().__init__(name, geo(m['outline']))
        self.peak = np.array(m['peak']); self.rise = rise
        b = self.outline.bounds; self.y_bot = b[3]
        # the blue faces (teal, navy, steel) meet at creases, not gold lines: they share one inset for the gold
        raw = [(c['color'], geo(c['shape'])) for c in m['cells']]
        blue = unary_union([q for c, q in raw if c in ('teal', 'navy', 'steel')]).buffer(0.6).buffer(-0.6)
        groups = [(c, q) for c, q in raw if c not in ('teal', 'navy', 'steel')] + ([('blue', blue)] if not blue.is_empty else [])
        inset = lambda q: q.buffer(-LW / 2, join_style='mitre', mitre_limit=3).intersection(self.outline.buffer(-14))
        self.cells = []
        for c, q in groups:
            qi = inset(q)
            if c == 'blue':
                self.cells += [(cc, qq.intersection(qi)) for cc, qq in raw if cc in ('teal', 'navy', 'steel')]
            else:
                self.cells.append((c, qi))
        self.cell_union = unary_union([inset(q) for _, q in groups])
        xs = np.asarray(self.outline.exterior.coords)[:, 0]; self.xl, self.xr = xs.min(), xs.max()

    def plane(self, x, y):
        # left facet falls toward the lower left, right facet toward the lower right; base at the far bottom corners
        px, py = self.peak; h = self.rise
        left = x <= px
        fx = np.where(left, (px - x) / max(px - self.xl, 1), (x - px) / max(self.xr - px, 1))
        fy = (y - py) / max(self.y_bot - py, 1)
        return self.base + h * np.clip(1 - 0.6 * fx - 0.4 * fy, 0, 1)

    def z(self, x, y):
        zc = arc(np.minimum(dist(self.cell_union, x, y), dist(self.outline.exterior, x, y) + 0.0), LW / 2, 0.0095)
        zc = np.where(shapely.contains_xy(self.cell_union, x, y), 0.0, zc)
        return self.plane(x, y) + zc

    def build(self):
        split = LineString([(self.peak[0], 0), (self.peak[0], 1300)])
        rows = offsets(self.cell_union, [1.5, 3.0, 4.5]) + offsets(self.outline, [1.5, 3.0, 4.5], inward=True) + [split]
        rows += [l for _, q in self.cells for l in boundary_lines(q)]
        px_ = self.peak[0]

        def classify(x, y):
            m = np.full(len(x), 'Gold', dtype=object); md = np.full(len(x), 'smooth', dtype=object)
            for col, q in self.cells:
                ins = shapely.contains_xy(q, x, y)
                if col == 'snow_white':
                    m[ins & (x <= px_)] = 'Snow'; m[ins & (x > px_)] = 'SnowLavender'
                else:
                    m[ins] = {'royal': 'Royal', 'teal': 'Teal', 'navy': 'Navy', 'steel': 'Steel', 'navy_chevron': 'Navy'}[col]
                md[ins] = 'flat'
            return m, md
        self.mesh_all(rows, classify)


# 6 to 8. the lower part: cloud cells (flat white), the border band, cloud outlines and curls as one surface
class Lower(Part):
    def __init__(self):
        cells = unary_union([geo(c) for c in D['cloud_cells']])
        self.cloud = cells.buffer(-LW / 2, join_style='mitre', mitre_limit=3).buffer(-2).buffer(2)
        self.cloud = unary_union([q for q in parts_of(self.cloud) if q.area > 2500])          # no tiny leftover cells
        gold = geo(D['lower_gold'])
        super().__init__('lower', unary_union([gold, self.cloud]).buffer(0))
        self.border_prof = PchipInterpolator([0, 8, 14, 20, 24, 28, 32, 40, 60], [0.000, 0.016, 0.021, 0.016, 0.010, 0.015, 0.016, 0.006, 0.006])
        self.sil = silhouette.exterior

    def z(self, x, y):
        dc = dist(self.cloud, x, y); inside = shapely.contains_xy(self.cloud, x, y)
        zl = np.where(inside, 0.004, 0.004 + arc(dc, 17.6, 0.030) + 0.006 * np.clip((dc - 17.6) / 25, 0, 1))   # a gentle ridge, no flat top
        zb = self.border_prof(np.clip(dist(self.sil, x, y), 0, 60))
        return self.base + np.maximum(zl, zb)

    def build(self):
        rows = offsets(self.cloud, [1.5, 3.0, 5.0, 8.0, 12.0]) + offsets(silhouette, [8, 14, 20, 24, 28, 32, 40], inward=True)
        rows += boundary_lines(self.cloud)

        def classify(x, y):
            ins = shapely.contains_xy(self.cloud, x, y)
            return np.where(ins, 'Cloud', 'GoldLower').astype(object), np.where(ins, 'flat', 'smooth').astype(object)
        self.mesh_all(rows, classify)


# 9, 10. gem and star frame
gem_pts = np.array(D['gem']['outline'], float); APEX = np.array(D['gem']['apex'], float)


class Gem(Part):
    def __init__(self):
        super().__init__('gem', Polygon(gem_pts).buffer(2, join_style='mitre'))
        self.rise = 0.12

    def facet_planes(self):
        # 8 planes through the apex and consecutive girdle points (tips and inner corners)
        P = []
        g = np.asarray(self.outline.exterior.coords)[:-1]
        return g

    def z(self, x, y):
        # cone like star: height falls linearly with the distance ratio to the outline along the ray from the apex
        ang = np.arctan2(y - APEX[1], x - APEX[0]); r = np.hypot(x - APEX[0], y - APEX[1])
        out = []
        for a_, r_ in zip(ang, r):
            ray = LineString([tuple(APEX), (APEX[0] + 2000 * np.cos(a_), APEX[1] + 2000 * np.sin(a_))])
            hit = ray.intersection(self.outline.exterior)
            R = min((np.hypot(p.x - APEX[0], p.y - APEX[1]) for p in (hit.geoms if hasattr(hit, 'geoms') else [hit]) if not p.is_empty), default=1.0)
            out.append(self.base + self.rise * max(0.0, 1 - r_ / max(R, 1e-6)))
        return np.array(out)

    def build(self):
        g = np.asarray(self.outline.exterior.coords)[:-1]
        tris = np.array([[APEX, g[i], g[(i + 1) % len(g)]] for i in range(len(g))])
        self.add(tris, 'Gem', 'flat')


class Frame(Part):
    def __init__(self, gem):
        self.gem = gem
        super().__init__('frame', geo(D['frame']).difference(Polygon(gem_pts)).buffer(0))
        self.inner = Polygon(gem_pts).exterior; self.outer = geo(D['frame']).exterior

    def z(self, x, y):
        zo = self.base + T30 * dist(self.outer, x, y) * S
        zi = self.gem.base + 0.016 + T30 * dist(self.inner, x, y) * S
        return np.minimum(zo, zi)

    def build(self):
        rows = offsets(geo(D['frame']), [3, 6, 10, 14, 20], inward=True) + offsets(Polygon(gem_pts), [3, 6, 10, 14, 20])
        self.mesh_all(rows, lambda x, y: (np.full(len(x), 'Gold', dtype=object), np.full(len(x), 'smooth', dtype=object)))


# ---------------- assemble the stack ----------------
plate = Plate(); parts.append(plate)
for s in D['spikes']:
    parts.append(Spike(s['name'], geo(s['shape'])))
parts.append(Sun())
parts.append(Mountain('mountain_side_left', D['mountains']['side_left'], 0.05))
parts.append(Mountain('mountain_side_right', D['mountains']['side_right'], 0.05))
parts.append(Mountain('mountain_central', D['mountains']['central'], 0.08))
lower = Lower(); parts.append(lower)
gem = Gem(); frame = Frame(gem)
parts += [frame, gem]
pair_groups = {'mountain_side_left': 'side', 'mountain_side_right': 'side'}


def sample_points(region, step=3.0):
    bx0, by0, bx1, by1 = region.bounds
    X, Y = np.meshgrid(np.arange(bx0, bx1 + step, step), np.arange(by0, by1 + step, step))
    x, y = X.ravel(), Y.ravel(); keep = shapely.contains_xy(region, x, y)
    bp = []
    for l in boundary_lines(region):
        n = max(int(l.length / 2), 4); bp += [l.interpolate(t, normalized=True).coords[0] for t in np.linspace(0, 1, n)]
    bp = np.array(bp) if bp else np.zeros((0, 2))
    return np.r_[x[keep], bp[:, 0]], np.r_[y[keep], bp[:, 1]]


done = []
for p in parts:
    if p is plate:
        p.base = 0.0
    else:
        reg = p.outline.buffer(2)
        x, y = sample_points(reg)
        top = 0.0
        for q in done:
            if isinstance(q, Frame) or (isinstance(p, Frame) and isinstance(q, Gem)):
                continue
            inside = shapely.contains_xy(q.outline, x, y)
            if inside.any():
                top = max(top, float(q.z(x[inside], y[inside]).max()))
        p.base = top + GAP
    done.append(p)
gem.base = max(gem.base, frame.base)
# mirrored pairs share one base
sb = max(p.base for p in parts if p.name.startswith('mountain_side'))
for p in parts:
    if p.name.startswith('mountain_side'):
        p.base = sb
sp = {}
for p in parts:
    if isinstance(p, Spike):
        k = p.name.replace('_mirror', ''); sp[k] = max(sp.get(k, 0), p.base)
for p in parts:
    if isinstance(p, Spike):
        p.base = sp[p.name.replace('_mirror', '')]
print('bases', {p.name: round(p.base, 4) for p in parts})

# visible outlines: each part minus what the later parts cover (they are closed solids through the full thickness)
for i, p in enumerate(parts):
    later = [q.outline for q in parts[i + 1:] if not isinstance(q, Gem)]
    if later and not isinstance(p, Gem):
        v = p.outline.difference(unary_union(later).buffer(-4)).buffer(0)
        p.vis = unary_union([q for q in parts_of(v) if q.area > 30])

# ---------------- solids: front, back, side walls ----------------
out = {}; meta = []
for p in parts:
    p.build()
    T = np.vstack(p.tris)                                          # (n, 3, 2) px
    mats = np.array(p.mats, dtype=object); modes = np.array(p.normal_mode, dtype=object)
    # weld the front: one vertex per position, so faces and walls share exact points
    key = np.round(T.reshape(-1, 2), 3); uq, inv = np.unique(key, axis=0, return_inverse=True); F = inv.reshape(-1, 3)
    good = (F[:, 0] != F[:, 1]) & (F[:, 1] != F[:, 2]) & (F[:, 0] != F[:, 2])
    F, mats, modes = F[good], mats[good], modes[good]
    x, y = uq[:, 0], uq[:, 1]
    if isinstance(p, Gem):
        z = np.where(np.hypot(x - APEX[0], y - APEX[1]) < 0.01, p.base + p.rise, p.base)
    else:
        z = p.z(x, y)
    P3 = np.c_[(x - AX) * S, 2.995 - (y - 15.0) * S, z]
    V = P3[F]
    n = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0]); flip = n[:, 2] < 0
    F[flip] = F[flip][:, ::-1]; V = P3[F]; n = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0])
    fn = n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    Nc = np.repeat(fn[:, None, :], 3, 1)
    smooth = modes == 'smooth'
    vn = None
    if smooth.any() and not isinstance(p, Gem):
        h = 0.35
        dzx = (p.z(x + h, y) - p.z(x - h, y)) / (2 * h * S); dzy = (p.z(x, y + h) - p.z(x, y - h)) / (2 * h * S)
        vn = np.c_[-dzx, dzy, np.ones_like(dzx)]; vn /= np.linalg.norm(vn, axis=1, keepdims=True)
        Nc[smooth] = vn[F[smooth]]
    # boundary edges: used by one front triangle; walls follow them exactly
    E = np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]); Em = np.concatenate([mats, mats, mats])
    Es = np.sort(E, 1); _, idx, cnt = np.unique(Es, axis=0, return_index=True, return_counts=True)
    bE = E[idx[cnt == 1]]; bM = Em[idx[cnt == 1]]
    # outward direction of each boundary edge: to the right of a counterclockwise front (model X right, Y up)
    d = P3[bE[:, 1], :2] - P3[bE[:, 0], :2]; out_n = np.c_[d[:, 1], -d[:, 0]]
    out_n /= np.maximum(np.linalg.norm(out_n, axis=1, keepdims=True), 1e-12)
    vout = np.zeros((len(P3), 2))
    np.add.at(vout, bE[:, 0], out_n); np.add.at(vout, bE[:, 1], out_n)
    vout /= np.maximum(np.linalg.norm(vout, axis=1, keepdims=True), 1e-12)
    face_up = np.array([0, 0, 1.0]); lipd = 0.004
    zt = P3[:, 2]
    levels = [zt, zt - lipd, -(zt - lipd), -zt] if not isinstance(p, Gem) else [zt, zt - lipd, np.zeros(len(zt)), -(zt - lipd), -zt]
    side = 0.3 * np.c_[vout, np.zeros(len(P3))] + 0.7 * face_up
    side /= np.linalg.norm(side, axis=1, keepdims=True)
    WV, WN, WM = [], [], []
    nl = len(levels) - 1
    for k in range(nl):
        za, zb = levels[k], levels[k + 1]
        for (a, b), mm in zip(bE, bM):
            A0 = np.r_[P3[a, :2], za[a]]; A1 = np.r_[P3[b, :2], za[b]]; B0 = np.r_[P3[a, :2], zb[a]]; B1 = np.r_[P3[b, :2], zb[b]]
            sa = 1 if np.mean([za[a], za[b]]) >= 0 else -1; sb = 1 if np.mean([zb[a], zb[b]]) > 0 else -1
            if k == 0:
                na_, nb_ = (Nc[0, 0] * 0 + (vn[a] if vn is not None else face_up)), side[a] * [1, 1, sb]
                na1, nb1 = (vn[b] if vn is not None else face_up), side[b] * [1, 1, sb]
                mat = mm
            elif k == nl - 1:
                na_, na1 = side[a] * [1, 1, sa], side[b] * [1, 1, sa]
                nb_ = (vn[a] if vn is not None else face_up) * [1, 1, -1]; nb1 = (vn[b] if vn is not None else face_up) * [1, 1, -1]
                mat = mm
            else:
                na_, na1, nb_, nb1 = side[a] * [1, 1, sa], side[b] * [1, 1, sa], side[a] * [1, 1, sb], side[b] * [1, 1, sb]
                mat = 'Gem' if isinstance(p, Gem) else 'Side'
            # quad (A0, A1, B1, B0) facing outward
            for tri, nn in (((A0, B0, A1), (na_, nb_, na1)), ((A1, B0, B1), (na1, nb_, nb1))):
                tri = np.array(tri); nn = np.array(nn, float)
                f = np.cross(tri[1] - tri[0], tri[2] - tri[0])
                o = np.r_[(out_n[0] * 0), 0]
                WV.append(tri); WN.append(nn); WM.append(mat)
    WV = np.array(WV).reshape(-1, 3, 3) if WV else np.zeros((0, 3, 3)); WN = np.array(WN).reshape(-1, 3, 3) if WN else np.zeros((0, 3, 3))
    # orient every wall triangle outward (its normal along the edge's outward direction)
    if len(WV):
        fwn = np.cross(WV[:, 1] - WV[:, 0], WV[:, 2] - WV[:, 0]); cen = WV.mean(1)[:, :2]
        # the outward direction of the edge the triangle came from
        reps = np.tile(out_n, (2, 1)); reps = np.repeat(out_n, 2, 0); reps = np.tile(reps, (nl, 1))
        bad = np.einsum('ij,ij->i', fwn[:, :2], reps) < 0
        WV[bad] = WV[bad][:, ::-1]; WN[bad] = WN[bad][:, ::-1]
    Vb = V * [1, 1, -1]; Vb = Vb[:, ::-1]; Nb = (Nc * [1, 1, -1])[:, ::-1]
    allV = np.concatenate([V, Vb, WV]); allN = np.concatenate([Nc, Nb, WN]); allM = np.concatenate([mats, mats, np.array(WM, dtype=object)])
    pxv = allV[..., 0] / S + AX; pyv = 15.0 + (2.995 - allV[..., 1]) / S
    UV = np.stack([pxv / 1312.0, 1 - pyv / 1199.0], -1)
    if isinstance(p, Gem):
        front = allV.mean(1)[:, 2] >= 0
        UV = np.where(front[:, None, None], np.array([0.0, 0.5]), np.array([0.5, 0.5])) * np.ones_like(UV)
    out[p.name + '_uv'] = UV.astype(np.float32)
    out[p.name + '_v'] = allV.astype(np.float32); out[p.name + '_n'] = allN.astype(np.float32)
    names = sorted(set(allM)); out[p.name + '_m'] = np.array([names.index(m) for m in allM], np.int16)
    meta.append(dict(name=p.name, base=p.base, materials=names, triangles=int(len(allV)), front=int(len(V))))
    print(f'{p.name:22s} base {p.base:.4f} front {len(V):6d} total {len(allV):6d} max front z {float(V[..., 2].max()):.3f}')
np.savez_compressed(OUT / 'parts.npz', **out)
order = [p.name for p in parts]
vorder = [n for n in order if n != 'gem']; vorder.insert(vorder.index('frame'), 'gem')      # the frame overlaps the gem's tucked rim
json.dump(dict(parts=meta, order=order, validate_order=vorder), open(OUT / 'parts.json', 'w'), indent=1)
print('triangles', sum(m['triangles'] for m in meta))
