"""Measure the Golden Storm mockup into design.json (PLAN.md sections 2 and 4). Python 3.11.

Every shape comes from the mockup itself: color classes, smoothed traces (Gaussian blur, contour at 0.5, simplify),
and the bolt's edges fitted to the outer edge of its gold outline. Lengths in mockup pixels.
"""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.ndimage import gaussian_filter
import contourpy
from shapely.geometry import Polygon, MultiPolygon, LineString, Point
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
mock = np.asarray(Image.open(HERE.parent / 'reference/mockup.png').convert('RGB')).astype(float) / 255
H, W = mock.shape[:2]
r, g, b = mock.transpose(2, 0, 1); mx, mn = mock.max(2), mock.min(2); sat = (mx - mn) / np.maximum(mx, 1e-6)
d = np.maximum(mx - mn, 1e-6)
hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
field = (mx < 0.62) & (hue >= 215) & (hue <= 290) & (sat > 0.35)
ribbon = (hue >= 195) & (hue < 219) & (sat > 0.15) & (sat < 0.63) & (mx > 0.6)   # ribbon blue: sat 0.42 to 0.57; the field's painted highlights are 0.67 to 0.71
yellow = (hue >= 44) & (hue < 62) & (sat > 0.55) & (mx > 0.85)
gold = (hue >= 20) & (hue < 62) & (sat > 0.3) & ~yellow
white = (sat < 0.2) & (mx > 0.72)
dropped = []


def trace(mask, sigma=2.0, min_area=0.0, label=''):
    """Smooth outline of a mask: blur, contour at half, simplify; even-odd nesting gives holes."""
    f = gaussian_filter(mask.astype(float), sigma)
    G = Polygon()
    for q in sorted([Polygon(l + 0.5) for l in contourpy.contour_generator(z=f, line_type='Separate').lines(0.5) if len(l) > 3], key=lambda q: -q.area):
        G = G.symmetric_difference(q.buffer(0))
    G = G.simplify(0.6)
    keep = []
    for q in (G.geoms if isinstance(G, MultiPolygon) else [G]):
        if q.is_empty:
            continue
        (keep if q.area >= min_area else dropped).append(q if q.area >= min_area else (label, round(q.area), tuple(np.round(q.centroid.coords[0]))))
    return unary_union(keep) if keep else Polygon()


def ser(geom):
    gs = geom.geoms if isinstance(geom, MultiPolygon) else [geom]
    return [dict(exterior=[[round(x, 2), round(y, 2)] for x, y in q.exterior.coords], holes=[[[round(x, 2), round(y, 2)] for x, y in h.coords] for h in q.interiors]) for q in gs if not q.is_empty and q.area > 1]


def biggest(geom):
    return max(geom.geoms, key=lambda q: q.area) if isinstance(geom, MultiPolygon) else geom


# silhouette: the badge's own colors closed and filled (the drop shadow is pale grey, never gold, so it stays out)
highlight = (mx > 0.95) & (r - b > 0.06)                     # warm white highlights on the gold (the background is neutral)
solid = ndi.binary_fill_holes(ndi.binary_closing(field | ribbon | yellow | gold | highlight, iterations=4))
solid = ndi.binary_opening(solid, iterations=2)
lab, n = ndi.label(solid); solid = lab == (1 + np.argmax(ndi.sum(solid, lab, range(1, n + 1))))
sil = biggest(trace(solid, 1.2))
ys, xs = np.nonzero(solid); top, bot = int(ys.min()), int(ys.max()); cx = (xs.min() + xs.max()) / 2
S = 5.45 / (bot - top)

# bolt: approximate corners read from the mockup on a grid, then each edge fitted to the outer edge of the gold outline
approx = dict(TL=(640, 225), L=(360, 630), P2=(600, 575), B=(440, 965), R=(935, 452), P1=(595, 508), TR=(735, 250))
order = ['TL', 'L', 'P2', 'B', 'R', 'P1', 'TR']
poly0 = Polygon([approx[k] for k in order])
outside_ok = field | ribbon | white


