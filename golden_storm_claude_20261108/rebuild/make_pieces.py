"""Turn the measured shapes (design.json) into the stacked pieces file (pieces.json) for badge3d.py.

Plan: rebuild/PLAN.md sections 2 and 4. Lengths in mockup pixels, heights in units. Back to front: core, base (frame
and field), star points, ribbons, field lines, lower cloud, bolt, upper cloud.
"""
import json
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, LineString, Point
from shapely.ops import unary_union, nearest_points

HERE = Path(__file__).resolve().parent
D = json.load(open(HERE / 'design.json'))
U = D['units']
dropped = []


def geo(shape):
    return unary_union([Polygon(q['exterior'], q['holes']).buffer(0) for q in shape]) if shape else Polygon()


def ser(g):
    g = g.simplify(0.6) if not g.is_empty else g
    gs = g.geoms if isinstance(g, MultiPolygon) else [g]
    return [dict(exterior=[[round(x, 2), round(y, 2)] for x, y in q.exterior.coords], holes=[[[round(x, 2), round(y, 2)] for x, y in h.coords] for h in q.interiors]) for q in gs if not q.is_empty and q.area > 1]


def keep(g, minimum, label):
    out = []
    for q in (g.geoms if isinstance(g, MultiPolygon) else [g]):
        if q.is_empty:
            continue
        (out if q.area >= minimum else dropped).append(q if q.area >= minimum else (label, round(q.area), tuple(np.round(q.centroid.coords[0]))))
    return unary_union(out) if out else Polygon()


def biggest(g):
    return max(g.geoms, key=lambda q: q.area) if isinstance(g, MultiPolygon) else g


def half(a, b, ref, far=4000.0):
    """The half plane on ref's side of the line through a and b."""
    a, b = np.asarray(a, float), np.asarray(b, float); d = (b - a) / np.linalg.norm(b - a); n = np.array([-d[1], d[0]])
    if np.dot(np.asarray(ref, float) - a, n) < 0:
        n = -n
    return Polygon([tuple(a - d * far), tuple(b + d * far), tuple(b + d * far + n * far), tuple(a - d * far + n * far)])


sil = geo(D['silhouette']); field = geo(D['field_cell'])
OWN = 6                                     # a piece that forms the outline owns it; the base ends this far inside it

# ---- heights (PLAN section 2) ----
BASE = 0.06
FRAME_PROFILE = [[0, 0.0], [4, 0.016], [8, 0.028], [13, 0.036], [18, 0.040], [21, 0.042], [24, 0.043]]   # a rounded crown (round 2: the flatter band read as flat gold); full by 24 px
FIELD_SLOPE, FIELD_DEPTH = 7, 0.025
FIELD_FLOOR = BASE + FRAME_PROFILE[-1][1] - FIELD_DEPTH                                     # 0.078
RIB_BEVEL, RIB_DEPTH, RIB_SLOPE = (3, 0.01), 0.012, 3          # short bevel: the wires are 7 to 10 px wide
RIB_BASE = round(FIELD_FLOOR + 0.008 + RIB_BEVEL[1] + RIB_DEPTH + 0.002, 4)           # its lowest edge and sunken floor clear the field floor
LINE_BEVEL = (4, 0.015); LINE_BASE = round(FIELD_FLOOR + 0.008 + LINE_BEVEL[1], 4)
CLOUD_PROFILE = [[0, 0.0], [4, 0.02], [8, 0.035], [12, 0.042]]                               # full by 12 px, the fills begin at 12
CLOUD_SLOPE, CLOUD_DEPTH = 4, 0.016                                # 40 degrees
BOLT_RIM = 26                                                                                 # measured: bevel about 14 px, inner step about 10
BOLT_PROFILE = [[0, 0.0], [6, 0.02], [12, 0.034], [16, 0.038]]
BOLT_SLOPE, BOLT_DEPTH = 5, 0.018
POINT_BEVEL = (8, 0.03); POINT_TIP, POINT_RIDGE = 0.012, 0.09     # a stronger ridge (round 2: faces 8 to 10 degrees read flat)

pieces = []
pieces.append(dict(name='core', outline=ser(sil.buffer(-1).simplify(0.5)), material='Side', base=0.03, top=dict(kind='flat', height=0.0), no_clip=True))

