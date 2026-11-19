"""Build any 3D badge from a pieces file: exact closed solids, stacked, with bevels, rims and colored cells.

Usage: badge3d.py PIECES.json OUT_DIR
Python 3.11 with numpy, scipy and shapely 2.2. Writes OUT_DIR/parts.npz and OUT_DIR/parts.json (the format that
write_usdz.py, build_live.py and validate.py read).

PIECES.json (all lengths in mockup pixels unless the name ends in an a unit height):
{
 "units": {"S": units per pixel, "axis": mirror column x, "top": mockup row of Y 2.995},
 "gap": 0.008,                                   # every piece stands at least this far above what it covers
 "pieces": [                                     # back to front; later pieces sit on earlier ones
  {"name": "sun", "outline": SHAPE, "material": "Gold", "side": "Side",
   "base": 0.06,                                 # optional fixed base (else computed by the stack rule)
   "same_base_as": "other piece",                # optional, for mirrored twins
   "base_ignore": ["piece"],                     # optional, pieces left out of the stack rule (a frame over its gem)
   "base_from": {"piece": "frame", "offset": -0.012},   # optional, base relative to another piece
   "top": {"kind": "flat", "height": 0.0, "dome": 0.0}             # flat top, optional dome toward the middle
        # profile tops take "from": SHAPE to measure heights from that outline instead of the piece's own (a base with openings under covering pieces)
        | {"kind": "roof", "slope_deg": 18}                         # convex outline: flat facets rising from each edge
        | {"kind": "planes", "facets": [{"shape": SHAPE, "p": [[x, y, h], [x, y, h], [x, y, h]]}]}   # facets through points
        | {"kind": "profile", "points": [[d, h], ...]},             # height by distance from the outline (rings, borders)
   "bevel": {"width": 9, "height": 0.03},        # the outer edge rises over this width (no knife edges)
   "rim": {"width": 12, "height": 0.03, "material": "Gold"},       # a raised gold rim just inside the outline
   "cells": [{"material": "Lemon", "shape": SHAPE, "recess": {"depth": 0.012, "width": 6}}],  # colored areas, optionally set in; the slope is the piece's metal, the color only on the flat floor (grow a traced fill by the slope width)
   "lines": {"width": 11.5, "height": 0.02, "material": "Gold"},   # raised lines between cells of different groups
   "edge_skip": SHAPE,                           # no bevel or rim along outline parts on this shape (its own gold edge is there)
   "cell_groups": {"Teal": "blue", "Navy": "blue"},                 # cells in one group meet at a crease, no line
   "gem": {"apex": [x, y], "rise": 0.12}         # a faceted crystal (outline points as girdle), material "Gem"
  }]
}
SHAPE: [{"exterior": [[x, y], ...], "holes": [[[x, y], ...], ...]}, ...]

Rules built in (badge-plan and badge-quality): triangles follow every outline, bevel, rim, line, cell border and
crease; heights come from exact distances; each piece is a closed solid (front, mirrored back, side walls built
from the front's exact boundary: a lip row with the face's normal and material, then the wall in the side material
with normals blended 70% toward the face); pieces stack with a computed base; hidden areas are not meshed.
"""
import sys, json
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union, polygonize
from scipy.interpolate import PchipInterpolator

SPEC = json.load(open(sys.argv[1])); OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
S = SPEC['units']['S']; AX = SPEC['units']['axis']; TOP = SPEC['units'].get('top', 15.0); GAP = SPEC.get('gap', 0.008)


def geo(shape):
    return unary_union([Polygon(q['exterior'], q.get('holes', [])).buffer(0) for q in shape]) if shape else Polygon()


def polys(g):
    if g.is_empty:
        return []
    return [q for q in (g.geoms if hasattr(g, 'geoms') else [g]) if isinstance(q, Polygon) and q.area > 0.5]


def lines_of(g):
    out = []
    for q in polys(g):
        out.append(LineString(q.exterior.coords)); out += [LineString(h.coords) for h in q.interiors]
    return out


