import bpy,json,math,time
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');S=R/'phase03/stylized_wood45';C=S/'candidate04';D=json.loads((C/'design.json').read_text());sc=bpy.context.scene;assert sc.frame_current==0 and bpy.data.filepath==str(C/'chest.blend')
cam=sc.camera;camera=cam.matrix_world.copy();props=(cam.data.type,cam.data.ortho_scale,cam.data.lens,sc.render.resolution_x,sc.render.resolution_y,sc.cycles.samples,sc.render.filepath);lights={o.name:(o.matrix_world.copy(),o.data.energy,tuple(o.data.color)) for o in sc.objects if o.type=='LIGHT'};floor=sc.objects['Development floor'];floorstate=floor.hide_render;mat=bpy.data.materials[D['material']];normal=mat.node_tree.nodes['Single plank physical tangent normal'];strength=normal.inputs['Strength'].default_value;yaw=Matrix.Rotation(math.radians(32),3,'Y');done=[];seconds=[]
def world(q):p=yaw@Vector(q);return Vector((p.x,-p.z,p.y))
# True Blender camera renders under the existing development studio.
jobs=[('front','whole',0),('plank_close','plank',0),('grain_close','grain',0),('grain_flat_normal_control','flat',0),('warm_front','whole',0),('warm_plank','plank',0),('warm_grain','grain',0),('turn08','turn',8),('turn12','turn',12),('turn16','turn',16),('turn45','turn',45),('grain_opposed_key','opposed',0)]
try:
 for name,mode,value in jobs:
  for n,(M,energy,color) in lights.items():sc.objects[n].matrix_world=M;sc.objects[n].data.energy=energy;sc.objects[n].data.color=color
  if name.startswith('warm_'):
   for ln,lc,le in [('Chest Development Key',(1,.62,.34),1100),('Chest Development Fill',(.84,.90,1),350),('Chest Development Rear',(1,.50,.22),900)]:sc.objects[ln].data.color=lc;sc.objects[ln].data.energy=le
  cam.matrix_world=camera;cam.data.type=props[0];cam.data.ortho_scale=props[1];cam.data.lens=props[2];sc.render.resolution_x=sc.render.resolution_y=1100;sc.cycles.samples=32;floor.hide_render=floorstate;normal.inputs['Strength'].default_value=strength
  if mode=='turn':
   turn=Matrix.Rotation(math.radians(value),4,'Z');cam.matrix_world=turn@camera
   for n,(M,energy,color) in lights.items():sc.objects[n].matrix_world=turn@M
  elif mode!='whole':
   target=world((-.05,-1.35,1.60) if mode=='plank' else (-1.18,-1.38,1.60));forward=camera.to_quaternion()@Vector((0,0,-1));cam.location=target-forward*12;cam.rotation_euler=camera.to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=5.6 if mode=='plank' else 2.2;sc.render.resolution_x=1400 if mode=='plank' else 1100;sc.render.resolution_y=650 if mode=='plank' else 800;sc.cycles.samples=48
   if mode=='flat':normal.inputs['Strength'].default_value=0
   if mode=='opposed':
    key=sc.objects['Chest Development Key'];key.location.x=-key.location.x;key.rotation_euler=(-key.location).to_track_quat('-Z','Y').to_euler()
  sc.render.filepath=str(C/(name+'.png'));start=time.time();bpy.ops.render.render(write_still=True);seconds.append(time.time()-start);done.append(name);(C/'render_progress.json').write_text(json.dumps(dict(completed=done,seconds=seconds),indent=2))
finally:
 normal.inputs['Strength'].default_value=strength;cam.matrix_world=camera;cam.data.type,cam.data.ortho_scale,cam.data.lens,sc.render.resolution_x,sc.render.resolution_y,sc.cycles.samples,sc.render.filepath=props;floor.hide_render=floorstate
 for n,(M,energy,color) in lights.items():sc.objects[n].matrix_world=M;sc.objects[n].data.energy=energy;sc.objects[n].data.color=color
 bpy.context.view_layer.update()
 proof=dict(camera_restored=all(abs(a-b)<1e-6 for ar,br in zip(cam.matrix_world,camera) for a,b in zip(ar,br)),lights_restored=all(all(abs(a-b)<1e-6 for a,b in zip(sc.objects[n].data.color,color)) and sc.objects[n].data.energy==energy and all(abs(a-b)<1e-6 for ar,br in zip(sc.objects[n].matrix_world,M) for a,b in zip(ar,br)) for n,(M,energy,color) in lights.items()),normal_restored=normal.inputs['Strength'].default_value==strength,floor_restored=floor.hide_render==floorstate)
 assert all(proof.values()),proof
 (C/'render_state_proof.json').write_text(json.dumps(proof,indent=2))
print(json.dumps(dict(rendered=done,seconds=seconds,camera_lights_floor_and_normal_strength_restored=True)))
