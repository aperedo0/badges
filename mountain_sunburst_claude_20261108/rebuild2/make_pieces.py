"""Turn the measured shapes (rebuild/design.json) into the stacked pieces file (pieces.json) for badge3d.py.

Plan: rebuild2/PLAN.md section 2. All lengths in mockup pixels, heights in units.
"""
import json
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon, Point, box, MultiPolygon
from shapely.ops import unary_union
from shapely.affinity import scale as sscale

HERE = Path(__file__).resolve().parent
D = json.load(open(HERE.parent / 'rebuild/design.json'))
AX = 653.5; LW = D['line_width']
RC = D['ring']['center']; RR = D['ring']['r_outer']; RI = D['ring']['r_inner']
SC = D['sun']['center']; SRIM = D['sun']['r_rim']; SR = D['sun']['r_enamel']


def geo(shape):
    return unary_union([Polygon(q['exterior'], q['holes']).buffer(0) for q in shape])


def ser(g):
    gs = g.geoms if isinstance(g, MultiPolygon) else [g]
    return [dict(exterior=[[round(x, 2), round(y, 2)] for x, y in q.exterior.coords], holes=[[[round(x, 2), round(y, 2)] for x, y in h.coords] for h in q.interiors]) for q in gs if not q.is_empty and q.area > 1]


def mirror(g):
    return sscale(g, xfact=-1, yfact=1, origin=(AX, 0))


SP = json.load(open(HERE.parent / 'rebuild/design_spikes.json'))['spikes']
HALF = LW / 2
dropped = []


def keep(g, minimum, label):
    out = []
    for q in (g.geoms if isinstance(g, MultiPolygon) else [g]):
        if q.is_empty:
            continue
        (out if q.area >= minimum else dropped).append(q if q.area >= minimum else (label, round(q.area), tuple(np.round(q.centroid.coords[0]))))
    return unary_union(out) if out else Polygon()


pieces = []
sil = geo(D['silhouette'])
# 0. hidden core: nothing can be seen through the badge where pieces do not overlap
pieces.append(dict(name='core', outline=ser(sil.buffer(-1).simplify(0.5)), material='Side', base=0.03, top=dict(kind='flat', height=0.0), no_clip=True))
# 1. red background, under the ring's outer edge (no shared wall with the ring)
pieces.append(dict(name='background', outline=ser(Point(*RC).buffer(459, quad_segs=96)), material='Red', base=0.06, top=dict(kind='flat', height=0.0)))
# 2. the gold star: everything inside the ring that is not a red opening; lemon areas set in; bevels down into the red
red = unary_union([geo(c['shape']) for c in D['plate_cells'] if c['color'] == 'red'])
lemon = unary_union([geo(c['shape']) for c in D['plate_cells'] if c['color'] == 'lemon'])
red_open = keep(red.buffer(-HALF, join_style='mitre', mitre_limit=3).buffer(-2).buffer(2), 150, 'red opening')
lemon_in = keep(lemon.buffer(-HALF, join_style='mitre', mitre_limit=3).buffer(-2).buffer(2), 150, 'lemon area')
star = Point(*RC).buffer(RI + 6, quad_segs=96).difference(red_open)
pieces.append(dict(name='star', outline=ser(star), material='Gold', top=dict(kind='flat', height=0.0), bevel=dict(width=9, height=0.03),
                   cells=[dict(material='Lemon', shape=ser(lemon_in), recess=dict(depth=0.012, width=6))]))
# 3. ring: a rounded band over the star's outer edge
ring = Point(*RC).buffer(RR, quad_segs=96).difference(Point(*RC).buffer(RI, quad_segs=96))
pieces.append(dict(name='ring', outline=ser(ring), material='GoldRing', top=dict(kind='profile', points=[[0, 0.0], [2.5, 0.009], [5, 0.018], [10, 0.031], [14.3, 0.036], [20, 0.036]])))
# 4. the five long blades: each one piece over the ring, from under the sun to its tip (mockup: the blade's gold bars
#    cross over the ring; cand02 cut each blade in two at the ring and was read as a kite plus a cone). The blade is the
#    star between its two neighboring red wedges, joined to its point beyond the ring; its yellow is set in, flat (a
#    3.5 degree ridge split the yellow into patches of different brightness, cand04).
SUNC = np.array(SC)
reds = [q for q in (red_open.geoms if isinstance(red_open, MultiPolygon) else [red_open])]
star_in = Point(*RC).buffer(RI + 6, quad_segs=96).difference(red_open)