def fit_edge(a, b, direction=None):
    a, b = np.array(a, float), np.array(b, float); t = (b - a) / np.linalg.norm(b - a); nrm = np.array([-t[1], t[0]])
    mid = (a + b) / 2
    if poly0.contains(Point(*(mid + nrm * 5))):
        nrm = -nrm                                             # normal points out of the bolt
    pts = []
    for f in np.linspace(0.15, 0.85, 40):
        p = a + (b - a) * f
        prev_gold = False
        for s_ in np.arange(-25, 40, 0.5):
            x, y = (p + nrm * s_).round().astype(int)
            if not (0 <= x < W and 0 <= y < H):
                break
            if gold[y, x] or yellow[y, x]:
                prev_gold = True
            elif prev_gold and outside_ok[y, x]:
                # the outer edge of the gold: next pixels must stay outside (not another gold outline)
                ahead = [(p + nrm * (s_ + k)).round().astype(int) for k in (2, 4, 6)]
                if all(0 <= q[0] < W and 0 <= q[1] < H and not gold[q[1], q[0]] for q in ahead):
                    pts.append(p + nrm * (s_ - 0.5)); break
                prev_gold = False
    if len(pts) < 4:
        return None, 0
    P = np.array(pts)
    if direction is not None:                                  # only the offset is fitted (a parallel edge)
        dirv = np.asarray(direction, float) / np.linalg.norm(direction); nn = np.array([-dirv[1], dirv[0]])
        off = np.median(P @ nn); return (P.mean(0) - nn * ((P.mean(0) @ nn) - off), dirv), len(pts)
    c = P.mean(0); u, sv, vt = np.linalg.svd(P - c); dirv = vt[0]
    res = np.abs((P - c) @ np.array([-dirv[1], dirv[0]]))
    keep = res < max(np.median(res) * 3, 1.0)                  # drop outliers (a neighbor's gold) and refit
    c = P[keep].mean(0); u, sv, vt = np.linalg.svd(P[keep] - c); dirv = vt[0]
    return (c, dirv), int(keep.sum())


def meet(l1, l2):
    (p, u), (q, v) = l1, l2
    A = np.array([u, -v]).T; s_, _ = np.linalg.solve(A, q - p); return p + u * s_


lines = {}
for i in range(len(order)):
    k0, k1 = order[i], order[(i + 1) % len(order)]
    if (k0, k1) == ('TR', 'TL'):
        continue                                                # the top end is under the upper cloud
    if (k0, k1) == ('P1', 'TR'):
        continue
    lines[(k0, k1)], nfit = fit_edge(approx[k0], approx[k1])
    print(f'bolt edge {k0}-{k1}: {nfit} samples')
# the upper segment's right edge is mostly under the upper cloud's spiral: it runs parallel to the segment's left edge,
# so only its offset is fitted, along the stretch that borders the field just above the inner corner
dl = lines[('TL', 'L')][1]; dl = dl if dl[1] < 0 else -dl
p1 = np.array(approx['P1'], float)
lines[('P1', 'TR')], nfit = fit_edge(p1 + dl * 10, p1 + dl * 150, direction=dl)
print(f'bolt edge P1-TR (parallel): {nfit} samples')
verts = {}
for k in ['L', 'P2', 'B', 'R', 'P1']:
    i = order.index(k); prev = (order[i - 1], k); nxt = (k, order[(i + 1) % len(order)])
    verts[k] = meet(lines[prev], lines[nxt]) if lines.get(prev) and lines.get(nxt) else np.array(approx[k], float)
# the top end: the left and right edges extended up to row 225, under the upper cloud
for k, edge in (('TL', ('TL', 'L')), ('TR', ('P1', 'TR'))):
    c, u = lines[edge]; s_ = (225 - c[1]) / u[1]; verts[k] = c + u * s_
bolt_full = Polygon([tuple(verts[k]) for k in order])
bolt = bolt_full
# its gold outline width: from the outer edge inward to the first yellow
widths = []
for k0, k1 in [('L', 'P2'), ('B', 'R'), ('R', 'P1'), ('TL', 'L')]:
    a, b2 = verts[k0], verts[k1]; t = (b2 - a) / np.linalg.norm(b2 - a); nrm = np.array([-t[1], t[0]])
    if not bolt.contains(Point(*((a + b2) / 2 + nrm * 5))):
        nrm = -nrm
    for f in np.linspace(0.3, 0.7, 9):
        p = a + (b2 - a) * f
        for s_ in range(2, 45):
            x, y = (p + nrm * s_).round().astype(int)
            if yellow[y, x]:
                widths.append(s_); break
bolt_w = float(np.median(widths)) if widths else 18.0

