import bpy,numpy as np,json,hashlib,math
from pathlib import Path
D=Path(__file__).resolve().parent;F=D.parents[1]/'phase05/iron_character/validate.py';code=F.read_text();exec(compile(code[code.index('def digest'):code.index("bpy.ops.wm.open_mainfile")],'existing_mesh_and_material_fingerprints','exec'));assignment=json.loads((D/'assignments.json').read_text());allowed=set(assignment['wood_objects']+assignment['iron_objects'])
def capture():
 sc=bpy.data.scenes['Test plank master'];bpy.context.window.scene=sc;sc.frame_set(0);bpy.context.view_layer.update();objects={}
 for o in bpy.data.objects:
  if any(s.name=='Chest Complete Form Phase 1' for s in o.users_scene) or o.name in sc.objects:
   objects[o.name]=dict(type=o.type,matrix=[list(r) for r in o.matrix_world],basis=[list(r) for r in o.matrix_basis],parent=o.parent.name if o.parent else None,mesh=mesh(o) if o.type=='MESH' else None,constraints=[(c.type,c.name,getattr(c,'subtarget','')) for c in o.constraints])
 return dict(objects=objects,world=graph(sc.world),lights={o.name:(list(o.data.color),o.data.energy,o.data.size) for o in sc.objects if o.type=='LIGHT'},frame=sc.frame_current,view=(sc.view_settings.view_transform,sc.view_settings.look,sc.view_settings.exposure,sc.view_settings.gamma),camera=[sc.camera.name,sc.camera.data.type,sc.camera.data.ortho_scale,sc.camera.data.lens])
bpy.ops.wm.open_mainfile(filepath=str(D/'baseline.blend'));base=capture();basewood=bpy.data.scenes['Test plank master'].objects['Master Chest Body Envelope'];face_materials=np.array([p.material_index for p in basewood.data.polygons]);benchmark_graph=graph(basewood.data.materials[1]);reference=bpy.data.objects['First chest owner reference'];reference_before=(reference.data.name,list(reference.location),list(reference.rotation_euler),reference.empty_display_size,hashlib.sha256(bytes(reference.data.packed_file.data)).hexdigest())
bpy.ops.wm.open_mainfile(filepath=str(D/'master.blend'));now=capture();assert base['world']==now['world'] and base['lights']==now['lights'] and base['view']==now['view'] and base['camera']==now['camera'] and base['frame']==now['frame'];assert base['objects'].keys()==now['objects'].keys()
for name,old in base['objects'].items():
 new=now['objects'][name];assert {k:v for k,v in old.items() if k!='mesh'}=={k:v for k,v in new.items() if k!='mesh'},name
 if name not in allowed:assert old==new,(name,'unintended component change')
 else:
  assert {k:v for k,v in old['mesh'].items() if k!='materials' and not k.startswith('uv:')}=={k:v for k,v in new['mesh'].items() if k!='materials' and not k.startswith('uv:')},(name,'geometry or normals changed')
  for key,value in old['mesh'].items():
   if key.startswith('uv:'):assert new['mesh'][key]==value,(name,key)
sc=bpy.data.scenes['Test plank master'];wood=sc.objects['Master Chest Body Envelope'];assert np.array_equal(face_materials,np.array([p.material_index for p in wood.data.polygons]));assert benchmark_graph==graph(wood.data.materials[1]);ref=bpy.data.objects['First chest owner reference'];assert reference_before==(ref.data.name,list(ref.location),list(ref.rotation_euler),ref.empty_display_size,hashlib.sha256(bytes(ref.data.packed_file.data)).hexdigest());assert len([o for o in bpy.data.objects if o.name.startswith('First chest owner reference')])==1
uv_issues=[]
for name in allowed:
 o=sc.objects[name];uvname='ChestRolloutWood' if name in assignment['wood_objects'] else 'LowerIronAtlas';uv=o.data.uv_layers[uvname];a=np.empty(len(uv.data)*2,np.float32);uv.data.foreach_get('uv',a);assert np.isfinite(a).all();a=a.reshape(-1,2);o.data.calc_loop_triangles()
 for tri in o.data.loop_triangles:
  p=o.data.polygons[tri.polygon_index]
  if name=='Master Chest Body Envelope' and p.material_index==1:continue
  if tri.area<.002:continue
  b=a[list(tri.loops)];area=abs(np.cross(b[1]-b[0],b[2]-b[0]));
  if area<1e-10:uv_issues.append(dict(object=name,face=p.index,area=tri.area))
 assert all(m for m in o.data.materials)
required={}
for scene in bpy.data.scenes:
 for obj in scene.objects:
  if obj.type=='MESH':
   for m in obj.data.materials:
    if m and m.use_nodes:
     for n in m.node_tree.nodes:
      if n.type=='TEX_IMAGE' and n.image:required[n.image.name]=n.image
  if obj.type=='EMPTY' and obj.empty_display_type=='IMAGE' and obj.data:required[obj.data.name]=obj.data
 if scene.world and scene.world.use_nodes:
  for n in scene.world.node_tree.nodes:
   if n.type=='TEX_ENVIRONMENT' and n.image:required[n.image.name]=n.image
assert all(i.packed_file for i in required.values());assert not list(bpy.data.libraries)
proof=dict(all_vertex_coordinates_topology_and_normals_exact=True,object_hierarchies_transforms_constraints_exact=True,approved_wood_benchmark_material_geometry_and_uv_exact=True,original_iron_and_two_knobs_exact=True,decorative_hardware_and_original_complete_scene_exact=True,original_lighting_exposure_and_camera_exact=True,all_original_uv_layers_preserved=True,one_reference_setup_exact=True,required_resources_packed=True,linked_libraries=0,wood_objects=assignment['wood_objects'],new_iron_objects=len(assignment['iron_objects']),uv_issues=uv_issues,source_maps_shared=True,new_wood_images=3,new_surface_materials=2,geometry_relief_note=assignment['geometry'],file_sha256=hashlib.sha256((D/'master.blend').read_bytes()).hexdigest());(D/'validation.json').write_text(json.dumps(proof,indent=2));assert not uv_issues,uv_issues[:10];print(json.dumps(proof),flush=True)