def ang(p):
    return np.arctan2(p[1] - SUNC[1], p[0] - SUNC[0])


def blade(name, s):
    T = np.array(s['tip']); A = np.array(s['corner_a']); B = np.array(s['corner_b']); th = ang(T)
    d = [((ang(q.centroid.coords[0]) - th + np.pi) % (2 * np.pi) - np.pi) for q in reds]
    lo = max(x for x in d if x < 0); hi = min(x for x in d if x > 0)
    W = Polygon([tuple(SUNC)] + [(SUNC[0] + 900 * np.cos(th + a), SUNC[1] + 900 * np.sin(th + a)) for a in np.linspace(lo, hi, 48)])
    inner = star_in.intersection(W).intersection(Point(*RC).buffer(RI - HALF - 4, quad_segs=96)).difference(Point(*SC).buffer(SRIM - 25, quad_segs=96))
    probe = Point(*(SUNC + (T - SUNC) / np.linalg.norm(T - SUNC) * (SRIM + 40)))
    inner = [q for q in (inner.geoms if isinstance(inner, MultiPolygon) else [inner]) if q.distance(probe) < 1]
    L = np.linalg.norm((A + B) / 2 - T); dT = np.linalg.norm(T - np.array(RC)); r_end = dT - (RI - HALF - 12)
    A2 = T + (A - T) * (r_end / L); B2 = T + (B - T) * (r_end / L)
    point = Polygon([tuple(T), tuple(A2), tuple(B2)])
    point = point.difference(red_open.buffer(0.5))                 # never into a red wedge
    g = unary_union(inner + [point]).buffer(1.5, join_style='mitre').buffer(-1.5, join_style='mitre')
    g = max(g.geoms, key=lambda q: q.area) if isinstance(g, MultiPolygon) else g
    cell = keep(lemon_in.intersection(g.buffer(-9)), 150, name + ' lemon')
    return dict(name=name, outline=ser(g), material='Gold', top=dict(kind='flat', height=0.0), bevel=dict(width=8, height=0.03),
                cells=[dict(material='Lemon', shape=ser(cell), recess=dict(depth=0.012, width=6))] if not cell.is_empty else [])


for n in ('top', 'diag_left', 'diag_right', 'side_left', 'side_right'):
    p = blade('blade_' + n, SP[n])
    if n.endswith('right'):
        p['same_base_as'] = 'blade_' + n.replace('right', 'left')
    pieces.append(p)
# 5. sun: bevel and rim make its 23 px gold edge; a gentle dome (a deeper one mirrored the studio's low reflector as a
# white glow above the peak, cand03)
pieces.append(dict(name='sun', outline=ser(Point(*SC).buffer(SRIM, quad_segs=96)), material='Gold', top=dict(kind='flat', height=0.0, dome=0.03),
                   bevel=dict(width=9, height=0.03), rim=dict(width=14, height=0.015, material='Gold'),
                   cells=[dict(material='SunDisc', shape=ser(Point(*SC).buffer(SR, quad_segs=96)))]))


# 6, 7. mountains: two faces meeting at the center ridge; snow caps and the chevron as their own pieces on the same faces.
# Colored faces are flat, as real enamel: any tilt of about 0.04 sends the reflection onto a bright part of the studio
# (cand02: tilted left and down, teal read pale grey; cand03: tilted up, navy still read 9 times its paint). The faces
# differ by their paint, as in the mockup; depth comes from the stacked pieces and their gold edges.
RIDGE, BOTTOM_SLOPE = 0.0, 0.0