# field cell: field and ribbons with their thin gold edges closed in, holes filled
# the field is everything inside the frame's gold band: gold touching the outer edge and within 70 px of it is frame
dist_out = ndi.distance_transform_edt(solid)
fg = (gold | highlight | yellow) & (dist_out < 70)
lab_f, nf = ndi.label(fg, structure=np.ones((3, 3)))
touch = np.unique(lab_f[(dist_out < 3) & fg]); touch = touch[touch > 0]
frame_gold = np.isin(lab_f, touch)
interior = solid & ~ndi.binary_dilation(frame_gold, iterations=1)
interior = ndi.binary_opening(interior, iterations=3)
lab_i, ni = ndi.label(interior); sz = ndi.sum(interior, lab_i, range(1, ni + 1))
interior = ndi.binary_fill_holes(np.isin(lab_i, 1 + np.nonzero(sz > 300)[0]))   # small parts too (the crown point's navy triangle)
field_cell = trace(interior, 2.0, 300, 'field part')           # the bolt splits the field: keep every part
# ribbons: light blue fills, each joined to its gold edge line inside the field
import sys as _sys
_sys.path.insert(0, str(HERE.parent.parent / 'skills/badge-build/scripts'))
from linework import regularize
from PIL import ImageDraw as _ID


def raster(geom):
    im = Image.new('L', (W, H), 0); dr_ = _ID.Draw(im)
    for q in (geom.geoms if isinstance(geom, MultiPolygon) else [geom]):
        if q.is_empty:
            continue
        dr_.polygon(list(q.exterior.coords), fill=255)
        for h in q.interiors:
            dr_.polygon(list(h.coords), fill=0)
    return np.asarray(im) > 127


# gold with its highlights: warm and greener than blue (the pink pearl and the blue field stay out)
gold_ext = gold | ((mx > 0.8) & ((r - b) > 0.08) & ((g - b) > 0.05))
rib = trace(ribbon & interior, 2.0, 800, 'ribbon')
rib_polys = [q for q in (rib.geoms if isinstance(rib, MultiPolygon) else [rib]) if not q.is_empty]
gold_in_field = trace(gold & ndi.binary_erosion(interior, iterations=4), 1.2, 60, 'field gold')
ribbons = []
for q in rib_polys:
    # the ribbon's gold wires as clean strokes (round 2: traced 6 to 8 px lines were lost under grown fills); the bolt's
    # or a cloud's gold near its end is kept so the end lands under them
    zone = raster(q.buffer(18)) & ndi.binary_erosion(interior, iterations=3)
    Gq = ndi.binary_closing(ndi.binary_opening(gold_ext & zone, iterations=1), iterations=2) & zone
    labq, nq = ndi.label(Gq); szq = ndi.sum(Gq, labq, range(1, nq + 1)); Gq = np.isin(labq, 1 + np.nonzero(szq >= 60)[0])
    wires = trace(regularize(Gq, smooth_px=10, min_radius=3.5, prune_px=8), 1.0, 40, 'ribbon wire') if Gq.any() else Polygon()
    piece = unary_union([q, wires]).buffer(1.5).buffer(-1.5).intersection(field_cell.buffer(-4))
    piece = biggest(piece) if not piece.is_empty else piece
    ribbons.append(dict(outline=ser(piece), fill=ser(q.intersection(piece)), gold=ser(wires.intersection(piece)) if not wires.is_empty else []))
# the slim gold crescent needle at the upper left: one clean stroke from the frame's inner edge to its tip
box_n = Polygon([(440, 232), (525, 232), (525, 345), (440, 345)])
Gn = gold_ext & raster(box_n) & ~ndi.binary_dilation(frame_gold, iterations=2) if 'frame_gold' in globals() else None
# clouds: pearl fills per cloud (white inside the badge, away from the bolt), grown by the gold outline
wcl = white & ndi.binary_erosion(solid, iterations=6)
wtr = trace(wcl, 2.0, 60, 'white')
allw = [q for q in (wtr.geoms if isinstance(wtr, MultiPolygon) else [wtr]) if not q.is_empty and not bolt.contains(q.representative_point())]
big = [q for q in allw if q.area >= 3000]
up_big = [q for q in big if q.centroid.y < 600 and q.centroid.x > 560]; lo_big = [q for q in big if q.centroid.y >= 600 and q.centroid.y < 1000]
def with_centers(main):
    hull = unary_union(main).convex_hull.buffer(-10)
    small = [q for q in allw if q.area < 3000 and hull.contains(q.representative_point())]
    return unary_union(main + small), len(small)
