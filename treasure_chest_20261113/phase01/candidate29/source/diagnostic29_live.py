import bpy,math,json,time
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');C=R/'phase01/candidate29';sc=bpy.context.scene;s=json.loads((R/'schedule.json').read_text());assert s['status']=='active' and s['phase']=='work' and time.time()+105<s['work_until_epoch'],'Not enough work time for diagnostic'
show={'Chest Case Back With Key Bore','Chest Hollow Lock Case Walls','Chest Rotating Keyed Cam','Chest Fixed Cam C Bearing'}
flags={o.name:o.hide_render for o in sc.objects};cam=sc.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();typ=cam.data.type;ortho=cam.data.ortho_scale;path=sc.render.filepath
yaw=Matrix.Rotation(math.radians(32),3,'Y')
def world(q):
 p=yaw@Vector(q);return Vector((p.x,-p.z,p.y))
try:
 for o in sc.objects:
  if o.type=='MESH' and o.name not in show:o.hide_render=True
 target=world((0,-.40,1.95));cam.location=world((.70,.15,8));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.25;sc.render.filepath=str(C/'internal_front_cover_removed.png');result=bpy.ops.render.render(write_still=True);assert 'FINISHED' in result
finally:
 for n,v in flags.items():sc.objects[n].hide_render=v
 cam.location=loc;cam.rotation_euler=rot;cam.data.type=typ;cam.data.ortho_scale=ortho;sc.render.filepath=path;bpy.context.view_layer.update()
print('Rendered actual internal stage one with front covers removed; restored complete chest')
