import bpy,json,numpy as np,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;choice=json.loads((D/'selection.json').read_text());C=D/choice['candidate'];expected=json.loads((C/'live_validation.json').read_text());F=D.parent/'iron_fidelity';text=(F/'validate.py').read_text();exec(compile(text[text.index('def digest'):text.index('def mesh')],'existing_material_graph_hash','exec'));bpy.ops.wm.open_mainfile(filepath=str(C/'master.blend'));sc=bpy.data.scenes['Test plank master']
def mh(o):
 a=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
assert not any(n.bl_idname=='ShaderNodeOutputAOV' for n in sc.objects['Lab Chest Lower Rim'].data.materials[0].node_tree.nodes);assert not any(a.name.startswith('Iron_') for l in sc.view_layers for a in l.aovs);assert mh(sc.objects['Lab Chest Lower Rim'])==expected['iron_geometry'];assert mh(sc.objects['Master Chest Body Envelope'])==expected['wood_geometry'];assert graph(sc.objects['Lab Chest Lower Rim'].data.materials[0])==expected['material_graph'];required={}
if expected.get('shallow_scale_marks_inverted'):
 assert sc.objects['Lab Chest Lower Rim'].data.materials[0].node_tree.nodes['Independent shallow fractured scale markings'].invert
design=json.loads((C/'design.json').read_text())
for params in design.get('review_reflection_settings',[]):
 light=bpy.data.scenes['Bottom iron reflection review'].objects[params['name']];assert params['name'] not in sc.objects;assert abs(light.data.energy-params['power'])<1e-5;assert max(abs(a-b) for a,b in zip(light.location,params['position']))<1e-5;assert max(abs(a-b) for a,b in zip(light.rotation_euler,params['rotation']))<1e-5;assert abs(light.data.size-params['size'])<1e-5 and abs(light.data.size_y-params['size_y'])<1e-5
for scene in bpy.data.scenes:
 for obj in scene.objects:
  if obj.type=='MESH':
   for mat in obj.data.materials:
    if mat and mat.use_nodes:
     for node in mat.node_tree.nodes:
      if node.type=='TEX_IMAGE' and node.image:required[node.image.name]=node.image
  if obj.type=='EMPTY' and obj.empty_display_type=='IMAGE' and obj.data:required[obj.data.name]=obj.data
 if scene.world and scene.world.use_nodes:
  for node in scene.world.node_tree.nodes:
   if node.type=='TEX_ENVIRONMENT' and node.image:required[node.image.name]=node.image
assert all(im.packed_file for im in required.values());assert not list(bpy.data.libraries);assert len([o for o in bpy.data.objects if o.name.startswith('First chest owner reference')])==1;h=hashlib.sha256((C/'master.blend').read_bytes()).hexdigest();assert h==expected['file_sha256'];proof=dict(fresh_final_restore=True,production_diagnostics_absent=True,geometry_and_material_match_live=True,all_required_resources_packed=True,shared_reference_preserved=True,no_linked_libraries=True,file_sha256=h,required_images=sorted(required));(C/'restore_validation.json').write_text(json.dumps(proof,indent=2));print(json.dumps({k:v for k,v in proof.items() if k!='required_images'}))
