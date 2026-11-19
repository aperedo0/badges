import bpy,math,json,time
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');C=R/'phase01/candidate43';sc=bpy.context.scene;master=sc.objects['Chest Rig Master'];assert sc.frame_current==0
report=json.loads((C/'whole_motion_screen.json').read_text());assert report['complete'] and not report['unclassified'],'Motion checks not accepted yet'
cam=sc.camera;camera=cam.matrix_world.copy();props=(cam.data.type,cam.data.ortho_scale,cam.data.lens,sc.render.resolution_x,sc.render.resolution_y,sc.cycles.samples,sc.render.filepath);lights={o.name:(o.matrix_world.copy(),o.data.energy) for o in sc.objects if o.type=='LIGHT'};fill=sc.objects['Chest Development Fill'];objects=[o for o in sc.objects if o.type=='MESH'];visibility={o.name:(o.hide_render,o.hide_get()) for o in objects};action=master.animation_data.action;curves=list(action.fcurves) if hasattr(action,'fcurves') else [f for l in action.layers for s in l.strips for b in s.channelbags for f in b.fcurves];curve=next(f for f in curves if f.data_path=='["lid_degrees"]');oldmute=curve.mute;yaw=Matrix.Rotation(math.radians(32),3,'Y');done=[];seconds=[]
def world(q):p=yaw@Vector(q);return Vector((p.x,-p.z,p.y))
def manual(degrees):
 sc.frame_set(240);bpy.context.view_layer.update();curve.mute=True;master['lid_degrees']=float(degrees);master.update_tag(refresh={'TIME','OBJECT'});bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();dg.update();assert abs(sc.objects['Chest Rig LidOpen'].evaluated_get(dg).rotation_axis_angle[0]+math.radians(degrees))<1e-6
jobs=[('reference','closed',0),('left_end','orbit',-58),('right_end','orbit',122),('back','orbit',180),('early_turn','orbit',12),('open30_front','open',30),('open95_front','open',95),('open95_floor','floor',95),('open95_rear','rear',95)]
try:
 for name,mode,value in jobs:
  sc.objects['Development floor'].hide_render=(mode=='orbit')
  for n,(M,energy) in lights.items():sc.objects[n].matrix_world=M;sc.objects[n].data.energy=energy
  cam.matrix_world=camera;cam.data.type=props[0];cam.data.ortho_scale=props[1];cam.data.lens=props[2];sc.render.resolution_x=sc.render.resolution_y=1100;sc.cycles.samples=32
  if mode in ('closed','orbit'):
   curve.mute=oldmute;master.update_tag(refresh={'TIME'});sc.frame_set(0);bpy.context.view_layer.update()
   if mode=='orbit':
    turn=Matrix.Rotation(math.radians(value),4,'Z');cam.matrix_world=turn@camera
    for n,(M,energy) in lights.items():sc.objects[n].matrix_world=turn@M
  else:
   manual(value);cam.data.type='ORTHO';cam.data.ortho_scale=10.2
   if mode=='open':cam.location=camera.translation+Vector((0,0,1.0))
   elif mode in ('floor','rear'):
    target=world((0,-.4,0) if mode=='floor' else (0,1.0,-1.4));cam.location=world((5,11,6) if mode=='floor' else (-6,5,-9));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();fill.location=world((0,4,0) if mode=='floor' else (-3,4,-6));fill.rotation_euler=(target-fill.location).to_track_quat('-Z','Y').to_euler();fill.data.energy=650
   else:
    target=world((1.55,.40,-1.93));cam.location=world((3.7,1.6,-5.5));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.65;fill.location=world((3,2,-4));fill.rotation_euler=(target-fill.location).to_track_quat('-Z','Y').to_euler();fill.data.energy=250
  sc.render.filepath=str(C/(name+'.png'));start=time.time();bpy.ops.render.render(write_still=True);seconds.append(time.time()-start);done.append(name);(C/'render_sweep_progress.json').write_text(json.dumps(dict(completed=done,seconds=seconds),indent=2))
finally:
 curve.mute=oldmute;master.update_tag(refresh={'TIME'});sc.frame_set(0);bpy.context.view_layer.update();cam.matrix_world=camera;cam.data.type,cam.data.ortho_scale,cam.data.lens,sc.render.resolution_x,sc.render.resolution_y,sc.cycles.samples,sc.render.filepath=props
 for n,(M,energy) in lights.items():sc.objects[n].matrix_world=M;sc.objects[n].data.energy=energy
 for ob in objects:ob.hide_render=visibility[ob.name][0];ob.hide_set(visibility[ob.name][1])
 bpy.context.view_layer.update()
assert len(done)==9 and abs(master['lid_degrees'])<1e-6
print(json.dumps(dict(rendered=done,seconds=seconds,closed_scene_and_inspection_lights_restored=True)))
