"""Raise the original gem's widest band while preserving its exact envelope."""
from pathlib import Path
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(__file__).with_name('build_gem.py')
namespace = {'__name__': 'original_raised_builder', '__file__': str(SOURCE)}
exec(compile(SOURCE.read_text(), str(SOURCE), 'exec'), namespace)
original_top = namespace['GIRDLE_TOP_Y']
original_bottom = namespace['GIRDLE_BOTTOM_Y']
table = namespace['TABLE_Y']
rise = 0.05 * (table - original_top)
namespace['GIRDLE_TOP_Y'] = original_top + rise
namespace['GIRDLE_BOTTOM_Y'] = original_bottom + rise
namespace['STAR_TIP_Y'] = table - 0.95 * (table - namespace['STAR_TIP_Y'])
directory = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'rebuilt'
directory.mkdir(parents=True, exist_ok=True)
planes = namespace['facet_planes']()
vertices = namespace['intersect_planes'](planes)
polygons = namespace['facet_polygons'](planes, vertices)
triangles = namespace['triangulate'](polygons)
namespace['run_checks'](planes, vertices, polygons, triangles)
namespace['write_usd'](directory, planes, vertices, triangles)
model = directory / 'diamond_badge_mobile.usdz'
facts = {
    'source': 'Original installed gem, not a shallower recut',
    'girdle_rise': rise, 'original_crown_height': table - original_top,
    'girdle_top_y': namespace['GIRDLE_TOP_Y'],
    'girdle_bottom_y': namespace['GIRDLE_BOTTOM_Y'],
    'table_y': table, 'culet_y': namespace['CULET_Y'],
    'star_tip_y': namespace['STAR_TIP_Y'],
    'pavilion_degrees': math.degrees(math.atan((namespace['GIRDLE_BOTTOM_Y'] - namespace['CULET_Y']) / namespace['GIRDLE_APOTHEM'])),
    'lower_girdle_extra_degrees': namespace['LOWER_GIRDLE_EXTRA_DEGREES'],
    'azimuth_degrees': namespace['TURN_DEGREES'],
    'planes': len(planes), 'triangles': len(triangles),
    'bounds': [vertices.min(0).tolist(), vertices.max(0).tolist()],
    'model_sha256': hashlib.sha256(model.read_bytes()).hexdigest(),
}
(directory / 'geometry.json').write_text(json.dumps(facts, indent=2))
assert abs(vertices.min(0)[1] + 2.455) < 1e-6
assert abs(vertices.max(0)[1] - 2.349) < 1e-6
assert abs(vertices.min(0)[0] + 3.12) < 1e-6
assert abs(vertices.max(0)[0] - 3.12) < 1e-6
print(json.dumps(facts, indent=2))
