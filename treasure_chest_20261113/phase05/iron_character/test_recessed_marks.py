import bpy,json,shutil
from pathlib import Path
D=Path(__file__).resolve().parent;A=D/'11_restored_pigment';C=D/'13_recessed_scale';C.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(A/'master.blend'));sc=bpy.data.scenes['Test plank master'];obj=sc.objects['Lab Chest Lower Rim'];obj.data=obj.data.copy();m=obj.data.materials[0].copy();m.name='Forged iron shallow recessed scale boundaries';obj.data.materials[0]=m
for name in ['Lab Chest Rail Rivet 1 3','Lab Chest Rail Rivet 1 4']:sc.objects[name].data.materials[0]=m
m.node_tree.nodes['Independent shallow fractured scale markings'].invert=True
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True);a=json.loads((A/'design.json').read_text());a.update(mesh=obj.data.name,material=m.name,source='11_restored_pigment',only_new_marking_relief_direction_changed=True);(C/'design.json').write_text(json.dumps(a,indent=2));shutil.copy2(A/'edge_geometry.npz',C/'edge_geometry.npz')
