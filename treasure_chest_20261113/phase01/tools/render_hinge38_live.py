import bpy,math,json,time
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');C=R/'phase01/candidate38';sc=bpy.context.scene
objects=[o for o in sc.objects if o.type=='MESH'];model=[o for o in objects if o.get('full_form')];assert len(model)==155;visibility={o.name:(o.hide_render,o.hide_get()) for o in objects};matrices={o.name:o.matrix_world.copy() for o in model};cam=sc.camera;old=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.type,cam.data.ortho_scale,cam.data.lens,sc.render.resolution_x,sc.render.resolution_y,sc.cycles.samples,sc.render.filepath);yaw=Matrix.Rotation(math.radians(32),3,'Y');done=[]
def world(q):p=yaw@Vector(q);return Vector((p.x,-p.z,p.y))
try:
 for name in ('back','hinge_close','bore_pin_removed'):
  for o in model:o.matrix_world=matrices[o.name]
  for o in objects:o.hide_render=visibility[o.name][0]
  cam.location=old[0];cam.rotation_euler=old[1];cam.data.type=old[2];cam.data.ortho_scale=old[3];cam.data.lens=old[4];sc.render.resolution_x=sc.render.resolution_y=1100;sc.cycles.samples=48
  if name=='back':
   for o in model:o.matrix_world=Matrix.Rotation(math.pi,4,'Z')@matrices[o.name]
  else:
   cam.data.type='ORTHO';cam.data.ortho_scale=1.65 if name=='hinge_close' else .75;target=world((1.55,.40,-1.93));cam.location=world((3.7,1.6,-5.5)) if name=='hinge_close' else world((3.8,.36175,-1.93));
   if name=='bore_pin_removed':
    target=world((1.55,.36175,-1.93))
    for side in (-1,1):sc.objects[f'Chest Rear Hinge Barrel {side}'].hide_render=True
   cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
  sc.render.filepath=str(C/(name+'.png'));bpy.ops.render.render(write_still=True);done.append(name);(C/'render_progress.json').write_text(json.dumps(dict(completed=done),indent=2))
finally:
 for o in model:o.matrix_world=matrices[o.name]
 for o in objects:o.hide_render=visibility[o.name][0];o.hide_set(visibility[o.name][1])
 cam.location,cam.rotation_euler,cam.data.type,cam.data.ortho_scale,cam.data.lens,sc.render.resolution_x,sc.render.resolution_y,sc.cycles.samples,sc.render.filepath=old;bpy.context.view_layer.update()
print(json.dumps(dict(rendered=done,complete_scene_restored=True)))
