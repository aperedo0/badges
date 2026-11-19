import bpy,json,shutil
from pathlib import Path
D=Path(__file__).resolve().parent;A=D/'06_balanced';C=D/'07_integrated';C.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(A/'master.blend'));o=bpy.data.scenes['Test plank master'].objects['Lab Chest Lower Rim'];o.data=o.data.copy();m=o.data.materials[0].copy();o.data.materials[0]=m;m.name='Forged iron integrated surface';nt=m.node_tree
for name in ['Lab Chest Rail Rivet 1 3','Lab Chest Rail Rivet 1 4']:bpy.data.scenes['Test plank master'].objects[name].data.materials[0]=m
image=next(n for n in nt.nodes if n.type=='TEX_IMAGE' and Path(n.image.filepath).name=='exposed_lips.png');links=list(image.outputs['Color'].links);mul=nt.nodes.new('ShaderNodeMath');mul.name='Restrained legacy broad stroke wear';mul.operation='MULTIPLY';mul.inputs[1].default_value=.20;nt.links.new(image.outputs['Color'],mul.inputs[0])
for link in links:
 dest=link.to_socket;nt.links.remove(link);nt.links.new(mul.outputs[0],dest)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True);a=json.loads((A/'design.json').read_text());a.update(mesh=o.data.name,material=m.name,legacy_broad_stroke_wear=.20,source='06_balanced');(C/'design.json').write_text(json.dumps(a,indent=2));shutil.copy2(A/'edge_geometry.npz',C/'edge_geometry.npz')