def offsets(g, ds, inward=True):
    rows = []
    for d in ds:
        if d <= 0:
            continue
        b = g.buffer(-d if inward else d, quad_segs=4)
        rows += [l.simplify(0.5) for l in lines_of(b)]
    return rows


def dist(g, x, y):
    return shapely.distance(g, shapely.points(np.c_[x, y]))


def mesh_faces(region, rows):
    lines = lines_of(region) + [r.intersection(region.buffer(0.01)) for r in rows]
    noded = unary_union([l for l in lines if not l.is_empty])
    tris = []
    for face in polygonize(noded):
        if face.area < 0.05 or not region.buffer(0.02).contains(face.representative_point()):
            continue
        t = shapely.constrained_delaunay_triangles(face)
        tris += [np.asarray(x.exterior.coords)[:3] for x in t.geoms]
    return np.array(tris) if tris else np.zeros((0, 3, 2))


def bevel_curve(width, height):
    """Rises from 0 at the outline to `height` at `width`, at a steady slope with soft ends."""
    return lambda d: height * np.clip(d / max(width, 1e-6), 0, 1) ** 1 * (1 - 0.15 * (1 - np.clip(d / max(width, 1e-6), 0, 1)))


class Piece:
    def __init__(self, spec):
        self.spec = spec; self.name = spec['name']; self.outline = geo(spec['outline']); self.vis = self.outline
        self.base = spec.get('base'); self.top = spec.get('top', {'kind': 'flat', 'height': 0.0})
        self.cells = [(c['material'], geo(c['shape']), c.get('recess')) for c in spec.get('cells', [])]
        self.rim = spec.get('rim'); self.bev = spec.get('bevel'); self.lines = spec.get('lines'); self.gem = spec.get('gem')
        self.groups = spec.get('cell_groups', {})
        self.edge = unary_union([l for l in lines_of(self.outline)])
        skip = geo(spec['edge_skip']) if spec.get('edge_skip') else None
        self.edge_b = self.edge.difference(skip.buffer(2.5)) if skip is not None else self.edge     # where bevel and rim apply
        if self.edge_b.is_empty:
            self.edge_b = self.edge
        self.inner_r = max((shapely.maximum_inscribed_circle(q).length for q in polys(self.outline)), default=1.0)
        if self.top['kind'] == 'profile':
            pts = np.array(self.top['points'], float); self.prof = PchipInterpolator(pts[:, 0], pts[:, 1])
            self.prof_shape = geo(self.top['from']) if self.top.get('from') else self.outline   # distances from this outline
            self.prof_edge = unary_union(lines_of(self.prof_shape))
        if self.top['kind'] == 'roof':
            c = np.asarray(self.outline.convex_hull.exterior.coords)[:-1]; cen = np.array(self.outline.centroid.coords[0]); self.NA = []
            for i in range(len(c)):
                a, b = c[i], c[(i + 1) % len(c)]
                if np.hypot(*(b - a)) < 3:
                    continue
                t = b - a; n = np.array([-t[1], t[0]]) / np.hypot(*t)
                if np.dot(cen - a, n) < 0:
                    n = -n
                self.NA.append((n, a))
        if self.top['kind'] == 'planes':
            self.facets = []
            for f in self.top['facets']:
                P = np.array(f['p'], float); P3 = np.c_[P[:, 0], P[:, 1], P[:, 2]]
                nrm = np.cross(P3[1] - P3[0], P3[2] - P3[0])
                self.facets.append((geo(f['shape']), P3[0], nrm))
        # line network: cells grouped; the gold between groups (inset by half a line)
        if self.lines and self.cells:
            grp = {}
            for m, g, _ in self.cells:
                grp.setdefault(self.groups.get(m, m + str(id(g))), []).append(g)
            half = self.lines['width'] / 2
            self.inset = unary_union([unary_union(gs).buffer(-half, join_style='mitre', mitre_limit=3) for gs in grp.values()])
        else:
            self.inset = None

        if spec.get('ridge_paths'):
            network = unary_union([LineString(points).buffer(self.lines['width'] / 2, cap_style='round', join_style='round') for points in spec['ridge_paths']])
            self.inset = self.outline.difference(network)

    # ---- heights ----
    def shape_z(self, x, y):
        k = self.top['kind']
        if k == 'flat':
            z = np.full(len(x), self.top.get('height', 0.0))
            if self.top.get('dome'):
                d = dist(self.edge, x, y); dm = max(self.inner_r, 1.0)
                z = z + self.top['dome'] * (1 - (1 - np.clip(d / dm, 0, 1)) ** 2)
            return z
        if k == 'roof':
            ds = np.array([np.abs((x - a[0]) * n[0] + (y - a[1]) * n[1]) for n, a in self.NA]).min(0)
            return np.tan(np.radians(self.top['slope_deg'])) * ds * S
        if k == 'planes':
            z = np.zeros(len(x)); done = np.zeros(len(x), bool)
            for g, p0, n in self.facets:
                ins = shapely.contains_xy(g.buffer(0.6), x, y) & ~done
                z[ins] = p0[2] - (n[0] * (x[ins] - p0[0]) + n[1] * (y[ins] - p0[1])) / n[2]; done |= ins
            if (~done).any():                                  # points on no facet: nearest facet
                for i in np.nonzero(~done)[0]:
                    g, p0, n = min(self.facets, key=lambda f: f[0].distance(Point(x[i], y[i])))
                    z[i] = p0[2] - (n[0] * (x[i] - p0[0]) + n[1] * (y[i] - p0[1])) / n[2]
            return z
        if k == 'profile':
            return self.prof(np.clip(dist(self.prof_edge, x, y), 0, float(np.array(self.top['points'])[-1, 0])))
        return np.zeros(len(x))

    def z(self, x, y):
        x = np.asarray(x, float); y = np.asarray(y, float)
        if self.gem:
            ap = np.array(self.gem['apex']); g = np.asarray(self.outline.exterior.coords)[:-1]
            return np.where(np.hypot(x - ap[0], y - ap[1]) < 0.01, self.base + self.gem['rise'], self.base)
        z = self.base + self.shape_z(x, y)
        d = dist(self.edge_b, x, y)
        if self.bev:
            b = self.bev; z = z - b['height'] + bevel_curve(b['width'], b['height'])(d)
        if self.rim:
            r = self.rim; w = r['width']; d0 = self.bev['width'] if self.bev else 0.0
            t = np.clip((d - d0) / w, 0, 1)
            z = z + r['height'] * 0.5 * (1 - np.cos(2 * np.pi * t)) * ((d >= d0) & (t < 1))
        if self.inset is not None:
            dl = dist(self.inset, x, y); half = self.lines['width'] / 2
            inside = shapely.contains_xy(self.inset, x, y)
            t = np.clip(dl / half, 0, 1)
            z = z + np.where(inside, 0.0, self.lines['height'] * (1 - (1 - t) ** 2))
        for m, g, rec in self.cells:
            if rec:
                ins = shapely.contains_xy(g, x, y); dc = dist(g.boundary, x, y)
                z = z - np.where(ins, rec['depth'] * np.clip(dc / rec['width'], 0, 1), 0.0)
        return z

    # ---- rows and materials ----
    def rows(self):
        r = []
        if self.bev:
            r += offsets(self.outline, np.linspace(0, self.bev['width'], 3)[1:])
        if self.rim:
            d0 = self.bev['width'] if self.bev else 0.0
            r += offsets(self.outline, [d0 + self.rim['width'] * f for f in (0.25, 0.5, 0.75, 1.0)])
            if self.rim.get('outer_width'):
                r += offsets(self.outline, [self.rim['outer_width']])
        if self.top['kind'] == 'profile':
            r += [l.intersection(self.outline.buffer(0.5)) for l in offsets(self.prof_shape, [p[0] for p in self.top['points'][1:-1]])]
        if self.top['kind'] == 'flat' and self.top.get('dome'):
            # rings all the way in: long thin triangles across a dome's middle bend the shading into straight streaks
            r += offsets(self.outline, [8, 20, 40, 70] + list(range(100, int(self.inner_r) - 12, 30)))
        for m, g, rec in self.cells:
            r += lines_of(g)
            if rec:
                r += offsets(g, [rec['width'] * f for f in (0.5, 1.0)])
        if self.inset is not None:
            r += lines_of(self.inset) + offsets(self.inset, [1.5, 3.0, 4.5], inward=False)
        if self.top['kind'] == 'planes':
            for g, _, _ in self.facets:
                r += lines_of(g)
        if self.top['kind'] == 'roof':
            big = 5000
            for i, (ni, ai) in enumerate(self.NA):
                reg = self.outline
                for j, (nj, aj) in enumerate(self.NA):
                    if i == j:
                        continue
                    w = ni - nj; c = np.dot(ni, ai) - np.dot(nj, aj)
                    if np.hypot(*w) < 1e-9:
                        continue
                    u = w / np.hypot(*w); p0 = u * c / np.hypot(*w); v = np.array([-u[1], u[0]])
                    reg = reg.intersection(Polygon([p0 + v * big, p0 - v * big, p0 - v * big - u * big, p0 + v * big - u * big]))
                r += lines_of(reg)
        return r

    def classify(self, x, y):
        flat_kinds = ('roof', 'planes')
        m = np.full(len(x), self.spec.get('material', 'Gold'), dtype=object)
        md = np.full(len(x), 'flat' if self.top['kind'] in flat_kinds else 'smooth', dtype=object)
        for mat, g, rec in self.cells:
            ins = shapely.contains_xy(g, x, y)
            if rec:                                          # a sunken fill's slope stays the piece's metal: a colored slope
                ins &= dist(g.boundary, x, y) >= rec['width'] * 0.98   # catches the light as white dashes (cand06)
            if self.inset is not None:
                ins &= shapely.contains_xy(self.inset, x, y)
            if self.rim:
                ins &= dist(self.edge_b, x, y) > self.rim['width'] + (self.bev['width'] if self.bev else 0.0)
            m[ins] = mat
            md[ins] = 'flat' if self.top['kind'] in flat_kinds or not self.top.get('dome') else 'smooth'
        if self.rim:
            near = dist(self.edge_b, x, y) <= self.rim['width'] + (self.bev['width'] if self.bev else 0.0); m[near] = self.rim.get('material', 'Gold'); md[near] = 'smooth'
        if self.inset is not None:
            gold = ~shapely.contains_xy(self.inset, x, y) & (m != self.rim.get('material', 'Gold') if self.rim else True)
            m[gold] = self.lines.get('material', 'Gold'); md[gold] = 'smooth'
        if self.rim and self.rim.get('outer_material'):
            m[dist(self.edge_b, x, y) <= self.rim['outer_width']] = self.rim['outer_material']
        return m, md


