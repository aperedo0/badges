import bpy,json,hashlib,shutil
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate36'
assert bpy.data.filepath==str(R/'treasure_chest.blend') and not bpy.data.is_dirty and bpy.context.scene.frame_current==0
oldsha=hashlib.sha256((R/'treasure_chest.blend').read_bytes()).digest();assert oldsha==hashlib.sha256((P/'candidate35/chest.blend').read_bytes()).digest(),'Wrong current baseline'
exec(compile((P/'tools/frame36_live.py').read_text(),'frame36.py','exec'))
exec(compile((P/'tools/check_frame36_live.py').read_text(),'check_frame36.py','exec'))
assert hashlib.sha256((R/'treasure_chest.blend').read_bytes()).digest()==oldsha,'Premature save'
p=bpy.context.preferences.filepaths.save_version
try:
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'chest.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=p
(C/'source').mkdir(exist_ok=True)
for name in ('frame36_geometry.py','frame36_live.py','check_frame36_live.py','build36_guarded_live.py'):shutil.copy2(P/'tools'/name,C/'source'/name)
assert hashlib.sha256((R/'treasure_chest.blend').read_bytes()).digest()==oldsha
print('Saved candidate36 for required visual comparison. Canonical35 remains unchanged until visual approval.')
