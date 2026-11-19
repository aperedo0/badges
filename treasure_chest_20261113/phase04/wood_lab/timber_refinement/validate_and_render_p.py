import bpy,numpy as np,json,hashlib,time
from pathlib import Path
W=Path(__file__).resolve().parent;P=W.parent
chosen=W/'P_physical_fractures/master.blend'
ns=dict(bpy=bpy,np=np,json=json,hashlib=hashlib)
code=(P/'verify_saved.py').read_text();exec(code[code.index('def manifest'):code.index('bpy.ops.wm.open_mainfile')],ns)
manifest=ns['manifest']
bpy.ops.wm.open_mainfile(filepath=str(W/'baseline.blend'))
baseline=manifest(bpy.data.scenes['Chest Complete Form Phase 1'])
bpy.ops.wm.open_mainfile(filepath=str(W/'owner_window_checkpoint.blend'))
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
code=(P/'render_batch.py').read_text().split('jobs=')[0].replace("sc=bpy.data.scenes['Wood surface comparison']","sc=bpy.data.scenes['Test plank master']")
exec(compile(code,'reused_render_setup','exec'))
folder=chosen.parent
slot=list(mesh.materials).index(material)
clay=material.copy();clay.name='Temporary geometry diagnostic clay';bs=clay.node_tree.nodes['Principled BSDF']
for socket in ['Base Color','Roughness','Normal']:
    for link in list(bs.inputs[socket].links):clay.node_tree.links.remove(link)
bs.inputs['Base Color'].default_value=(.28,.28,.28,1);bs.inputs['Roughness'].default_value=.76
done=[]
for name,light,view,isclay in [('neutral_close','neutral','close',False),('clay_graze','graze','close',True),('cinema_full','cinema','full',False)]:
    mesh.materials[slot]=clay if isclay else material
    lighting(light);frame(view)
    sc.render.resolution_x=1200;sc.render.resolution_y=1200 if view=='full' else 888;sc.render.resolution_percentage=100;sc.cycles.samples=64
    sc.render.filepath=str(folder/(name+'.png'));start=time.time();bpy.ops.render.render(write_still=True)
    done.append(dict(image=name,seconds=round(time.time()-start,1)));(folder/'final_progress.json').write_text(json.dumps(done,indent=2));print('FINAL',done[-1],flush=True)
mesh.materials[slot]=material
