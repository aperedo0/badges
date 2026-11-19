import bpy,numpy as np,json,hashlib,time
from pathlib import Path
D=Path(__file__).resolve().parent;W=D.parent;P=W.parent
import sys
chosen=W/sys.argv[sys.argv.index('--')+1]/'master.blend'
ns=dict(bpy=bpy,np=np,json=json,hashlib=hashlib)
code=(P/'verify_saved.py').read_text();exec(code[code.index('def manifest'):code.index('bpy.ops.wm.open_mainfile')],ns)
manifest=ns['manifest']
bpy.ops.wm.open_mainfile(filepath=str(W/'baseline.blend'))
baseline=manifest(bpy.data.scenes['Chest Complete Form Phase 1'])
bpy.ops.wm.open_mainfile(filepath=str(W/'R_layers_full/master.blend'))
owner=manifest(bpy.data.scenes['Chest Complete Form Phase 1'])
assert owner==baseline,'Owner source changes must be preserved before promoting the candidate'
bpy.ops.wm.open_mainfile(filepath=str(chosen))
current=manifest(bpy.data.scenes['Chest Complete Form Phase 1'])
assert current==baseline,'Original source scene drift'
sc=bpy.data.scenes['Test plank master'];body=sc.objects['Master Chest Body Envelope'];mesh=body.data
indices=np.empty(len(mesh.loops),dtype=np.int32);mesh.loops.foreach_get('edge_index',indices);counts=np.bincount(indices,minlength=len(mesh.edges));assert np.all(counts==2)
material=next(m for m in mesh.materials if m and m.name.startswith('Wood Lab '))
assert all(n.image and n.image.packed_file for n in material.node_tree.nodes if n.type=='TEX_IMAGE')
assert sc.objects['First chest owner reference'] is bpy.data.scenes['Chest Complete Form Phase 1'].objects['First chest owner reference']
proof=dict(original_geometry_materials_transforms_parents_and_action_names_preserved=True,owner_checkpoint_source_matches=True,reference_shared_without_reimport=True,watertight=True,all_material_images_packed=True,vertices=len(mesh.vertices),polygons=len(mesh.polygons),file_sha256=hashlib.sha256(chosen.read_bytes()).hexdigest())
(chosen.parent/'saved_validation.json').write_text(json.dumps(proof,indent=2))

print(json.dumps(proof),flush=True)
