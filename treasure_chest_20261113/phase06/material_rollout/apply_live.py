import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase06/material_rollout');assert not bpy.app.is_job_running('RENDER');assert not bpy.data.is_dirty;assert Path(bpy.data.filepath)==D.parents[1]/'phase05/iron_character/14_edge_review/master.blend';v=json.loads((D/'validation.json').read_text());assert not v['uv_issues'];assert v['file_sha256']==hashlib.sha256((D/'master.blend').read_bytes()).hexdigest()
image_names=[a.spaces.active.image.name if a.spaces.active.image else None for w in bpy.context.window_manager.windows for a in w.screen.areas if a.type=='IMAGE_EDITOR'];bpy.ops.wm.open_mainfile(filepath=str(D/'master.blend'),load_ui=False);review=bpy.data.scenes['Full chest material evaluation'];original=bpy.data.scenes['Test plank master'];assert review.camera is not original.camera and review.camera.data is not original.camera.data;review.camera.data.type='ORTHO';review.camera.data.ortho_scale=8.5
parts=[o for o in review.objects if o.type=='MESH' and not o.hide_render and 'floor' not in o.name.lower()];bottom=min((o.matrix_world@Vector(q)).z for o in parts for q in o.bound_box)
for floor in [o for o in review.objects if o.type=='MESH' and 'floor' in o.name.lower()]:
 assert list(floor.users_scene)==[review];floor.location.z+=bottom-max((floor.matrix_world@Vector(q)).z for q in floor.bound_box)+.0005
nt=review.world.node_tree;assert review.world is not original.world
if not nt.nodes.get('Rollout camera background'):
 out=next(n for n in nt.nodes if n.type=='OUTPUT_WORLD' and n.is_active_output);source=out.inputs['Surface'].links[0].from_socket;path=nt.nodes.new('ShaderNodeLightPath');bg=nt.nodes.new('ShaderNodeBackground');bg.name='Rollout camera background';bg.inputs['Color'].default_value=(.009,.007,.009,1);mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(path.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(source,mix.inputs[1]);nt.links.new(bg.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface'])
i=0
for w in bpy.context.window_manager.windows:
 w.scene=review
 for a in w.screen.areas:
  if a.type=='IMAGE_EDITOR':
   old=image_names[i] if i<len(image_names) else None;i+=1
   if old and bpy.data.images.get(old):a.spaces.active.image=bpy.data.images[old]
  if a.type=='VIEW_3D':
   space=a.spaces.active;space.region_3d.view_perspective='CAMERA';space.region_3d.view_camera_offset=(0,0);space.region_3d.view_camera_zoom=0;space.shading.type='MATERIAL';space.shading.use_scene_lights=True;space.shading.use_scene_world=True
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_mainfile();(D/'live_validation.json').write_text(json.dumps(dict(file=bpy.data.filepath,dirty=bpy.data.is_dirty,active_scene=bpy.context.scene.name,complete_chest_framed=True,reference_editor_preserved=True,material_rollout_loaded=True,review_floor_and_camera_only_adjusted=True,file_sha256=hashlib.sha256((D/'master.blend').read_bytes()).hexdigest()),indent=2));print('Full chest rollout loaded and saved in Blender; original reference layout retained')