# ---- clouds (built first: points and the base end inside them) ----
def cloud_piece(name):
    c = D['clouds'][name]; plate = geo(c['plate']); fills = geo(c['fills'])
    for t in D['tips'][name]:                                  # measured tips: a spike from the plate to the point
        T = Point(*t); q = nearest_points(plate.exterior if isinstance(plate, Polygon) else plate.boundary, T)[0]
        ring = plate.exterior if isinstance(plate, Polygon) else biggest(plate).exterior
        s0 = ring.project(q); L = ring.length
        P1 = ring.interpolate((s0 + 18) % L); P2 = ring.interpolate((s0 - 18) % L)
        plate = unary_union([plate, Polygon([t, P1.coords[0], P2.coords[0]]).buffer(0)])
    # between the cloud and the badge outline, every gap narrower than 28 px is filled completely (the cloud owns the
    # outline there); wider gaps stay frame. A partial fill left a 2 to 4 px ledge of base sharing the cloud's wall.
    near = sil.difference(sil.buffer(-30)).intersection(plate.buffer(30))
    strip = sil.difference(plate)
    thin = strip.difference(strip.buffer(-14).buffer(14)).intersection(near)
    thin = unary_union([q for q in (thin.geoms if isinstance(thin, MultiPolygon) else [thin]) if q.distance(plate) < 1.0 and q.area > 20])
    plate = Polygon(biggest(unary_union([plate, thin]).buffer(1.0).buffer(-1.0).intersection(sil)).exterior)
    # the cloud and its pearl run 12 px under the bolt (it lies on top), so the pearl meets the bolt's rim directly and no
    # wall is shared (round 2)
    if name == 'lower':                                         # only the cloud that lies under the bolt
        ext = fills.buffer(20).intersection(geo(D['bolt']['outline']).buffer(8))   # across the small gap and under the bolt
        fills = unary_union([fills, ext])
        plate = unary_union([plate, ext]).buffer(1.0).buffer(-1.0)
        plate = biggest(plate) if isinstance(plate, MultiPolygon) else plate
    # fills grown by the slope so the pearl floor is the traced fill, never into a gold stroke's core (the clean stroke
    # shrunk 2 px): every stroke keeps its full width as gold (flat core plus its two slopes)
    core = geo(c['gold']).buffer(-2)
    cells = keep(fills.buffer(CLOUD_SLOPE).difference(core).intersection(plate.buffer(-12 + CLOUD_SLOPE)), 60, f'{name} cloud fill')
    return plate, dict(name=f'cloud_{name}', outline=ser(plate), material='GoldCloud', top=dict(kind='profile', points=CLOUD_PROFILE),
                       cells=[dict(material='Pearl', shape=ser(cells), recess=dict(depth=CLOUD_DEPTH, width=CLOUD_SLOPE))])


lower_plate, lower_piece = cloud_piece('lower'); upper_plate, upper_piece = cloud_piece('upper')
clouds_all = unary_union([lower_plate, upper_plate])

# ---- star points: two faces on a tip to center ridge, from the tip to the field's edge, ending 6 px inside a cloud ----
point_pieces, point_regions = [], []
for k, p in D['points'].items():
    T, A, B = np.array(p['tip']), np.array(p['a']), np.array(p['b'])
    inward = (np.array([U['axis'], (U['top'] + U['bottom']) / 2]) - T); inward /= np.linalg.norm(inward)
    A2, B2 = A + inward * 45, B + inward * 45
    side = np.array([-inward[1], inward[0]])
    if np.dot(A - T, side) < 0:
        side = -side
    To = T - inward * 15; Ao = A + side * 15; Bo = B - side * 15             # beyond the flanks: the silhouette cuts the edge
    # it stops at the field's edge, except under a cloud: there it runs on 6 px under the cloud (both stopping at the same
    # field edge put their walls in one place)
    region = Polygon([tuple(To), tuple(Ao), tuple(A2 + side * 15), tuple(B2 - side * 15), tuple(Bo)]).convex_hull.intersection(sil).difference(field.difference(clouds_all)).difference(clouds_all.buffer(-OWN))
    region = biggest(keep(region, 400, f'point {k}'))
    C = (A2 + B2) / 2
    fa = region.intersection(half(T, C, A)); fb = region.intersection(half(T, C, B))
    facets = [dict(shape=ser(fa), p=[[*T, POINT_TIP], [*C, POINT_RIDGE], [*A, 0.0]]), dict(shape=ser(fb), p=[[*T, POINT_TIP], [*C, POINT_RIDGE], [*B, 0.0]])]
    point_regions.append(region)
    point_pieces.append(dict(name=f'point_{k}', outline=ser(region), material='GoldPoint', top=dict(kind='planes', facets=facets),
                             bevel=dict(width=POINT_BEVEL[0], height=POINT_BEVEL[1])))

# ---- base: frame and field; it ends 6 px inside every piece that forms the outline ----
owners = [lower_plate, upper_plate] + point_regions
# only along the badge's outer outline: elsewhere the base runs on under the covering piece
outer_band = sil.difference(sil.buffer(-(OWN + 2)))
strip = unary_union([g.difference(g.buffer(-OWN)) for g in owners]).intersection(outer_band)
base_out = sil.difference(strip)
base_out = unary_union([q for q in (base_out.geoms if isinstance(base_out, MultiPolygon) else [base_out]) if q.area > 50])
pieces.append(dict(name='base', outline=ser(base_out), material='GoldFrame', base=BASE, top=dict(kind='profile', points=FRAME_PROFILE, **{'from': ser(sil)}),
                   cells=[dict(material='Enamel', shape=ser(field.buffer(FIELD_SLOPE).intersection(sil.buffer(-12))), recess=dict(depth=FIELD_DEPTH, width=FIELD_SLOPE))]))
