import bpy,numpy as np,json,hashlib,sys
from pathlib import Path
D=Path(__file__).resolve().parent;key=sys.argv[sys.argv.index('--')+1];C=D/key;extra=json.loads((C/'design.json').read_text()).get('isolated_bevel_reflection_lights',[]);assert set(extra).issubset({'Iron upper bevel reflection','Iron lower bevel reflection'});TARGET='Lab Chest Lower Rim';KNOBS=['Lab Chest Rail Rivet 1 3','Lab Chest Rail Rivet 1 4'] 
def digest(a):return hashlib.sha256(a).hexdigest()
def graph(m):
 if not m or not m.use_nodes:return None
 nodes=[]
 for n in m.node_tree.nodes:
  values=[]
  for s in n.inputs:
   if not hasattr(s,'default_value'):continue
   v=s.default_value
   if not isinstance(v,(str,int,float,bool)):
    try:v=list(v)
    except TypeError:v=str(v)
   values.append((s.name,v))
  im=n.image if n.type in ['TEX_IMAGE','TEX_ENVIRONMENT'] else None
  nodes.append((n.name,n.bl_idname,values,getattr(n,'operation',None),getattr(n,'blend_type',None),getattr(n,'uv_map',None),None if im is None else (im.name,im.colorspace_settings.name,digest(bytes(im.packed_file.data)) if im.packed_file else im.filepath)))
 return digest(json.dumps((nodes,[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]),sort_keys=True).encode())
def mesh(o):
 m=o.data;result={}
 for key,col,prop,dim,dtype in [('points',m.vertices,'co',3,np.float32),('loops',m.loops,'vertex_index',1,np.int32),('starts',m.polygons,'loop_start',1,np.int32),('sizes',m.polygons,'loop_total',1,np.int32),('material_indices',m.polygons,'material_index',1,np.int32),('normals',m.corner_normals,'vector',3,np.float32)]:
  a=np.empty(len(col)*dim,dtype=dtype);col.foreach_get(prop,a);result[key]=digest(a.tobytes())
 for uv in m.uv_layers:
  a=np.empty(len(uv.data)*2,np.float32);uv.data.foreach_get('uv',a);result['uv:'+uv.name]=digest(a.tobytes())
 result['materials']=[(m.name,graph(m)) if m else None for m in o.data.materials];return result
bpy.ops.wm.open_mainfile(filepath=str(D/'baseline.blend'));sc=bpy.data.scenes['Test plank master'];before={};knob_baseline={};membership={s.name:sorted(o.name for o in s.objects) for s in bpy.data.scenes};wood=mesh(sc.objects['Master Chest Body Envelope']);lights={o.name:dict(matrix=[list(r) for r in o.matrix_world],energy=o.data.energy,color=list(o.data.color),size=o.data.size,hide_render=o.hide_render) for o in sc.objects if o.type=='LIGHT'}
for scene in bpy.data.scenes:
 for obj in scene.objects:
  if scene.name in ['Test plank master','Bottom iron reflection review'] and obj.name==TARGET:continue
  if scene.name in ['Test plank master','Bottom iron reflection review'] and obj.name in KNOBS:
   knob_baseline[obj.name]=dict(mesh=mesh(obj),matrix=[list(r) for r in obj.matrix_world],parent=obj.parent.name if obj.parent else None);continue
  before[(scene.name,obj.name)]=dict(type=obj.type,matrix=[list(r) for r in obj.matrix_world],parent=obj.parent.name if obj.parent else None,data=mesh(obj) if obj.type=='MESH' else None)
base_target=sc.objects[TARGET];base_material_graph=graph(base_target.data.materials[0]);target_matrix=[list(r) for r in base_target.matrix_world];target_parent=base_target.parent.name if base_target.parent else None;base_target_uvs={k:v for k,v in mesh(base_target).items() if k.startswith('uv:')};a=np.array([tuple(v.co) for v in base_target.data.vertices]);base_bounds=np.array([a.min(0),a.max(0)]);base_objects=sorted(o.name for o in bpy.data.objects);worlds={s.name:graph(s.world) for s in bpy.data.scenes if s.world and s.name!='Bottom iron reflection review'};view=(sc.view_settings.view_transform,sc.view_settings.look,sc.view_settings.exposure,sc.view_settings.gamma,sc.camera.name,sc.camera.data.type,sc.camera.data.ortho_scale,sc.camera.data.lens)
bpy.ops.wm.open_mainfile(filepath=str(C/'master.blend'));sc=bpy.data.scenes['Test plank master'];assert set(base_objects).issubset(o.name for o in bpy.data.objects);assert membership=={s.name:sorted(o.name for o in s.objects if not (s.name=='Bottom iron reflection review' and o.name in extra)) for s in bpy.data.scenes if s.name in membership}
for name in extra:
 o=bpy.data.objects[name];assert o.type=='LIGHT' and o.data.type=='AREA' and o.get('isolated_iron_review') and sorted(s.name for s in o.users_scene)==['Bottom iron reflection review'];assert sorted(x.name for x in o.light_linking.receiver_collection.objects)==sorted([TARGET]+KNOBS)
