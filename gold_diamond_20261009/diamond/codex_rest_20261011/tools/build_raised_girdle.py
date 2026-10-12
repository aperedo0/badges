"""Owner-requested higher widest band, derived from the 41 degree copy."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'gem_shader_20261011/model/build_gem.py'
namespace = {'__name__': 'raised_builder', '__file__': str(SOURCE)}
exec(compile(SOURCE.read_text(), str(SOURCE), 'exec'), namespace)
base = json.loads((ROOT / 'recuts/02_41/geometry.json').read_text())
table = base['table_y']
old_top = base['girdle_top_y']
rise = 0.15 * (table - old_top)
new_top = old_top + rise
namespace['TABLE_Y'] = table
namespace['GIRDLE_TOP_Y'] = new_top
namespace['GIRDLE_BOTTOM_Y'] = base['girdle_bottom_y'] + rise
old_star = 1.60 + base['crown_translation_y']
namespace['STAR_TIP_Y'] = table - 0.85 * (table - old_star)
namespace['LOWER_GIRDLE_EXTRA_DEGREES'] = 2.0
directory = ROOT / 'recuts/04_raised15'
directory.mkdir(parents=True, exist_ok=True)
planes = namespace['facet_planes']()
vertices = namespace['intersect_planes'](planes)
polygons = namespace['facet_polygons'](planes, vertices)
triangles = namespace['triangulate'](polygons)
namespace['run_checks'](planes, vertices, polygons, triangles)
namespace['write_usd'](directory, planes, vertices, triangles)
np.savez(directory / 'gem_planes.npz', normals=np.array([p[1] for p in planes]), offsets=np.array([p[2] for p in planes]), families=np.array([p[0] for p in planes]), ALLP=np.array([[vertices[a], vertices[b], vertices[c]] for _, a, b, c in triangles]))
model = directory / 'diamond_badge_mobile.usdz'
facts = {'owner_requested_variant': 'Raise widest band by 15 percent of the 41 degree crown height, with flat top fixed.', 'rise_y': rise, 'pavilion_degrees': math.degrees(math.atan((namespace['GIRDLE_BOTTOM_Y'] - namespace['CULET_Y']) / namespace['GIRDLE_APOTHEM'])), 'lower_girdle_extra_degrees': 2.0, 'rest_azimuth_degrees': 22.5, 'girdle_bottom_y': namespace['GIRDLE_BOTTOM_Y'], 'girdle_top_y': new_top, 'table_y': table, 'culet_y': namespace['CULET_Y'], 'star_tip_y': namespace['STAR_TIP_Y'], 'planes': len(planes), 'triangles': len(triangles), 'vertices': len(vertices), 'bounds': [vertices.min(0).tolist(), vertices.max(0).tolist()], 'bytes': model.stat().st_size, 'sha256': hashlib.sha256(model.read_bytes()).hexdigest()}
(directory / 'geometry.json').write_text(json.dumps(facts, indent=2))
(directory / 'BadgeGemSurface.metal').write_bytes((ROOT / 'original/ScreenTime/Sources/App/Features/Badges/BadgeGemSurface.metal').read_bytes())
(directory / 'NOTES.txt').write_text('Widest band raised 0.22035 units, 15 percent of the 41 degree crown height, with table, culet, width and resting azimuth fixed.\nCrown height compressed proportionally; pavilion consequently steepens to about 43.2 degrees. Original three-hit shader.\n')
print(json.dumps(facts, indent=2))
