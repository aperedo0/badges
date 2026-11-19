import bpy,json,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase05/iron_fidelity');C=D/'N_charcoal_scale';checkpoint=json.loads((D/'checkpoint.json').read_text());asset=json.loads((C/'design.json').read_text());sc=bpy.data.scenes['Test plank master'];target=sc.objects['Lab Chest Lower Rim'];wood=sc.objects['Master Chest Body Envelope'];assert not bpy.app.is_job_running('RENDER')
def meshhash(obj):
 a=np.empty(len(obj.data.vertices)*3,np.float32);obj.data.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
assert meshhash(wood)==checkpoint['wood_geometry'];assert meshhash(target)==checkpoint['iron_geometry'],'Live iron changed after checkpoint'
assert (C/'iron_studio3_final.png').exists()
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'live_before_selection.blend'),compress=True,copy=True)
with bpy.data.libraries.load(str(C/'master.blend'),link=False) as (available,chosen):
 assert asset['mesh'] in available.meshes;chosen.meshes=[asset['mesh']]
target.data=chosen.meshes[0];target['iron_development']='Bottom reinforcement test only, awaiting owner review';assert target.data.library is None
users=bpy.data.user_map()
for lib in list(bpy.data.libraries):
 if Path(bpy.path.abspath(lib.filepath))==C/'master.blend':
  assert not users.get(lib) and not any(x.library==lib for x in users);bpy.data.libraries.remove(lib)
# Isolate reflection development from the approved wood scene and its original lighting.
review=bpy.data.scenes.new('Bottom iron reflection review');review.world=sc.world;review.render.engine='CYCLES';review.cycles.samples=64;review.cycles.use_denoising=True;review.cycles.device=sc.cycles.device
for prop in ['view_transform','look','exposure','gamma']:
 setattr(review.view_settings,prop,getattr(sc.view_settings,prop))
for obj in sc.objects:
 if obj.type in ['LIGHT','CAMERA'] or 'Development floor' in obj.name:
  clone=obj.copy();clone.data=obj.data.copy();clone.name='Iron review '+obj.name;clone['source_light']=obj.name;review.collection.objects.link(clone)
  if obj==sc.camera:review.camera=clone;clone.data.type='ORTHO';clone.data.ortho_scale=8.5
 else:review.collection.objects.link(obj)
floors=[o for o in review.objects if o.type=='MESH' and 'Development floor' in o.name]
bottoms=[(o.matrix_world@Vector(q)).z for o in review.objects if o.type=='MESH' and not o.hide_render and 'Development floor' not in o.name for q in o.bound_box]
for floor in floors:floor.location.z+=min(bottoms)-max((floor.matrix_world@Vector(q)).z for q in floor.bound_box)+.0005
exec(compile((D/'environment.py').read_text(),'isolated_reflection_environment','exec'));apply_environment(review,D,'studio3')
nt=review.world.node_tree;out=next(n for n in nt.nodes if n.type=='OUTPUT_WORLD');existing=out.inputs['Surface'].links[0].from_socket;bg=nt.nodes.new('ShaderNodeBackground');bg.inputs['Color'].default_value=(.006,.0045,.006,1);bg.inputs['Strength'].default_value=1;path=nt.nodes.new('ShaderNodeLightPath');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(path.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(existing,mix.inputs[1]);nt.links.new(bg.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface']);review.render.resolution_x=1400;review.render.resolution_y=1400;review.render.resolution_percentage=100
shown=False
for window in list(bpy.context.window_manager.windows)[1:]:
 for area in window.screen.areas:
  if area.type=='IMAGE_EDITOR':
   im=bpy.data.images.load(str(C/'iron_studio3_final.png'),check_existing=True);im.name='Bottom iron test review';im.use_view_as_render=False;im.pack();area.spaces.active.image=im;region=next(r for r in area.regions if r.type=='WINDOW')
   with bpy.context.temp_override(window=window,area=area,region=region):bpy.ops.image.view_all(fit_view=True)
   shown=True
assert shown,'Existing review image window unavailable'
asset['mesh']=target.data.name;asset['material']=target.data.materials[0].name;asset['review_scene']=review.name;(C/'design.json').write_text(json.dumps(asset,indent=2));assert meshhash(wood)==checkpoint['wood_geometry']
bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True)
proof=dict(file=bpy.data.filepath,target=target.name,wood_geometry_hash=meshhash(wood),iron_geometry_hash=meshhash(target),original_scene_lighting_preserved=True,review_scene=review.name,reference_preserved=True,review_image_shown=shown,only_target_mesh_material_swapped=True)
(C/'live_validation.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
