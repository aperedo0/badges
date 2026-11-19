import bpy,json,hashlib,shutil
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate35'
assert bpy.data.filepath==str(R/'treasure_chest.blend') and not bpy.data.is_dirty and bpy.context.scene.frame_current==0
canonical_hash=hashlib.sha256((R/'treasure_chest.blend').read_bytes()).hexdigest();assert canonical_hash==hashlib.sha256((P/'candidate34/chest.blend').read_bytes()).hexdigest(),'Wrong baseline checkpoint'
exec(compile((P/'tools/hollow35_live.py').read_text(),'hollow35.py','exec'))
exec(compile((P/'tools/trim_interior35_live.py').read_text(),'trim_interior35.py','exec'))
exec(compile((P/'tools/check_hollow35_live.py').read_text(),'check_hollow35.py','exec'))
assert hashlib.sha256((R/'treasure_chest.blend').read_bytes()).hexdigest()==canonical_hash,'Premature save'
p=bpy.context.preferences.filepaths.save_version
try:
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(R/'treasure_chest.blend'),compress=True);shutil.copy2(R/'treasure_chest.blend',C/'chest.blend')
finally:bpy.context.preferences.filepaths.save_version=p
(C/'source').mkdir(exist_ok=True)
for name in ('hollow35_live.py','check_hollow35_live.py','build35_guarded_live.py','trim_interior35_live.py','cavity35_inventory_live.py'):shutil.copy2(P/'tools'/name,C/'source'/name)
print('Verified actual hollow interiors and preserved exterior, then saved35.')