upper, nu = with_centers(up_big); lower, nl = with_centers(lo_big)
print('cloud small white bits kept (spiral centers): upper', nu, 'lower', nl)
# the bolt's top runs under the upper cloud: above the cloud's lower edge it keeps only what the cloud covers
up_plate0 = upper.buffer(16).buffer(6).buffer(-6)
# the bolt's left gold edge curves right near the top and merges into the upper cloud's outline (mockup, rows 200 to
# 300): above row 310 the bolt keeps only what lies on the mockup's gold, yellow or cloud, never on the field
not_field = trace(solid & ~field & ~ribbon, 2.0)
top_zone = Polygon([(0, 0), (W, 0), (W, 310), (0, 310)])
bolt = unary_union([bolt_full.difference(top_zone), bolt_full.intersection(top_zone).intersection(not_field.buffer(-1))])
bolt = biggest(bolt.buffer(0.5).buffer(-0.5))
# a white highlight on the bottom star point touches the lower cloud's white: cut every star point's triangle out
bnd0 = np.asarray(sil.exterior.coords)[:-1]
def tip_triangle(tx, ty, run):
    i = int(np.argmin(np.hypot(bnd0[:, 0] - tx, bnd0[:, 1] - ty)))
    def walk(step):
        j, acc = i, 0.0
        while acc < run:
            j2 = (j + step) % len(bnd0); acc += np.hypot(*(bnd0[j2] - bnd0[j])); j = j2
        return bnd0[j]
    return Polygon([tuple(bnd0[i]), tuple(walk(1)), tuple(walk(-1))])
_lx = float(np.asarray(sil.exterior.coords)[:, 0].min()); _rx = float(np.asarray(sil.exterior.coords)[:, 0].max())
_ly = float(np.asarray(sil.exterior.coords)[np.argmin(np.asarray(sil.exterior.coords)[:, 0]), 1]); _ry = float(np.asarray(sil.exterior.coords)[np.argmax(np.asarray(sil.exterior.coords)[:, 0]), 1])
tri_cut = unary_union([tip_triangle(cx, bot, 150), tip_triangle(cx, top, 150), tip_triangle(_lx, _ly, 130), tip_triangle(_rx, _ry, 130)]).buffer(3)
lower = lower.difference(tri_cut); upper = upper.difference(tri_cut)
lower = unary_union([q for q in (lower.geoms if isinstance(lower, MultiPolygon) else [lower]) if q.area > 60])
# clean line work: each cloud's gold (outline ring, spirals, hooks) thinned to its centerline and redrawn as even strokes
# (traced edges wobbled with the pearl's shading: lumpy spirals twice the mockup's width, cand plan check)
import sys as _sys
_sys.path.insert(0, str(HERE.parent.parent / 'skills/badge-build/scripts'))
from linework import regularize
from PIL import ImageDraw as _ID


def raster(g, pad=0):
    im = Image.new('L', (W, H), 0); dr_ = _ID.Draw(im)
    for q in (g.geoms if isinstance(g, MultiPolygon) else [g]):
        if q.is_empty:
            continue
        dr_.polygon(list(q.exterior.coords), fill=255)
        for h in q.interiors:
            dr_.polygon(list(h.coords), fill=0)
    return np.asarray(im) > 127


warm_hi = (mx > 0.95) & (r - b > 0.08)
# gold with its highlights: warm and greener than blue (the pearl is pink, green about equal to blue)
gold_ext = gold | ((mx > 0.8) & ((r - b) > 0.08) & ((g - b) > 0.05))   # warm tinted pearl (green - blue about 0.04) stays out
clean_gold = {}
for name, f in (('upper', upper), ('lower', lower)):
    zone = raster(f.buffer(22))
    # the bolt's rim and its warm reflection, and the frame band, are not this cloud's line work (round 2: a jagged
    # strand beside the bolt over the lower cloud)
    # the bolt where it shows (below row 310; above it runs under the upper cloud, whose spiral lies there), the frame and
    # the star points
    others = raster(bolt_full.intersection(Polygon([(0, 310), (W, 310), (W, H), (0, H)])).buffer(10)) | ndi.binary_dilation(frame_gold, iterations=2) | raster(tri_cut.buffer(2))
    G = ndi.binary_closing(ndi.binary_opening(gold_ext & zone & ~others, iterations=1), iterations=2) & zone & ~others
    labG, nG = ndi.label(G); szG = ndi.sum(G, labG, range(1, nG + 1)); G = np.isin(labG, 1 + np.nonzero(szG >= 80)[0])   # specks out
    Gr = regularize(G, smooth_px=10, min_radius=3.5, prune_px=8)
    cg = trace(Gr, 1.0, 40, f'{name} clean gold')
    cg = unary_union([Polygon(q.exterior, [h for h in q.interiors if Polygon(h).area >= 60]) for q in (cg.geoms if isinstance(cg, MultiPolygon) else [cg])])
    clean_gold[name] = cg                                          # specks of holes inside strokes filled
    pm = ndi.binary_closing((Gr | (white & zone)) & zone, iterations=3)
    holes = ndi.binary_fill_holes(pm) & ~pm; lh, nh = ndi.label(holes); szh = ndi.sum(holes, lh, range(1, nh + 1))
    plate_mask = pm | np.isin(lh, 1 + np.nonzero(szh < 300)[0])   # only specks filled: the spiral's navy pocket stays open
    plate_poly = biggest(trace(plate_mask, 1.2)); clean_plate = globals().setdefault('clean_plate', {}); clean_plate[name] = plate_poly
    newf = keep_fills = plate_poly.difference(clean_gold[name].buffer(0.3))
    newf = unary_union([q for q in (newf.geoms if isinstance(newf, MultiPolygon) else [newf]) if q.area > 60])
    if name == 'upper':
        upper = newf
    else:
        lower = newf