def facets_of(m, ridge, tilt=None):
    out = geo(m['outline']); px, py = m['peak']; xs = np.asarray(out.exterior.coords)[:, 0]; ybot = min(out.bounds[3], m.get('foot', 1e9))
    xl, xr = xs.min(), xs.max(); hb = ridge + BOTTOM_SLOPE * (ybot - py) * (5.45 / 1161)
    if tilt:                                                   # one plane facing slightly up and right (normal slopes a, b)
        a, b = tilt; S_ = 5.45 / 1161
        return out, px, [(box(0, 0, 2000, 2000), [[xr, py, 0.0], [xl, py, a * (xr - xl) * S_], [xr, ybot, b * (ybot - py) * S_]])]
    return out, px, [(box(0, 0, px, 2000), [[xl, py, 0.0], [px, py, ridge], [px, ybot, hb]]),
                     (box(px, 0, 2000, 2000), [[xr, py, 0.0], [px, py, ridge], [px, ybot, hb]])]


def planes_on(shape, fac):
    return dict(kind='planes', facets=[dict(shape=ser(shape.intersection(h)), p=pts) for h, pts in fac if not shape.intersection(h).is_empty])


def mountain(name, m, ridge, twin=None, tilt=None):
    out, px, fac = facets_of(m, ridge, tilt)
    cells = []
    for c in m['cells']:
        g = geo(c['shape']).intersection(out.buffer(-15))
        if c['color'] in ('royal', 'teal', 'navy', 'steel'):
            cells.append(dict(material={'royal': 'Royal', 'teal': 'Teal', 'navy': 'Navy', 'steel': 'Steel'}[c['color']], shape=ser(g)))
    body = dict(name=name, outline=ser(out), material='Gold', top=planes_on(out, fac), bevel=dict(width=7, height=0.025),
                rim=dict(width=8, height=0.01, material='Gold'), cells=[c for c in cells if c['shape']])
    extra = []
    for c in m['cells']:
        if c['color'] in ('snow_white', 'navy_chevron'):
            g = keep(geo(c['shape']).buffer(4, join_style='mitre', mitre_limit=3).intersection(out.buffer(-12)), 300, name + ' ' + c['color'])
            if g.is_empty:
                continue
            inner = g.difference(g.boundary.difference(out.buffer(-12).exterior.buffer(2.5)).buffer(14))
            if c['color'] == 'snow_white':
                cl = [dict(material='Snow', shape=ser(inner.intersection(box(0, 0, px, 2000)))), dict(material='SnowLavender', shape=ser(inner.intersection(box(px, 0, 2000, 2000))))]
            else:
                cl = [dict(material='Navy', shape=ser(inner))]
            extra.append(dict(name=name + ('_snow' if c['color'] == 'snow_white' else '_chevron'), outline=ser(g), material='Gold', top=planes_on(g, fac),
                              bevel=dict(width=6, height=0.02), rim=dict(width=8, height=0.01, material='Gold'), cells=[x for x in cl if x['shape']],
                              edge_skip=ser(out.buffer(-12))))
    if twin:
        body['same_base_as'] = twin
        for e in extra:
            e['same_base_as'] = twin + e['name'][len(name):]
    return [body] + extra


pieces += mountain('mountain_side_left', D['mountains']['side_left'], RIDGE)
pieces += mountain('mountain_side_right', D['mountains']['side_right'], RIDGE, twin='mountain_side_left')
D['mountains']['central']['foot'] = 905.0                        # the visible foot, not the hidden tongue
# the central mountain faces slightly up and right: flat, the low reflector's mirror spot sat on the teal face's lower
# left corner as a white glow (cand05); this tilt moves it about 0.3 units down and left onto the cloud and gold
pieces += mountain('mountain_central', D['mountains']['central'], RIDGE, tilt=(0.03, 0.02))

