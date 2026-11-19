import bpy,numpy as np,json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;W=D.parent;P=W.parent;C=W/'V_lookdev_refinement'
code=(P/'verify_saved.py').read_text();ns=dict(bpy=bpy,np=np,json=json,hashlib=hashlib);exec(code[code.index('def manifest'):code.index('bpy.ops.wm.open_mainfile')],ns);manifest=ns['manifest']
def mesh_hash(o):
 m=o.data;out={}
 for label,collection,prop,dim,typ in [('vertices',m.vertices,'co',3,np.float32),('loop_vertices',m.loops,'vertex_index',1,np.int32),('face_starts',m.polygons,'loop_start',1,np.int32),('face_sizes',m.polygons,'loop_total',1,np.int32),('material_indices',m.polygons,'material_index',1,np.int32),('corner_normals',m.corner_normals,'vector',3,np.float32)]:
  a=np.empty(len(collection)*dim,dtype=typ);collection.foreach_get(prop,a);out[label]=hashlib.sha256(a.tobytes()).hexdigest()
 for uv in m.uv_layers:
  a=np.empty(len(uv.data)*2,dtype=np.float32);uv.data.foreach_get('uv',a);out['uv:'+uv.name]=hashlib.sha256(a.tobytes()).hexdigest()
 out['matrix']=[list(row) for row in o.matrix_world];out['parent']=o.parent.name if o.parent else None;return out
bpy.ops.wm.open_mainfile(filepath=str(D/'baseline_live.blend'));before=manifest(bpy.data.scenes['Chest Complete Form Phase 1']);sc=bpy.data.scenes['Test plank master'];baseline=mesh_hash(sc.objects['Master Chest Body Envelope']);other={o.name:mesh_hash(o) for o in sc.objects if o.type=='MESH' and o.name!='Master Chest Body Envelope'};other_materials={o.name:[m.name if m else None for m in o.data.materials] for o in sc.objects if o.type=='MESH' and o.name!='Master Chest Body Envelope'}
bpy.ops.wm.open_mainfile(filepath=str(C/'master.blend'));after=manifest(bpy.data.scenes['Chest Complete Form Phase 1']);assert before==after,'Original scene drift';sc=bpy.data.scenes['Test plank master'];body=sc.objects['Master Chest Body Envelope'];assert mesh_hash(body)==baseline,'Target geometry, normals or UV changed'
for name,sha in other.items():assert mesh_hash(sc.objects[name])==sha,name
for name,mats in other_materials.items():assert [m.name if m else None for m in sc.objects[name].data.materials]==mats,name
m=next(m for m in body.data.materials if m and m.name.startswith('Wood Lab V_'));assert all(n.image and n.image.packed_file for n in m.node_tree.nodes if n.type=='TEX_IMAGE')
assert sc.objects['First chest owner reference'] is bpy.data.scenes['Chest Complete Form Phase 1'].objects['First chest owner reference']
for rel,sha in json.loads((D/'source_fingerprints.json').read_text()).items():assert hashlib.sha256((W/'U_scan_fibers'/rel).read_bytes()).hexdigest()==sha,rel
proof=dict(original_complete_scene_geometry_materials_rig_and_transforms_preserved=True,test_plank_geometry_topology_corner_normals_uv_and_face_assignments_exact=True,other_parts_geometry_and_materials_exact=True,baseline_U_files_byte_identical=True,reference_shared_without_reimport=True,all_final_images_packed=True,normal_strength=m.node_tree.nodes['Single plank physical tangent normal'].inputs['Strength'].default_value,vertices=len(body.data.vertices),polygons=len(body.data.polygons),file_sha256=hashlib.sha256((C/'master.blend').read_bytes()).hexdigest(),scope='Fine normal texture, localized knot material and isolated review key light only')
(C/'saved_validation.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