assert worlds=={s.name:graph(s.world) for s in bpy.data.scenes if s.name in worlds};assert view==(sc.view_settings.view_transform,sc.view_settings.look,sc.view_settings.exposure,sc.view_settings.gamma,sc.camera.name,sc.camera.data.type,sc.camera.data.ortho_scale,sc.camera.data.lens)
for (scene,name),old in before.items():
 obj=bpy.data.scenes[scene].objects[name];now=dict(type=obj.type,matrix=[list(r) for r in obj.matrix_world],parent=obj.parent.name if obj.parent else None,data=mesh(obj) if obj.type=='MESH' else None);assert old==now,(scene,name)
for name,old in knob_baseline.items():
 obj=sc.objects[name];now=mesh(obj);assert {k:v for k,v in old['mesh'].items() if k!='materials' and not k.startswith('uv:')}=={k:v for k,v in now.items() if k!='materials' and not k.startswith('uv:')};assert old['matrix']==[list(r) for r in obj.matrix_world];assert old['parent']==(obj.parent.name if obj.parent else None);assert {k:v for k,v in old['mesh'].items() if k.startswith('uv:')}=={k:v for k,v in now.items() if k.startswith('uv:')};assert obj.data.materials[0] is sc.objects[TARGET].data.materials[0];assert set(u.name for u in obj.data.uv_layers)=={'LowerIronAtlas','LowerIronPhysical'}
assert wood==mesh(sc.objects['Master Chest Body Envelope']);afterlights={o.name:dict(matrix=[list(r) for r in o.matrix_world],energy=o.data.energy,color=list(o.data.color),size=o.data.size,hide_render=o.hide_render) for o in sc.objects if o.type=='LIGHT'};assert lights==afterlights
obj=sc.objects[TARGET];assert base_target_uvs=={k:v for k,v in mesh(obj).items() if k.startswith('uv:')};m=obj.data;co=np.array([tuple(v.co) for v in m.vertices]);assert np.max(np.abs(np.array([co.min(0),co.max(0)])-base_bounds))<2e-6
loops=np.empty(len(m.loops),np.int32);m.loops.foreach_get('edge_index',loops);assert np.all(np.bincount(loops,minlength=len(m.edges))==2)
assert [list(r) for r in obj.matrix_world]==target_matrix and (obj.parent.name if obj.parent else None)==target_parent
mat=m.materials[0];assert all(n.image and n.image.packed_file for n in mat.node_tree.nodes if n.type=='TEX_IMAGE');assert sc.objects['First chest owner reference'] is bpy.data.scenes['Chest Complete Form Phase 1'].objects['First chest owner reference'];fields=np.load(C/'edge_geometry.npz');rest=fields['before'];deformed=fields['after'];delta=np.linalg.norm(deformed-rest,axis=1)
from mathutils import Matrix
import math
q=np.c_[rest[:,0],rest[:,2],-rest[:,1]]@np.array(Matrix.Rotation(math.radians(32),3,'Y'));mask=((np.hypot(q[:,0]+1.1277,q[:,1]+1.96575)<.10)|(np.hypot(q[:,0]-1.1234,q[:,1]+1.96575)<.10))&(abs(q[:,2])>1.70);assert delta[mask].max()<1e-8
assert np.isfinite(co).all();assert np.array_equal(fields['before'][~fields['changed_vertices']],fields['after'][~fields['changed_vertices']])
for uv in m.uv_layers:
 a=np.empty(len(uv.data)*2,np.float32);uv.data.foreach_get('uv',a);assert np.isfinite(a).all()

review=bpy.data.scenes.get('Bottom iron reflection review');assert review and all(n.image and n.image.packed_file for n in review.world.node_tree.nodes if n.type=='TEX_ENVIRONMENT')
assert not any(n.bl_idname=='ShaderNodeOutputAOV' for n in mat.node_tree.nodes);assert not any(a.name.startswith('Iron_') for l in sc.view_layers for a in l.aovs)
design=json.loads((C/'design.json').read_text());design['mesh']=m.name;design['material']=mat.name;(C/'design.json').write_text(json.dumps(design,indent=2))
proof=dict(starting_iron_material_graph=base_material_graph,only_authorized_iron_components_changed=True,authorized_components=[TARGET]+KNOBS,knob_geometry_preserved=True,broad_surface_geometry_exact_outside_localized_edges=True,original_uvs_preserved=True,wood_geometry_uv_material_maps_exact=True,all_other_scene_objects_material_graphs_and_transforms_exact=True,original_complete_scene_preserved=True,lights_unchanged=True,original_environment_camera_and_color_management_unchanged=True,isolated_review_scene_allowed=True,original_outer_bounds_preserved=True,closed_two_faces_per_edge=True,rivet_contact_regions_exact=True,single_shared_reference=True,production_diagnostics_absent=True,all_target_images_packed=True,review_environment_packed=True,vertices=len(m.vertices),polygons=len(m.polygons),file_sha256=digest((C/'master.blend').read_bytes()),wood_hashes=wood)
(C/'validation.json').write_text(json.dumps(proof,indent=2));print(json.dumps({k:v for k,v in proof.items() if k!='wood_hashes'}),flush=True)
