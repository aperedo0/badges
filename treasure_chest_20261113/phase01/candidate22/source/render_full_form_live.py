import bpy,math,json,time
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');OUT=R/'phase01/candidate22';sc=bpy.context.scene
objects=[o for o in sc.objects if o.type=='MESH' and o.get('full_form')];original={o.name:o.matrix_world.copy() for o in objects};cam=sc.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();typ=cam.data.type
poses=json.loads((OUT/'render_queue.json').read_text())
completed=[];deferred=[];timings=[]
schedule_path=R/'schedule.json'
def pose_allowed():
 if not schedule_path.exists():return True
 saved=json.loads(schedule_path.read_text());now=time.time()
 if saved['status']!='active' or saved['phase']!='work':return False
 overall=saved.get('deadline_epoch');work=saved.get('work_until_epoch')
 budget=max(90,max(timings,default=0)*1.5)+15
 return work is not None and now+budget<work and (overall is None or now+budget<overall)
try:
 for pose_index,(name,angle) in enumerate(poses):
  if not pose_allowed():
   deferred=[p[0] for p in poses[pose_index:]];break
  if name=='top':
   cam.data.type='ORTHO';cam.data.ortho_scale=8;cam.location=(0,0,22);cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
  else:cam.data.type=typ;cam.location=loc;cam.rotation_euler=rot
  for ob in objects:ob.matrix_world=Matrix.Rotation(math.radians(angle),4,'Z')@original[ob.name]
  sc.render.filepath=str(OUT/(name+'.png'));started=time.time();result=bpy.ops.render.render(write_still=True)
  if 'FINISHED' not in result:
   deferred=[p[0] for p in poses[pose_index:]];break
  completed.append(name);timings.append(time.time()-started)
  (OUT/'render_progress.json').write_text(json.dumps(dict(completed=completed,deferred=[p[0] for p in poses[pose_index+1:]],seconds=timings),indent=2))
finally:
 for ob in objects:ob.matrix_world=original[ob.name]
 cam.location=loc;cam.rotation_euler=rot;cam.data.type=typ;bpy.context.view_layer.update()
(OUT/'render_progress.json').write_text(json.dumps(dict(completed=completed,deferred=deferred,seconds=timings),indent=2))
print('Rendered',completed,'Deferred until a later work block',deferred)
