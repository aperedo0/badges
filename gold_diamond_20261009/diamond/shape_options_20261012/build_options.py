"""Build model-only Diamond options from the preserved approved builder."""
from pathlib import Path
import hashlib
import json
import math
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'codex_rest_20261011/approved5/tools/build_gem.py'
BASE_CENTER = (.95345 + .85345) / 2


def make_planes(ns, repetitions, bottom, top, barrel, star_height=None):
    step = 360 / repetitions
    half = math.radians(step / 2)
    radius, table_radius = 3.12, 1.40
    ring_radius = radius - .03 if barrel else radius
    star_y = 1.63745
    if bottom < .7:
        star_y = 2.349 - .5 * (2.349 - top)
    if star_height is not None:
        star_y = star_height
    make = ns['make_plane']
    elevation = ns['elevation_through']
    planes = [('table', np.array([0., 1., 0.]), 2.349)]
    bezel = elevation((table_radius, 2.349), (ring_radius, top))
    tip_distance = table_radius + (ring_radius-table_radius) * (2.349-star_y) / (2.349-top)
    tip_radius = tip_distance / math.cos(half)
    table_apothem = table_radius * math.cos(half)
    star = elevation((table_apothem, 2.349), (tip_radius, star_y))
    upper = elevation((ring_radius, top), (tip_radius * math.cos(half/2), star_y))
    main = elevation((ring_radius, bottom), (0., -2.455))
    lower = main + 3
    for k in range(repetitions):
        planes.append(('bezel', *make(step*k, bezel, ring_radius, top)))
        planes.append(('star', *make(step/2+step*k, star, table_apothem, 2.349)))
        planes.append(('main', *make(step*k, main, ring_radius, bottom)))
    for k in range(2*repetitions):
        azimuth = step/4 + step/2*k
        planes.append(('upper', *make(azimuth, upper, ring_radius, top)))
        planes.append(('lower', *make(azimuth, lower, ring_radius, bottom)))
    for k in range(4*repetitions):
        azimuth = step/4*k
        if barrel:
            center = (bottom+top)/2
            slopes = [elevation((ring_radius, bottom), (radius, center)),
                      elevation((radius, center), (ring_radius, top))]
            for wall_elevation in slopes:
                planes.append(('wall', *make(azimuth, wall_elevation, radius, center)))
        else:
            planes.append(('wall', *make(azimuth, 0., radius, 0.)))
    return planes


def build(name, repetitions=8, thickness=.1, shallow=False, barrel=False, star_height=None):
    ns = {'__name__': 'shape_option_builder', '__file__': str(SOURCE)}
    exec(compile(SOURCE.read_text(), str(SOURCE), 'exec'), ns)
    ns['TURN_DEGREES'] = 22.5
    bottom = -2.455 + 3.12*math.tan(math.radians(41)) if shallow else BASE_CENTER-thickness/2
    top = bottom+thickness
    planes = make_planes(ns, repetitions, bottom, top, barrel, star_height)
    vertices = ns['intersect_planes'](planes)
    polygons = ns['facet_polygons'](planes, vertices)
    # The contract counts actual supporting facets, not unused input planes.
    active = [i for i,p in enumerate(polygons) if p is not None]
    planes = [planes[i] for i in active]
    polygons = [polygons[i] for i in active]
    ns['EXPECTED_FACET_COUNT'] = len(planes)
    assert len(planes) <= 256
    triangles = ns['triangulate'](polygons)
    ns['run_checks'](planes, vertices, polygons, triangles)
    low, high = vertices.min(0), vertices.max(0)
    # Rounder tessellation can change support on X and Z by a small amount.
    # Normalize X and Z equally, preserving a round gem and the approved width.
    radial_scale = 3.12/max(abs(low[0]), abs(high[0]))
    vertices[:, [0,2]] *= radial_scale
    corrected = []
    for family, normal, offset in planes:
        normal = normal / np.array([radial_scale,1,radial_scale])
        length = np.linalg.norm(normal)
        corrected.append((family, normal/length, offset/length))
    planes = corrected
    ns['run_checks'](planes, vertices, polygons, triangles)
    low, high = vertices.min(0), vertices.max(0)
    assert abs(high[0]-low[0]-6.24) < 1e-5
    output = ROOT / name
    output.mkdir(exist_ok=True)
    model = ns['write_usd'](output, planes, vertices, triangles)
    np.savez(output/'planes.npz', normals=np.array([p[1] for p in planes]),
             offsets=np.array([p[2] for p in planes]), vertices=vertices,
             triangles=np.array([t[1:] for t in triangles]))
    facts = dict(name=name, planes=len(planes), plane_work_relative_to_89=len(planes)/89,
                 triangles=len(triangles), bytes=model.stat().st_size,
                 band_bottom=bottom, band_top=top, band_center_delta=(bottom+top)/2-BASE_CENTER,
                 pavilion_degrees=math.degrees(math.atan((bottom+2.455)/(3.12*radial_scale))),
                 radial_scale=radial_scale, bounds=[low.tolist(),high.tolist()],
                 model_sha256=hashlib.sha256(model.read_bytes()).hexdigest())
    (output/'geometry.json').write_text(json.dumps(facts,indent=2)+'\n')
    print(json.dumps(facts))


if __name__ == '__main__':
    options = {
        'thick': dict(thickness=.25),
        'round': dict(repetitions=16),
        'shallow': dict(shallow=True),
        'combined': dict(repetitions=16,thickness=.25,shallow=True),
        'combined_raised': dict(repetitions=16,thickness=.25,
                               star_height=2.349-.5*(2.349-(-2.455+3.12*math.tan(math.radians(41))+.25))),
        'barrel': dict(thickness=.25,barrel=True),
    }
    for name in sys.argv[1:] or options:
        build(name, **options[name])