clouds = {}
for name, f in (('upper', upper), ('lower', lower)):
    plate = clean_plate[name].intersection(sil)                 # the clean strokes' outer edge, snapped to the outline later
    plate = unary_union([Polygon(q.exterior) for q in (plate.geoms if isinstance(plate, MultiPolygon) else [plate]) if q.area > 400])
    clouds[name] = dict(plate=ser(plate), fills=ser(f), gold=ser(clean_gold[name]))
# star points: tips and the silhouette's flanks a fixed run from each tip
bnd = np.asarray(sil.exterior.coords)[:-1]
tips = dict(top=(cx, top), bottom=(cx, bot), left=(xs.min(), None), right=(xs.max(), None))
for k in ('left', 'right'):
    col = int(tips[k][0]); rows = np.nonzero(solid[:, col if k == 'left' else col])[0]; tips[k] = (tips[k][0], float(rows.mean()))
points = {}
for k, (tx, ty) in tips.items():
    i = int(np.argmin(np.hypot(bnd[:, 0] - tx, bnd[:, 1] - ty))); T = bnd[i]
    run = 150 if k in ('top', 'bottom') else 130
    def walk(step):
        j, acc = i, 0.0
        while acc < run:
            j2 = (j + step) % len(bnd); acc += np.hypot(*(bnd[j2] - bnd[j])); j = j2
        return bnd[j]
    points[k] = dict(tip=T.round(2).tolist(), a=walk(1).round(2).tolist(), b=walk(-1).round(2).tolist())
# the needle: its gold (with highlights) in its box, not the frame's, redrawn as one clean stroke, then run 8 px into the
# frame's inner slope so it grows from the frame (round 2: a floating hairline)
nm = regularize(ndi.binary_closing(Gn, iterations=2), smooth_px=8, min_radius=3.5, prune_px=6) if Gn is not None and Gn.any() else None
needle = biggest(trace(nm, 1.0, 40, 'needle')) if nm is not None and nm.any() else Polygon()
if not needle.is_empty:
    needle = unary_union([needle, needle.buffer(8).intersection(field_cell.buffer(8).difference(field_cell))]).buffer(0.5).buffer(-0.5)
field_lines = [needle] if not needle.is_empty else []
print('needle', round(needle.area), 'px2', needle.bounds if not needle.is_empty else None)
tips = dict(lower=[[942, 972]], upper=[[783, 445], [917, 598]])
print('field gold lines', [(round(q.area), tuple(np.round(q.centroid.coords[0]))) for q in field_lines])
# cloud tips read from the mockup on a 10 px grid (tail and hooks taper to points the traced fills round off)
tips = dict(lower=[[942, 972]], upper=[[783, 445], [917, 598]])
# units from the traced silhouette itself, so the model's bounds land exactly on Y 2.995 and minus 2.455
top, bot = float(sil.bounds[1]), float(sil.bounds[3]); S = 5.45 / (bot - top); cx = (sil.bounds[0] + sil.bounds[2]) / 2
design = dict(units=dict(S=S, axis=cx, top=float(top), width_px=W, height_px=H, bottom=float(bot)),
              silhouette=ser(sil), field_cell=ser(field_cell), ribbons=ribbons, clouds=clouds,
              bolt=dict(outline=ser(bolt), vertices={k: np.round(v, 2).tolist() for k, v in verts.items()}, gold_width=bolt_w),
              points=points, field_lines=[ser(q) for q in field_lines], tips=tips, dropped=[list(x) for x in dropped])
json.dump(design, open(HERE / 'design.json', 'w'))
print('units', design['units'])
print('bolt vertices', design['bolt']['vertices'], 'gold width', bolt_w)
print('ribbons', len(ribbons), 'cloud fills upper', round(upper.area), 'lower', round(lower.area))
print('points', {k: v['tip'] for k, v in points.items()})
print('dropped', dropped)
