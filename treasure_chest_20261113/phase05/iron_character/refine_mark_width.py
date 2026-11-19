import bpy,json,shutil
from pathlib import Path
D=Path(__file__).resolve().parent;A=D/'09_surface_character';C=D/'10_defined_scale';C.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(A/'master.blend'));sc=bpy.data.scenes['Test plank master'];o=sc.objects['Lab Chest Lower Rim'];o.data=o.data.copy();m=o.data.materials[0].copy();m.name='Forged iron defined fractured scale';o.data.materials[0]=m
for name in ['Lab Chest Rail Rivet 1 3','Lab Chest Rail Rivet 1 4']:sc.objects[name].data.materials[0]=m
for name in ['mark_height16.png','exposed.png']:
 node=m.node_tree.nodes['Character '+name];im=bpy.data.images.load(str(D/'layers'/name),check_existing=False);im.colorspace_settings.name='Non-Color';im.pack();node.image=im
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True);a=json.loads((A/'design.json').read_text());a.update(mesh=o.data.name,material=m.name,source='09_surface_character',sharper_marking_shapes_only=True);(C/'design.json').write_text(json.dumps(a,indent=2));shutil.copy2(A/'edge_geometry.npz',C/'edge_geometry.npz')
