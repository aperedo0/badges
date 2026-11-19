"""Turn the traced areas (design_traced.json) into the design (design.json) by the plan's rules.

Every shape is a polygon in mockup pixels. Cells are grown to the gold line centerlines. Symmetric parts are
measured on the left and mirrored about x 653.5. Decisions taken at checkpoint 1 are written as rules below.
"""
import json
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, Point, box, LineString
from shapely.ops import unary_union
from shapely.affinity import scale as sscale

HERE = Path(__file__).resolve().parent
T = json.load(open(HERE / 'design_traced.json'))
AX = 653.5; LW = 11.5
RING_C = np.array([AX, 557.9]); RING_R = 473.7; RING_IN = RING_R - 28.6
SUN_C = np.array([AX, 566.2]); SUN_R = 195.0; SUN_RIM = 218.0
LEFT = box(-10, -10, AX, 1300)
silhouette = None


def mirror(g):
    return sscale(g, xfact=-1, yfact=1, origin=(AX, 0))


def sym(g):
    l = g.intersection(LEFT); return unary_union([l, mirror(l)]).buffer(0)


def poly(a):
    p = Polygon(a['poly'], a.get('holes', [])).buffer(0)
    return p


def thick(p):
    """Radius of the largest circle inside (by shrinking)."""
    r = 0.0
    for d in np.arange(0.5, 60, 0.5):
        if p.buffer(-d).is_empty:
            return d
    return 60


def grow(p):
    return p.buffer(LW / 2, join_style='mitre', mitre_limit=3.0)


def chaikin(p, n=3):
    """Round a polygon's corners by corner cutting (keeps the overall shape, removes bumps)."""
    def ring(c):
        c = np.asarray(c)[:-1]
        for _ in range(n):
            a = c; b = np.roll(c, -1, 0); c = np.vstack([np.c_[0.75 * a + 0.25 * b], np.c_[0.25 * a + 0.75 * b]]).reshape(2, -1, 2).transpose(1, 0, 2).reshape(-1, 2)
        return np.vstack([c, c[:1]])
    return Polygon(ring(p.exterior.coords), [ring(h.coords) for h in p.interiors]).buffer(0)


def biggest(g):
    return max(g.geoms, key=lambda q: q.area) if isinstance(g, MultiPolygon) else g


def rd(p):
    return float(np.hypot(*(np.array(p.representative_point().coords[0]) - RING_C)))


def sd(p):
    return float(np.hypot(*(np.array(p.representative_point().coords[0]) - SUN_C)))


areas = [(a, poly(a)) for a in T['areas']]
# silhouette from the mask outline (traced once more here as one polygon)
from PIL import Image
from scipy import ndimage as ndi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
mask = np.load(HERE.parent / 'trace/mask.npy')
cs = plt.contour(ndi.gaussian_filter(mask.astype(float), 1.2), levels=[0.5]); seg = max(cs.allsegs[0], key=len); plt.close('all')
silhouette = sym(Polygon(seg).buffer(0).simplify(1.5))

# ---------- plate cells: red wedges, yellow rays and flanks, the top spike's lemon, small red triangles ----------
plate = []
for a, p in areas:
    c = a['color']; pt = np.array(p.representative_point().coords[0])
    if c in ('red', 'dark') and rd(p) < RING_IN and sd(p) > SUN_RIM and p.area > 500 and pt[1] < 700:
        plate.append(('red', p))
    elif c == 'yellow' and rd(p) < RING_IN - 2 and sd(p) > SUN_RIM - 2 and pt[1] < 600 and p.area > 600 and thick(p) >= 4.0:
        plate.append(('lemon', p))
# merge touching pieces of one color (a red triangle split into light and dark parts)
merged = []
for col in ('red', 'lemon'):
    u = unary_union([p.buffer(1.5) for c, p in plate if c == col]).buffer(-1.5)
    for q in (u.geoms if isinstance(u, MultiPolygon) else [u]):
        if q.area > (1200 if col == 'lemon' else 500) and not (col == 'lemon' and rd(q) > RING_IN - 30 and thick(q) < 7):
            merged.append((col, q))
# symmetric: keep cells whose center is left of the axis, mirror them; the top spike's lemon spans the axis
cells_plate = []
for col, q in merged:
    x = q.representative_point().x
    if q.intersects(LineString([(AX, 0), (AX, 1300)])) and q.bounds[0] < AX - 5 and q.bounds[2] > AX + 5:
        cells_plate.append((col, sym(q)))
    elif x < AX:
        cells_plate.append((col, q)); cells_plate.append((col, mirror(q)))
cells_plate = [(c, grow(q.simplify(2.5)).intersection(Point(*RING_C).buffer(RING_IN, 256)).difference(Point(*SUN_C).buffer(SUN_RIM - 4, 256))) for c, q in cells_plate]
def keep_big(g, a=1000):
    gs = g.geoms if isinstance(g, MultiPolygon) else [g]
    return unary_union([q for q in gs if q.area >= a])
