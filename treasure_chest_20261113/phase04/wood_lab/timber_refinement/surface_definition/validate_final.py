import bpy,numpy as np,json,hashlib,sys
from pathlib import Path
D=Path(__file__).resolve().parent;W=D.parent;P=W.parent;KEY=sys.argv[sys.argv.index('--')+1];C=W/KEY
code=(P/'verify_saved.py').read_text();ns=dict(bpy=bpy,np=np,json=json,hashlib=hashlib);exec(code[code.index('def manifest'):code.index('bpy.ops.wm.open_mainfile')],ns);manifest=ns['manifest']
def mesh_hash(o):
 m=o.data;out={}
 for label,collection,prop,dim,typ in [('vertices',m.vertices,'co',3,np.float32),('loop_vertices',m.loops,'vertex_index',1,np.int32),('face_starts',m.polygons,'loop_start',1,np.int32),('face_sizes',m.polygons,'loop_total',1,np.int32),('material_indices',m.polygons,'material_index',1,np.int32),('corner_normals',m.corner_normals,'vector',3,np.float32)]:
  a=np.empty(len(collection)*dim,dtype=typ);collection.foreach_get(prop,a);out[label]=hashlib.sha256(a.tobytes()).hexdigest()
 for uv in m.uv_layers:
  a=np.empty(len(uv.data)*2,dtype=np.float32);uv.data.foreach_get('uv',a);out['uv:'+uv.name]=hashlib.sha256(a.tobytes()).hexdigest()
 out['matrix']=[list(row) for row in o.matrix_world];out['parent']=o.parent.name if o.parent else None;return out
bpy.ops.wm.open_mainfile(filepath=str(D/'live_before_selection.blend'));before=manifest(bpy.data.scenes['Chest Complete Form Phase 1']);sc=bpy.data.scenes['Test plank master'];baseline=mesh_hash(sc.objects['Master Chest Body Envelope']);n=len(bpy.data.scenes['Chest Complete Form Phase 1'].objects['Chest Body Envelope'].data.vertices);boundary=np.array([tuple(v.co) for v in sc.objects['Master Chest Body Envelope'].data.vertices[:n]],np.float32);others={o.name:(mesh_hash(o),[m.name if m else None for m in o.data.materials]) for o in sc.objects if o.type=='MESH' and o.name!='Master Chest Body Envelope'}
bpy.ops.wm.open_mainfile(filepath=str(C/'master.blend'));after=manifest(bpy.data.scenes['Chest Complete Form Phase 1']);assert before==after,'Original scene drift';sc=bpy.data.scenes['Test plank master'];body=sc.objects['Master Chest Body Envelope'];current=mesh_hash(body)
for key,value in baseline.items():
 if key not in ['vertices','corner_normals']:assert current[key]==value,key
assert np.array_equal(boundary,np.array([tuple(v.co) for v in body.data.vertices[:n]],np.float32))
for name,(sha,mats) in others.items():assert mesh_hash(sc.objects[name])==sha and [m.name if m else None for m in sc.objects[name].data.materials]==mats,name
m=next(m for m in body.data.materials if m and m.name.startswith('Wood Lab '));assert all(n.image and n.image.packed_file for n in m.node_tree.nodes if n.type=='TEX_IMAGE');assert sc.objects['First chest owner reference'] is bpy.data.scenes['Chest Complete Form Phase 1'].objects['First chest owner reference'];indices=np.empty(len(body.data.loops),dtype=np.int32);body.data.loops.foreach_get('edge_index',indices);assert np.all(np.bincount(indices,minlength=len(body.data.edges))==2)
checkpoint=json.loads((D/'checkpoint.json').read_text());assert hashlib.sha256(Path(checkpoint['source']).read_bytes()).hexdigest()==checkpoint['source_file_sha256']
proof=dict(original_complete_scene_geometry_materials_transforms_parent_and_action_names_preserved=True,target_topology_uv_material_assignments_transform_parent_preserved=True,target_original_boundary_vertices_exact=True,other_parts_geometry_normals_uv_material_assignments_exact=True,source_AE_checkpoint_byte_identical=True,reference_shared_without_reimport=True,closed_two_faces_per_edge=True,all_final_maps_packed=True,normal_strength=m.node_tree.nodes['Single plank physical tangent normal'].inputs['Strength'].default_value,vertices=len(body.data.vertices),polygons=len(body.data.polygons),file_sha256=hashlib.sha256((C/'master.blend').read_bytes()).hexdigest(),scope='Existing test plank relief and independent maps plus isolated comparison lighting')
(C/'saved_validation.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
