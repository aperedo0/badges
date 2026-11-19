import bpy,json
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab/timber_refinement/grain_hierarchy')
for KEY in ['Q_layers_soft','R_layers_full']:
 bpy.ops.wm.open_mainfile(filepath=json.loads((D/'comparison_geometry.json').read_text())['checkpoint'])
 exec(compile((D/'apply_layers.py').read_text(),'apply_layers','exec'))
 exec(compile((D/'render_fixed.py').read_text(),'render_fixed','exec'))