cells_plate = [(c, keep_big(q)) for c, q in cells_plate]
cells_plate = [(c, q) for c, q in cells_plate if not q.is_empty]
print('plate cells', len(cells_plate), {c: sum(1 for cc, _ in cells_plate if cc == c) for c in ('red', 'lemon')})

# ---------- mountains ----------
def pick(color, region):
    return [p for a, p in areas if a['color'] == color and region.contains(p.representative_point()) and p.area > 800]

side_region = box(100, 560, AX - 120, 820)
side_snow = biggest(unary_union(pick('white', box(150, 560, 440, 720))))
side_body = biggest(unary_union([p for c in ('blue', 'navy', 'teal', 'steel') for p in pick(c, box(100, 600, 390, 800))]))
side_out = unary_union([side_snow, side_body]).buffer(14, join_style='mitre', mitre_limit=3).simplify(2.5)
peak_side = max(side_snow.exterior.coords, key=lambda p: -p[1])
cen_region = box(300, 470, 1010, 930)
cen_snow = biggest(unary_union([p for p in pick('white', box(400, 480, 900, 760)) if p.area > 20000]))
cen_teal = biggest(unary_union([p for a, p in areas if a['id'] == 40]))
cen_chev_v = [(662, 815), (762, 722), (930, 840)]                      # measured V: left arm end, apex, right arm end
cen_chev = Polygon(cen_chev_v + [(930, 1000), (662, 1000)])
cen_blue_all = unary_union([p for c in ('blue', 'navy', 'teal', 'steel') for p in pick(c, cen_region)] + [cen_teal, cen_chev]).buffer(3).buffer(-3)
cen_out = sym(unary_union([cen_snow, cen_blue_all]).buffer(14, join_style='mitre', mitre_limit=3)).simplify(2.5)
cen_chev = cen_chev.intersection(cen_out.buffer(-14))
interior = cen_out.buffer(-14 - LW / 2)
rest = interior.difference(grow(cen_snow)).difference(cen_teal).difference(grow(cen_chev))
def nohole(g):
    gs = g.geoms if isinstance(g, MultiPolygon) else [g]
    return unary_union([Polygon(q.exterior) for q in gs if q.area > 400])
rest = nohole(rest).difference(grow(cen_snow)).difference(cen_teal).difference(grow(cen_chev))
navy_band = nohole(rest.intersection(box(0, 0, AX, 2000))); steel = nohole(rest.intersection(box(AX, 0, 2000, 2000)))
mountains = dict(
    side_left=dict(outline=side_out, peak=peak_side, cells=[('snow_white', grow(side_snow.simplify(2.5)).intersection(side_out.buffer(-14))),
                                                             ('royal', side_body.simplify(2.5).buffer(LW / 2, join_style='mitre').intersection(side_out.buffer(-14)))],
                    gold_lines='snowline'),
    central=dict(outline=cen_out, peak=(AX, cen_out.bounds[1]), cells=[('snow_white', nohole(grow(cen_snow.simplify(2.5)))), ('teal', nohole(cen_teal.simplify(2.5)).difference(grow(cen_chev))),
                                                                   ('navy', navy_band), ('steel', steel), ('navy_chevron', cen_chev.buffer(-LW / 2, join_style='mitre').buffer(LW / 2, join_style='mitre'))],
                 gold_lines='snowline and chevron; the blue faces meet at creases'))
mountains['side_right'] = dict(outline=mirror(side_out), peak=(2 * AX - peak_side[0], peak_side[1]),
                               cells=[(n, mirror(p)) for n, p in mountains['side_left']['cells']], gold_lines='snowline')

# ---------- spikes: wide gold inside the plate plus the points beyond the ring ----------
disc = Point(*RING_C).buffer(RING_R, 256)
gold_net = disc.difference(unary_union([q for _, q in cells_plate])).difference(Point(*SUN_C).buffer(SUN_RIM, 256))
sunburst = box(0, 0, 1312, 612).difference(unary_union([m['outline'] for m in mountains.values()]).buffer(4))
wide = gold_net.intersection(sunburst).buffer(-7).buffer(7).difference(disc.difference(Point(*RING_C).buffer(RING_IN + 2, 256)))
beyond = silhouette.difference(disc).intersection(box(0, 0, 1312, 640))
spikes = []
for q in list(wide.geoms if isinstance(wide, MultiPolygon) else [wide]) + list(beyond.geoms if isinstance(beyond, MultiPolygon) else [beyond]):
    if q.area > 300 and q.representative_point().x <= AX + 1:
        spikes.append(q)
# join each inner blade with its outer point across the ring
groups = []
for q in spikes:
    c = np.array(q.representative_point().coords[0]); ang = np.degrees(np.arctan2(-(c[1] - RING_C[1]), c[0] - RING_C[0]))
    for g in groups:
        if abs(g['ang'] - ang) < 9:
            g['parts'].append(q); break
    else:
        groups.append(dict(ang=ang, parts=[q]))