pieces += point_pieces

# ---- ribbons: gold pieces (fill and its gold lines), beveled on the gold sides only, the blue set in ----
rib_list = [dict(outline=geo(r['outline']), fill=geo(r['fill']), gold=geo(r.get('gold', []))) for r in D['ribbons']]
merged = True
while merged:                                                   # ribbons side by side become one piece (no shared walls)
    merged = False
    for a in range(len(rib_list)):
        for b in range(a + 1, len(rib_list)):
            if rib_list[a]['outline'].distance(rib_list[b]['outline']) < 3:
                rib_list[a] = dict(outline=unary_union([rib_list[a]['outline'], rib_list[b]['outline']]).buffer(2).buffer(-2),
                                   fill=unary_union([rib_list[a]['fill'], rib_list[b]['fill']]), gold=unary_union([rib_list[a]['gold'], rib_list[b]['gold']]))
                del rib_list[b]; merged = True; break
        if merged:
            break
D['ribbons'] = [dict(outline=ser(r['outline']), fill=ser(r['fill']), gold=ser(r['gold']) if not r['gold'].is_empty else []) for r in rib_list]
for i, r in enumerate(D['ribbons']):
    out = keep(geo(r['outline']).buffer(0.5).buffer(-0.5), 300, f'ribbon {i}')
    out = out.intersection(field.buffer(-4))                    # on the field's floor, never on the frame's slope
    covers = unary_union([geo(D['bolt']['outline']), clouds_all])
    out = unary_union([out, out.buffer(16).intersection(covers.buffer(-OWN - 2))])   # ends tucked under the bolt and clouds
    if out.is_empty:
        continue
    # approved method (Tidal Compass, Astral Navigator): the colors come from the mockup itself, so the ribbon's whole top
    # is one enamel with the field (Enamel, sampled from the picture by enamel_fill.py); only its gold wires are metal.
    # A ribbon edge traced a few px off still shows the mockup's exact light blue and shading.
    wires = geo(r.get('gold', [])).intersection(out)
    core = wires.buffer(-2) if not wires.is_empty else Polygon()
    cell = out.buffer(RIB_SLOPE).difference(core)              # past the piece on the plain sides: no gold slope there
    skip = out.difference(wires.buffer(4)) if not wires.is_empty else out
    pieces.append(dict(name=f'ribbon_{i}', outline=ser(out), material='GoldRibbon', side='Side', base=RIB_BASE, top=dict(kind='flat', height=0.0),
                       bevel=dict(width=RIB_BEVEL[0], height=RIB_BEVEL[1]), edge_skip=ser(skip.buffer(1.0)),
                       cells=[dict(material='Enamel', shape=ser(cell), recess=dict(depth=RIB_DEPTH, width=RIB_SLOPE))]))
# ---- thin gold lines lying on the field by themselves (the navy crescent's outline) ----
for i, fl in enumerate(D['field_lines']):
    g = keep(geo(fl), 120, f'field line {i}')
    if not g.is_empty:
        pieces.append(dict(name=f'line_{i}', outline=ser(g), material='GoldRibbon', top=dict(kind='flat', height=0.0),   # base by the stack rule: its root lies on the frame's slope
                           bevel=dict(width=LINE_BEVEL[0], height=LINE_BEVEL[1])))

pieces.append(lower_piece)
# ---- bolt: its measured 26 px rim, one sunken yellow floor; its light and deep tones come from the mockup (enamel_fill.py) ----
bolt = geo(D['bolt']['outline']); V = {k: np.array(v) for k, v in D['bolt']['vertices'].items()}
floor = bolt.buffer(-BOLT_RIM, join_style='mitre', mitre_limit=4)
pieces.append(dict(name='bolt', outline=ser(bolt), material='GoldBolt', top=dict(kind='profile', points=BOLT_PROFILE),
                   cells=[dict(material='Bolt', shape=ser(floor.buffer(BOLT_SLOPE)), recess=dict(depth=BOLT_DEPTH, width=BOLT_SLOPE))]))
pieces.append(upper_piece)

spec = dict(units=dict(S=U['S'], axis=U['axis'], top=U['top'], width_px=U['width_px'], height_px=U['height_px']),
            box=[float(sil.bounds[0]), U['top'], float(sil.bounds[2]), U['bottom']], gap=0.008, pieces=pieces)
json.dump(spec, open(HERE / 'pieces.json', 'w'))
print(len(pieces), 'pieces:', [p['name'] for p in pieces])
print('heights: field floor', round(FIELD_FLOOR, 3), 'ribbon base', RIB_BASE, 'line base', LINE_BASE,
      '| recess below each crest: field', FIELD_DEPTH, 'cloud', CLOUD_DEPTH, 'bolt', BOLT_DEPTH, 'ribbon', RIB_DEPTH)
print('dropped shapes (name, area px2, center):', dropped)
