import bpy,json,math,time
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');C=R/'phase01/candidate36';sc=bpy.context.scene;policy=json.loads((R/'work_mode.json').read_text());assert policy['manual_work_authorized'] and policy['mode']=='manual'
roles=json.loads((C/'inspection_ownership.json').read_text())['parts'];objects=[o for o in sc.objects if o.type=='MESH'];model=[o for o in objects if o.get('full_form')];assert len(model)==147 and set(roles)=={o.name for o in model}
visibility={o.name:(o.hide_render,o.hide_get()) for o in objects};matrices={o.name:o.matrix_world.copy() for o in model};cam=sc.camera;cl=cam.location.copy();cr=cam.rotation_euler.copy();ct=cam.data.type;cs=cam.data.ortho_scale;lens=cam.data.lens;settings=(sc.render.resolution_x,sc.render.resolution_y,sc.cycles.samples);completed=[];times=[];inspection_light=sc.objects['Chest Development Fill'];light_state=(inspection_light.location.copy(),inspection_light.rotation_euler.copy(),inspection_light.data.energy);yaw=Matrix.Rotation(math.radians(32),3,'Y')
def world(q):
 p=yaw@Vector(q);return Vector((p.x,-p.z,p.y))
try:
 for name,mode in [('lid_without_rear_leaves_diagnostic','lid')]:
  inspection_light.location=light_state[0];inspection_light.rotation_euler=light_state[1];inspection_light.data.energy=light_state[2]
  for o in model:o.matrix_world=matrices[o.name]
  for o in objects:o.hide_render=visibility[o.name][0]
  cam.location=cl;cam.rotation_euler=cr;cam.data.type=ct;cam.data.lens=lens;sc.render.resolution_x=sc.render.resolution_y=1100;sc.cycles.samples=48
  if mode in ('end','right','back'):
   angle={'end':58,'right':-122,'back':180}[mode]
   for o in model:o.matrix_world=Matrix.Rotation(math.radians(angle),4,'Z')@matrices[o.name]
  if mode in ('body','lid'):
   for o in objects:o.hide_render=True
   for o in model:o.hide_render=not (roles[o.name]=='body' if mode=='body' else roles[o.name] in ('lid','hasp'))
   sc.objects['Chest Rear Hinge Upper -1'].hide_render=True;sc.objects['Chest Rear Hinge Upper 1'].hide_render=True
   cam.data.type='PERSP';cam.data.lens=58;sc.render.resolution_x=sc.render.resolution_y=1000;sc.cycles.samples=48
   if mode=='body':cam.location=world((6,5.5,8));target=world((0,-.7,0))
   else:cam.location=world((5,-4.5,7));target=world((0,1.1,0))
   cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
   inspection_light.location=world((0,4,0) if mode=='body' else (0,-1.5,0));inspection_light.rotation_euler=(target-inspection_light.location).to_track_quat('-Z','Y').to_euler();inspection_light.data.energy=650
  sc.render.filepath=str(C/(name+'.png'));start=time.time();bpy.ops.render.render(write_still=True);times.append(time.time()-start);completed.append(name);(C/'rear_leaf_diagnostic_progress.json').write_text(json.dumps(dict(completed=completed,seconds=times),indent=2))
finally:
 inspection_light.location=light_state[0];inspection_light.rotation_euler=light_state[1];inspection_light.data.energy=light_state[2]
 for o in model:o.matrix_world=matrices[o.name]
 for o in objects:o.hide_render=visibility[o.name][0];o.hide_set(visibility[o.name][1])
 cam.location=cl;cam.rotation_euler=cr;cam.data.type=ct;cam.data.ortho_scale=cs;cam.data.lens=lens;sc.render.resolution_x,sc.render.resolution_y,sc.cycles.samples=settings;bpy.context.view_layer.update()
print(json.dumps(dict(rendered=completed,seconds=times,visibility_and_full_scene_restored=True)))