# 8. lower body: one gold plate with the clouds set in. The clouds are traced from the mockup's white (warm shading
# included), smoothed, the left half mirrored. The gold left between them is the C curls, the cloud rims and the wide
# border, exactly where the mockup has gold (cand02 built clouds, curls and border separately: the curls came out as
# thorns, the border half as wide, and small lobes knotted beside the gem).
from scipy import ndimage as ndi
from scipy.ndimage import gaussian_filter
import contourpy
from PIL import Image
mock = np.asarray(Image.open(HERE.parent / 'reference/mockup.png').convert('RGB')).astype(float) / 255
r_, g_, b_ = mock.transpose(2, 0, 1)
wm = (mock.max(2) > 0.62) & (b_ / np.maximum(g_, 1e-3) > 0.8) & ((r_ - b_) < 0.32) & (b_ < r_ + 0.08)
wm[:690] = False
wm = ndi.binary_opening(wm, iterations=2)
lab, nlab = ndi.label(wm); sizes = ndi.sum(wm, lab, range(1, nlab + 1)); cents = ndi.center_of_mass(wm, lab, range(1, nlab + 1))
wm = np.isin(lab, [i + 1 for i in range(nlab) if sizes[i] > 1500 and cents[i][0] > 760])
# the left cloud traced and mirrored. (Averaging both sides by signed distance erased the thin gold C curls, cand03:
# a curl on one side lands on white on the other, and the average is white.)
W = Polygon()
for q in sorted([Polygon(l + 0.5) for l in contourpy.contour_generator(z=gaussian_filter(wm.astype(float), 3.0), line_type='Separate').lines(0.5) if len(l) > 3], key=lambda q: -q.area):
    W = W.symmetric_difference(q.buffer(0))
cl_left = keep(W.simplify(0.4).intersection(box(0, 0, AX, 2000)), 1500, 'cloud')
clouds = unary_union([cl_left, mirror(cl_left)]).buffer(0.5).buffer(-0.5)
gem_pts = D['gem']['outline']; gem = Polygon(gem_pts)
frame_out = gem.buffer(40, join_style='mitre', mitre_limit=2.0).intersection(sil.buffer(-3))
band = sil.difference(sil.buffer(-55)).intersection(box(0, 745, 2000, 2000))
plate = unary_union([clouds.buffer(15), band, frame_out]).buffer(8).buffer(-8).buffer(-5).buffer(5).intersection(sil)   # no spurs (cand04)
plate = unary_union([Polygon(q.exterior) for q in (plate.geoms if isinstance(plate, MultiPolygon) else [plate]) if q.area > 400])
plate = plate.difference(gem.buffer(1, join_style='mitre'))          # the gem fills this opening; the frame covers the seam
pieces.append(dict(name='lower_plate', outline=ser(plate), material='GoldLower', top=dict(kind='profile', points=[[0, 0.0], [5, 0.016], [10, 0.03], [18, 0.045], [30, 0.055], [45, 0.06]]),
                   cells=[dict(material='Cloud', shape=ser(clouds.intersection(plate.buffer(-6))), recess=dict(depth=0.02, width=7))]))
# 9. gem first, then the frame over its tucked rim (about 40 px wide, as the mockup)
pieces.append(dict(name='gem', outline=ser(gem.buffer(2, join_style='mitre')), material='Gem', gem=dict(apex=D['gem']['apex'], rise=0.12), base_from=dict(piece='frame', offset=-0.016)))
frame = frame_out.difference(gem)
pieces.append(dict(name='frame', outline=ser(frame), material='Gold', base_ignore=['gem'], top=dict(kind='profile', points=[[0, 0.0], [5, 0.018], [10, 0.034], [20, 0.05], [40, 0.06]])))
spec = dict(units=dict(S=5.45 / 1161, axis=AX, top=15.0, width_px=1312, height_px=1199), box=[81, 15, 1227, 1177], gap=0.008, pieces=pieces)
json.dump(spec, open(HERE / 'pieces.json', 'w'))
print(len(pieces), 'pieces:', [p['name'] for p in pieces])
print('dropped shapes (name, area px2, center):', dropped)
