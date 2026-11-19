import bpy,json,shutil
from pathlib import Path
D=Path(__file__).resolve().parent;A=D/'05_combined';C=D/'06_balanced';C.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(A/'master.blend'));sc=bpy.data.scenes['Test plank master'];o=sc.objects['Lab Chest Lower Rim'];o.data=o.data.copy();m=o.data.materials[0].copy();m.name='Forged iron balanced surface character';o.data.materials[0]=m
for name in ['Lab Chest Rail Rivet 1 3','Lab Chest Rail Rivet 1 4']:sc.objects[name].data.materials[0]=m
m.node_tree.nodes['Reference guided shallow forge laps'].inputs['Strength'].default_value=.25
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True);a=json.loads((A/'design.json').read_text());a.update(mesh=o.data.name,material=m.name,large_lap_normal_strength=.25,source='05_combined');(C/'design.json').write_text(json.dumps(a,indent=2));shutil.copy2(A/'edge_geometry.npz',C/'edge_geometry.npz')
