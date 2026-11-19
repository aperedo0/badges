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
# 4. spike points: two facets on one center ridge from the tip to inside the ring (no hip at the ring)
def spike_point(name, s):
    T = np.array(s['tip']); A = np.array(s['corner_a']); B = np.array(s['corner_b'])
    mid = (A + B) / 2; ax = mid - T; L = np.linalg.norm(ax); ax /= L
    dT = np.linalg.norm(T - np.array(RC))
    r_end = dT - (RI + 6); r_mid = dT - (RR + RI) / 2              # end over the ring band; ridge highest at the ring's middle
    A2 = T + (A - T) * (r_end / L); B2 = T + (B - T) * (r_end / L); E2 = T + ax * r_end
    Am = T + (A - T) * (r_mid / L); Bm = T + (B - T) * (r_mid / L); Mm = T + ax * r_mid
    poly = Polygon([tuple(T), tuple(A2), tuple(B2)])
    f = [(Polygon([tuple(T), tuple(Am), tuple(Mm)]), [[*T, 0.010], [*Mm, 0.045], [*Am, 0.0]]),
         (Polygon([tuple(T), tuple(Mm), tuple(Bm)]), [[*T, 0.010], [*Mm, 0.045], [*Bm, 0.0]]),
         (Polygon([tuple(Am), tuple(A2), tuple(E2), tuple(Mm)]), [[*Mm, 0.045], [*E2, 0.010], [*Am, 0.0]]),
         (Polygon([tuple(Mm), tuple(E2), tuple(B2), tuple(Bm)]), [[*Mm, 0.045], [*E2, 0.010], [*Bm, 0.0]])]
    facets = [dict(shape=ser(q), p=pts) for q, pts in f]
    return dict(name=name, outline=ser(poly), material='GoldRing', top=dict(kind='planes', facets=facets), bevel=dict(width=7, height=0.025))
for n in ('top', 'diag_left', 'diag_right', 'side_left', 'side_right'):
    p = spike_point('point_' + n, SP[n])
    if n.endswith('right'):
        p['same_base_as'] = 'point_' + n.replace('right', 'left')
    pieces.append(p)
# 5. sun: bevel and rim make its 23 px gold edge; a gentle dome
pieces.append(dict(name='sun', outline=ser(Point(*SC).buffer(SRIM, quad_segs=96)), material='Gold', top=dict(kind='flat', height=0.0, dome=0.04),
                   bevel=dict(width=9, height=0.03), rim=dict(width=14, height=0.015, material='Gold'),
                   cells=[dict(material='SunDisc', shape=ser(Point(*SC).buffer(SR, quad_segs=96)))]))


# 6, 7. mountains: faceted bodies with their faces as color areas; snow caps and the chevron as their own pieces on top
def facets_of(m, rise):
    out = geo(m['outline']); px, py = m['peak']; xs = np.asarray(out.exterior.coords)[:, 0]; ybot = min(out.bounds[3], m.get('foot', 1e9))
    xl, xr = xs.min(), xs.max()
    return out, px, [(box(0, 0, px, 2000), [[px, py, rise], [xl, ybot, 0.0], [px, ybot, rise * 0.4]]),
                     (box(px, 0, 2000, 2000), [[px, py, rise], [xr, ybot, 0.0], [px, ybot, rise * 0.4]])]


def planes_on(shape, fac):
    return dict(kind='planes', facets=[dict(shape=ser(shape.intersection(h)), p=pts) for h, pts in fac if not shape.intersection(h).is_empty])


def mountain(name, m, rise, twin=None):
    out, px, fac = facets_of(m, rise)
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
            inner = g.difference(g.boundary.difference(out.buffer(-12).exterior.buffer(2.5)).buffer(14)) if True else g.buffer(-14)
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


pieces += mountain('mountain_side_left', D['mountains']['side_left'], 0.14)
pieces += mountain('mountain_side_right', D['mountains']['side_right'], 0.14, twin='mountain_side_left')
D['mountains']['central']['foot'] = 905.0                        # the visible foot, not the hidden tongue
pieces += mountain('mountain_central', D['mountains']['central'], 0.20)
# 8. clouds, small lobes included
cl = [geo(c) for c in D['cloud_cells']]
for i, c in enumerate(cl):
    c = keep(c, 500, 'cloud cell')
    if c.is_empty:
        continue
    out = c.buffer(12, quad_segs=8).intersection(sil.buffer(-20))
    cp = dict(name=f'cloud_{i}', outline=ser(out), material='Gold', top=dict(kind='flat', height=0.0, dome=0.02),
              bevel=dict(width=6, height=0.022), rim=dict(width=6, height=0.008, material='Gold'),
              cells=[dict(material='Cloud', shape=ser(out.buffer(-12)))], edge_skip=ser(sil.buffer(-20)))
    if i % 2 == 1:
        cp['same_base_as'] = f'cloud_{i - 1}'                      # cells come as left, mirror pairs
    pieces.append(cp)
# 10. border along the lower outline, about 28 px wide
ring_zone = Point(*RC).buffer(RR + 1, quad_segs=96).difference(Point(*RC).buffer(RI - 1, quad_segs=96))
border = keep(sil.difference(sil.buffer(-24)).intersection(box(0, 690, 1312, 1300)).difference(ring_zone.intersection(box(0, 0, 1312, 700))), 400, 'border')
border_piece = dict(name='border', outline=ser(border), material='GoldLower', top=dict(kind='profile', points=[[0, 0.0], [3, 0.009], [6, 0.018], [12, 0.028], [20, 0.032]]))
# 9. curls: the gold between the cloud lobes, running into the border
clouds_all = unary_union([q.buffer(6) for q in cl])
# only the chunky hooks between lobes: drop the thin rings around the clouds (their own rims make those) and the border band
curls = geo(D['lower_gold']).difference(clouds_all.buffer(4)).buffer(-5).buffer(5)
curls = keep(curls, 400, 'curl')
for j, q in enumerate(sorted((curls.geoms if isinstance(curls, MultiPolygon) else [curls]), key=lambda q: q.centroid.x)):
    cp = dict(name=f'curl_{j}', outline=ser(q), material='GoldLower', top=dict(kind='flat', height=0.0, dome=0.02), bevel=dict(width=7, height=0.025))
    pieces.append(cp)
names_curl = [p['name'] for p in pieces if p['name'].startswith('curl_')]
for p in pieces:
    if p['name'].startswith('curl_') and p['name'] != names_curl[0] and len(names_curl) == 2:
        p['same_base_as'] = names_curl[0]
pieces.append(border_piece)
# 11. gem first, then the frame over its tucked rim
gem_pts = D['gem']['outline']; gem = Polygon(gem_pts)
pieces.append(dict(name='gem', outline=ser(gem.buffer(2, join_style='mitre')), material='Gem', gem=dict(apex=D['gem']['apex'], rise=0.12), base_from=dict(piece='frame', offset=-0.016)))
frame = geo(D['frame']).difference(gem)
pieces.append(dict(name='frame', outline=ser(frame), material='Gold', base_ignore=['gem'], top=dict(kind='profile', points=[[0, 0.0], [4, 0.014], [8, 0.028], [16, 0.045], [30, 0.06]])))
spec = dict(units=dict(S=5.45 / 1161, axis=AX, top=15.0, width_px=1312, height_px=1199), box=[81, 15, 1227, 1177], gap=0.008, pieces=pieces)
json.dump(spec, open(HERE / 'pieces.json', 'w'))
print(len(pieces), 'pieces:', [p['name'] for p in pieces])
print('dropped shapes (name, area px2, center):', dropped)
