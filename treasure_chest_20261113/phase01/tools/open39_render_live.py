import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');C=R/'phase01/candidate39';sc=bpy.context.scene;master=sc.objects['Chest Rig Master'];action=master.animation_data.action;curves=list(action.fcurves) if hasattr(action,'fcurves') else [f for l in action.layers for s in l.strips for b in s.channelbags for f in b.fcurves];curve=next(f for f in curves if f.data_path=='["lid_degrees"]');oldmute=curve.mute;rest=sc.frame_current;cam=sc.camera;old=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.type,cam.data.ortho_scale,cam.data.lens,sc.render.resolution_x,sc.render.resolution_y,sc.cycles.samples,sc.render.filepath);done=[]
try:
 sc.frame_set(240);bpy.context.view_layer.update();curve.mute=True;master['lid_degrees']=95.;master.update_tag(refresh={'OBJECT','TIME'});bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();dg.update();assert abs(sc.objects['Chest Rig LidOpen'].evaluated_get(dg).rotation_axis_angle[0]+math.radians(95))<1e-6
 cam.data.type='ORTHO';cam.data.ortho_scale=10.2;cam.location=old[0]+Vector((0,0,1.0));cam.rotation_euler=old[1];sc.cycles.samples=32;sc.render.resolution_x=sc.render.resolution_y=1100;sc.render.filepath=str(C/'open95_front.png');bpy.ops.render.render(write_still=True);done.append('open95_front')
finally:
 curve.mute=oldmute;master.update_tag(refresh={'TIME'});sc.frame_set(rest);bpy.context.view_layer.update();cam.location,cam.rotation_euler,cam.data.type,cam.data.ortho_scale,cam.data.lens,sc.render.resolution_x,sc.render.resolution_y,sc.cycles.samples,sc.render.filepath=old
assert sc.frame_current==0 and abs(master['lid_degrees'])<1e-6
(C/'open_render_progress.json').write_text(json.dumps(dict(rendered=done,complete_closed_scene_restored=True),indent=2));print(json.dumps(done))