pieces = [Piece(p) for p in SPEC['pieces']]
by = {p.name: p for p in pieces}


def sample(region, step=2.5):
    bx0, by0, bx1, by1 = region.bounds
    X, Y = np.meshgrid(np.arange(bx0, bx1 + step, step), np.arange(by0, by1 + step, step)); x, y = X.ravel(), Y.ravel()
    k = shapely.contains_xy(region, x, y); bp = []
    for l in lines_of(region):
        n = max(int(l.length / 1.5), 4); bp += [l.interpolate(t, normalized=True).coords[0] for t in np.linspace(0, 1, n)]
    bp = np.array(bp) if bp else np.zeros((0, 2))
    return np.r_[x[k], bp[:, 0]], np.r_[y[k], bp[:, 1]]


# ---- stack: each base is the highest earlier surface under the piece plus the gap ----
for i, p in enumerate(pieces):
    if p.base is not None:
        continue
    band = p.outline.buffer(2).difference(p.outline.buffer(-p.spec.get('base_band', 10)))
    x, y = sample(band if not band.is_empty else p.outline.buffer(2), step=1.5); need = -1e9
    p.base = 0.0; own = p.z(x, y)                              # this piece's height above its own base at each band point
    for q in pieces[:i]:
        if q.name in p.spec.get('base_ignore', []):
            continue
        ins = shapely.contains_xy(q.outline, x, y)
        if ins.any():
            need = max(need, float((q.z(x[ins], y[ins]) - own[ins]).max()))
    p.base = (need if need > -1e8 else 0.0) + GAP