spike_polys = []
for g in groups:
    u = unary_union(g['parts']).convex_hull if len(g['parts']) > 1 else g['parts'][0]
    # run the point down through the ring to the inner ring circle along its own edges
    hull = u.convex_hull; tip = max(hull.exterior.coords, key=lambda p: np.hypot(p[0] - RING_C[0], p[1] - RING_C[1]))
    near = sorted(hull.exterior.coords, key=lambda p: np.hypot(p[0] - RING_C[0], p[1] - RING_C[1]))[:2]
    ext = [np.array(tip) + (np.array(c) - tip) * (np.hypot(*(np.array(tip) - RING_C)) - RING_IN + 14) / max(np.hypot(*(np.array(c) - tip)), 1e-6) for c in near]
    u = unary_union([u, Polygon([tip, tuple(ext[0]), tuple(ext[1])]).convex_hull]).convex_hull
    u = u.intersection(silhouette).simplify(1.0)
    if abs(g['ang'] - 90) < 6:
        spike_polys.append(('spike_top', sym(u)))
    else:
        spike_polys.append((f"spike_{int(round(g['ang']))}", u)); spike_polys.append((f"spike_{int(round(g['ang']))}_mirror", mirror(u)))
print('spikes', [(n, round(p.area)) for n, p in spike_polys])

# ---------- clouds and the lower gold ----------
cloud_left = biggest(unary_union([p for p in pick('white', box(40, 690, AX - 20, 1100)) if p.area > 1500]))
cloud_left = chaikin(biggest(cloud_left.buffer(6, quad_segs=12).buffer(-12, quad_segs=12).buffer(6, quad_segs=12)).simplify(4.0))
cloud_cells = [grow(cloud_left.simplify(2.5)), mirror(grow(cloud_left.simplify(2.5)))]
# the white strips beside the frame's lower arm
strip = unary_union([p for p in pick('white', box(470, 900, AX, 1110)) if p.area > 800])
if not strip.is_empty:
    st = chaikin(biggest(biggest(strip).buffer(6, quad_segs=12).buffer(-12, quad_segs=12).buffer(6, quad_segs=12)).simplify(4.0))
    cloud_cells += [grow(st), mirror(grow(st))]

# ---------- gem and frame ----------
gem_pts = [(653.5, 853.0), (601, 940), (548, 958), (601, 976), (653.5, 1079), (706, 976), (759, 958), (706, 940)]
gem = Polygon(gem_pts)
frame = sscale(gem, xfact=343 / 211, yfact=337 / 226, origin=(653.5, 958))

# the lower gold: the border band along the lower outline, the clouds' outlines and their curls (closing fills the curl gaps)
cu = unary_union(cloud_cells)
border_band = silhouette.difference(silhouette.buffer(-40)).intersection(box(0, 700, 1312, 1300))
cloud_gold = cu.buffer(30, quad_segs=12).buffer(-14, quad_segs=12).difference(cu)
lower_gold = unary_union([border_band, cloud_gold]).intersection(silhouette).buffer(0)
# fill gaps inside the gold (a curl's middle) that are not cloud cells
lg = []
for q in (lower_gold.geoms if isinstance(lower_gold, MultiPolygon) else [lower_gold]):
    lg.append(Polygon(q.exterior, [h for h in q.interiors if Polygon(h).area > 20000 or Polygon(h).intersects(cu.buffer(-3))]))
lower_gold = unary_union(lg).difference(cu).difference(frame).buffer(0)


def ser(g):
    gs = g.geoms if isinstance(g, MultiPolygon) else [g]
    return [dict(exterior=[[round(x, 2), round(y, 2)] for x, y in q.exterior.coords], holes=[[[round(x, 2), round(y, 2)] for x, y in h.coords] for h in q.interiors]) for q in gs if not q.is_empty]


design = dict(units=T['units'], line_width=LW, axis=AX, silhouette=ser(silhouette),
              ring=dict(center=RING_C.tolist(), r_outer=RING_R, r_inner=RING_IN), sun=dict(center=SUN_C.tolist(), r_enamel=SUN_R, r_rim=SUN_RIM),
              plate_cells=[dict(color=c, shape=ser(q)) for c, q in cells_plate],
              spikes=[dict(name=n, shape=ser(p)) for n, p in spike_polys],
              mountains={k: dict(outline=ser(v['outline']), peak=list(v['peak']), gold_lines=v['gold_lines'], cells=[dict(color=c, shape=ser(q)) for c, q in v['cells']]) for k, v in mountains.items()},
              cloud_cells=[ser(q) for q in cloud_cells], lower_gold=ser(lower_gold),
              frame=ser(frame), gem=dict(outline=[list(p) for p in gem_pts], tips=[gem_pts[0], gem_pts[2], gem_pts[4], gem_pts[6]], apex=[653.5, 958.0]))
json.dump(design, open(HERE / 'design.json', 'w'), indent=0)
print('mountain peaks', {k: v['peak'] for k, v in mountains.items()}, 'cloud cells', len(cloud_cells))
