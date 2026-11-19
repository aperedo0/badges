import bpy,numpy as np,shutil,json
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate37';sc=bpy.context.scene
assert bpy.data.filepath==str(C/'chest.blend') and sc.frame_current==0
assert 'CONSTRUCTION READY: yes' in (C/'construction_review.md').read_text()
v=np.load(C/'geometry.npz');rows=json.loads((C/'validation.json').read_text())['checks']
for i,row in enumerate(rows):
 ob=sc.objects[row['name']];a=np.array([v.co[:] for v in ob.data.vertices]);assert np.array_equal(np.c_[a[:,0],a[:,2],-a[:,1]],v[f'part{i}_v']),(ob.name,'unexpected unsaved geometry');assert np.max(abs(np.array(ob.matrix_world)-np.eye(4)))<1e-7
old=bpy.context.preferences.filepaths.save_version
try:
 bpy.context.preferences.filepaths.save_version=0
 source=(P/'tools/save_full_form_view_live.py').read_text().replace('candidate35','candidate37')
 exec(compile(source,'save_complete37','exec'))
 bpy.context.view_layer.update()
 if bpy.data.is_dirty:bpy.ops.wm.save_as_mainfile(filepath=str(R/'treasure_chest.blend'),compress=True);shutil.copy2(R/'treasure_chest.blend',C/'chest.blend')
finally:bpy.context.preferences.filepaths.save_version=old
for f in ('verify37_live.py','pose37_screen_live.py','rig37_negative_controls_live.py','render_seats37_live.py','promote37_live.py','pose36_gate.py'):shutil.copy2(P/'tools'/f,C/'source'/f)
print('Promoted reviewed37 to canonical treasure_chest.blend, complete scene at closed rest, older checkpoints preserved.')
