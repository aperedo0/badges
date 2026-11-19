import bpy,json,time,hashlib,shutil
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate34'
s=json.loads((R/'schedule.json').read_text());assert s['status']=='active' and s['phase']=='work' and time.time()+210<s['work_until_epoch']
assert bpy.data.filepath==str(R/'treasure_chest.blend') and not bpy.data.is_dirty
canonical_hash=hashlib.sha256((R/'treasure_chest.blend').read_bytes()).hexdigest()
prev=bpy.context.preferences.filepaths.save_version;DEFER_CHEST_SAVE=True
try:
 bpy.context.preferences.filepaths.save_version=0
 exec(compile((P/'tools/direct_layout34_live.py').read_text(),'direct_layout34.py','exec'))
 exec(compile((P/'tools/full_form_check_live.py').read_text(),'full_check34.py','exec'))
 exec(compile((P/'tools/check_layout34_live.py').read_text(),'rigid_check34.py','exec'))
 assert hashlib.sha256((R/'treasure_chest.blend').read_bytes()).hexdigest()==canonical_hash,'A nested helper saved before validation'
 DEFER_CHEST_SAVE=False
 bpy.ops.wm.save_as_mainfile(filepath=str(R/'treasure_chest.blend'),compress=True);shutil.copy2(R/'treasure_chest.blend',C/'chest.blend')
 (C/'source').mkdir(exist_ok=True)
 for p in (P/'tools').glob('*.py'):shutil.copy2(p,C/'source'/p.name)
finally:
 DEFER_CHEST_SAVE=False;bpy.context.preferences.filepaths.save_version=prev
print('Validated rigid fit and original file preservation before saving34.')
