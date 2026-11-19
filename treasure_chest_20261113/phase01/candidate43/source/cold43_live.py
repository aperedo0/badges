import bpy,json,math
from pathlib import Path
import numpy as np
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');C=R/'phase01/candidate43';path=C/'chest.blend'
assert bpy.data.filepath==str(path) and not bpy.data.is_dirty,'Unexpected file or unknown unsaved changes'
pref=bpy.context.preferences.filepaths.use_scripts_auto_execute;bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);sc=bpy.context.scene;sc.frame_set(250);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();dg.update();master=sc.objects['Chest Rig Master'];lid=sc.objects['Chest Rig LidOpen'];drivers=[]
for owner in list(bpy.data.objects)+list(bpy.data.shape_keys):
 if owner.animation_data:
  for fc in owner.animation_data.drivers:drivers.append(dict(owner=owner.name,path=fc.data_path,simple=fc.driver.is_simple_expression,valid=fc.driver.is_valid))
angle=float(lid.evaluated_get(dg).rotation_axis_angle[0]);report=dict(use_scripts=False,autoexec_fail=bpy.app.autoexec_fail,autoexec_message=bpy.app.autoexec_fail_message,security_preference_unchanged=pref==bpy.context.preferences.filepaths.use_scripts_auto_execute,drivers=drivers,observed_lid_degrees=float(master['lid_degrees']),observed_lid_rotation_radians=angle,complete_badge=False)
assert not report['autoexec_fail'] and report['security_preference_unchanged'];assert len(drivers)==15 and all(d['simple'] and d['valid'] for d in drivers);assert abs(report['observed_lid_degrees']-95)<1e-5 and abs(angle+math.radians(95))<1e-6
sc.frame_set(0);bpy.context.view_layer.update();assert abs(master['lid_degrees'])<1e-6
for o in sc.objects:
 if o.type=='MESH' and o.get('full_form'):assert np.max(abs(np.array(o.matrix_world)-np.eye(4)))<1e-7,(o.name,'not closed rest')
report['restored_frame']=0;(C/'safe_cold_load_proof.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='drivers'}))
