from pathlib import Path
import bpy
R=Path('/Users/antonioperedo/Desktop/badges/botanical_match_20261014')
n={'__file__':str(R/'blender_workbench.py')}
exec((R.parent/'achievement_coins_refine_20261014/blender_workbench.py').read_text().split('LIVE=globals()')[0],n)
s=bpy.data.scenes['sunrise_matched'];bpy.context.window.scene=s
n['build_curved_borders'](s,'sunrise')
bpy.data.libraries.write(str(R/'sunrise/sunrise.blend'),{s},compress=True)