for p in pieces:                                             # a base set relative to another piece (a gem under its frame)
    if 'base_from' in p.spec:
        p.base = by[p.spec['base_from']['piece']].base + p.spec['base_from']['offset']
for p in pieces:                                             # twins share the higher base
    if 'same_base_as' in p.spec:
        b = max(p.base, by[p.spec['same_base_as']].base); p.base = b; by[p.spec['same_base_as']].base = b
# ---- visible regions: what later pieces do not cover (they are closed solids through the full thickness) ----
for i, p in enumerate(pieces):
    later = [q.outline for q in pieces[i + 1:] if not q.gem]
    if later and not p.gem and not p.spec.get('no_clip'):
        p.vis = unary_union([q for q in polys(p.outline.difference(unary_union(later).buffer(-(8 + i * 3)))) if q.area > 30])

# ---- solids ----
out = {}; meta = []
for p in pieces:
    if p.vis.is_empty:
        continue
    if p.gem:
        g = np.asarray(p.outline.exterior.coords)[:-1]; ap = np.array(p.gem['apex'])
        T = np.array([[ap, g[i], g[(i + 1) % len(g)]] for i in range(len(g))]); mats = np.full(len(T), 'Gem', dtype=object); modes = np.full(len(T), 'flat', dtype=object)
    else:
        T = mesh_faces(p.vis, p.rows())
        c = T.mean(1); mats, modes = p.classify(c[:, 0], c[:, 1])
    key = np.round(T.reshape(-1, 2), 3); uq, inv = np.unique(key, axis=0, return_inverse=True); F = inv.reshape(-1, 3)
    good = (F[:, 0] != F[:, 1]) & (F[:, 1] != F[:, 2]) & (F[:, 0] != F[:, 2]); F, mats, modes = F[good], mats[good], modes[good]
    x, y = uq[:, 0], uq[:, 1]; z = p.z(x, y)
    P3 = np.c_[(x - AX) * S, 2.995 - (y - TOP) * S, z]
    V = P3[F]; n = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0]); flip = n[:, 2] < 0; F[flip] = F[flip][:, ::-1]; V = P3[F]
    n = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0]); fn = n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    Nc = np.repeat(fn[:, None, :], 3, 1); vn = None
    if (modes == 'smooth').any() and not p.gem:
        h = 0.35
        dzx = (p.z(x + h, y) - p.z(x - h, y)) / (2 * h * S); dzy = (p.z(x, y + h) - p.z(x, y - h)) / (2 * h * S)
        vn = np.c_[-dzx, dzy, np.ones_like(dzx)]; vn /= np.linalg.norm(vn, axis=1, keepdims=True)
        sm = modes == 'smooth'; Nc[sm] = vn[F[sm]]
    E = np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]); Em = np.concatenate([mats, mats, mats])
    _, idx, cnt = np.unique(np.sort(E, 1), axis=0, return_index=True, return_counts=True)
    bE = E[idx[cnt == 1]]; bM = Em[idx[cnt == 1]]
    dv = P3[bE[:, 1], :2] - P3[bE[:, 0], :2]; on = np.c_[dv[:, 1], -dv[:, 0]]; on /= np.maximum(np.linalg.norm(on, axis=1, keepdims=True), 1e-12)
    vout = np.zeros((len(P3), 2)); np.add.at(vout, bE[:, 0], on); np.add.at(vout, bE[:, 1], on)
    vout /= np.maximum(np.linalg.norm(vout, axis=1, keepdims=True), 1e-12)
    up = np.array([0, 0, 1.0]); zt = P3[:, 2]; lip = 0.004
    covers = unary_union([q.outline.buffer(-1) for q in pieces[pieces.index(p) + 1:] if not q.gem]) if p is not pieces[-1] else Polygon()
    mids = (P3[bE[:, 0], :2] + P3[bE[:, 1], :2]) / 2
    hidden = shapely.contains_xy(covers, mids[:, 0] / S + AX, TOP + (2.995 - mids[:, 1]) / S) if not covers.is_empty else np.zeros(len(bE), bool)
    levels = [zt, zt - lip, -(zt - lip), -zt] if not p.gem else [zt, zt - lip, np.zeros(len(zt)), -(zt - lip), -zt]
    side = 0.3 * np.c_[vout, np.zeros(len(P3))] + 0.7 * up; side /= np.linalg.norm(side, axis=1, keepdims=True)
    face = vn if vn is not None else np.tile(up, (len(P3), 1))
    WV, WN, WM = [], [], []; nl = len(levels) - 1
    eidx = []
    for k in range(nl):
        za, zb = levels[k], levels[k + 1]
        for ei, ((a, b), mm) in enumerate(zip(bE, bM)):

            A0 = np.r_[P3[a, :2], za[a]]; A1 = np.r_[P3[b, :2], za[b]]; B0 = np.r_[P3[a, :2], zb[a]]; B1 = np.r_[P3[b, :2], zb[b]]
            sa = 1 if (za[a] + za[b]) >= 0 else -1; sb = 1 if (zb[a] + zb[b]) > 0 else -1
            if k == 0:
                na, na1, nb, nb1, mat = face[a], face[b], side[a] * [1, 1, sb], side[b] * [1, 1, sb], mm
            elif k == nl - 1:
                na, na1, nb, nb1, mat = side[a] * [1, 1, sa], side[b] * [1, 1, sa], face[a] * [1, 1, -1], face[b] * [1, 1, -1], mm
            else:
                na, na1, nb, nb1 = side[a] * [1, 1, sa], side[b] * [1, 1, sa], side[a] * [1, 1, sb], side[b] * [1, 1, sb]
                mat = 'Gem' if p.gem else p.spec.get('side', 'Side')
            WV += [np.array([A0, B0, A1]), np.array([A1, B0, B1])]; WN += [np.array([na, nb, na1]), np.array([na1, nb, nb1])]; WM += [mat, mat]; eidx += [ei, ei]
    WV = np.array(WV); WN = np.array(WN)
    if len(WV):
        fw = np.cross(WV[:, 1] - WV[:, 0], WV[:, 2] - WV[:, 0]); dirs = on[np.array(eidx)]
        bad = np.einsum('ij,ij->i', fw[:, :2], dirs) < 0; WV[bad] = WV[bad][:, ::-1]; WN[bad] = WN[bad][:, ::-1]
    Vb = (V * [1, 1, -1])[:, ::-1]; Nb = (Nc * [1, 1, -1])[:, ::-1]
    allV = np.concatenate([V, Vb, WV]); allN = np.concatenate([Nc, Nb, WN]); allM = np.concatenate([mats, mats, np.array(WM, dtype=object)])
    px = allV[..., 0] / S + AX; py = TOP + (2.995 - allV[..., 1]) / S
    UV = np.stack([px / SPEC['units'].get('width_px', 1312.0), 1 - py / SPEC['units'].get('height_px', 1199.0)], -1)
    if p.gem:
        fr = allV.mean(1)[:, 2] >= 0; UV = np.where(fr[:, None, None], np.array([0.0, 0.5]), np.array([0.5, 0.5])) * np.ones_like(UV)
    names = sorted(set(allM))
    out[p.name + '_v'] = allV.astype(np.float32); out[p.name + '_n'] = allN.astype(np.float32); out[p.name + '_uv'] = UV.astype(np.float32)
    out[p.name + '_m'] = np.array([names.index(m) for m in allM], np.int16)
    meta.append(dict(name=p.name, base=p.base, materials=names, triangles=int(len(allV)), front=int(len(V))))
    print(f'{p.name:24s} base {p.base:.4f} front {len(V):6d} total {len(allV):6d} max front z {float(V[..., 2].max()):.3f}')
np.savez_compressed(OUT / 'parts.npz', **out)
json.dump(dict(units=SPEC['units'], box=SPEC.get('box'), parts=meta, order=[m['name'] for m in meta], validate_order=SPEC.get('validate_order', [m['name'] for m in meta])), open(OUT / 'parts.json', 'w'), indent=1)
print('triangles', sum(m['triangles'] for m in meta))
