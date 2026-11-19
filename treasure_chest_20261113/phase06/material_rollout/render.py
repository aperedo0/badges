import bpy,sys,json,time,os
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parent;view=sys.argv[sys.argv.index('--')+1];final=os.environ.get('CHEST_FINAL')=='1';out=D/('final_' if final else 'draft_')/(view+'.png');out.parent.mkdir(exist_ok=True)
if out.exists():raise SystemExit('Using cached '+str(out))
bpy.ops.wm.open_mainfile(filepath=str(D/'master.blend'));P=D.parents[1]/'phase04/wood_lab';code=(P/'render_batch.py').read_text().split('jobs=')[0].replace("sc=bpy.data.scenes['Wood surface comparison']","sc=bpy.data.scenes['Full chest material evaluation']");exec(compile(code,'existing_cycles_camera_and_device_rig','exec'));sc.frame_set(0)
if view=='full':frame('full');sc.render.resolution_x=sc.render.resolution_y=1800 if final else 1100
elif view=='close':
 target=world((-.95,-.25,1.62));forward=camera.to_quaternion()@Vector((0,0,-1));cam.location=target-forward*12;cam.rotation_euler=camera.to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=4.35;sc.render.resolution_x=1800 if final else 1200;sc.render.resolution_y=1400 if final else 930
elif view=='back':
 target=world((0,0,0));position=world((7.8,5.4,-10));cam.location=position;cam.rotation_euler=(target-position).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=8.5;sc.render.resolution_x=sc.render.resolution_y=1200
# Presentation only: retain the saved illumination and actual production materials.
# Camera background separation does not alter environment reflections.
sc.world=sc.world.copy();nt=sc.world.node_tree
if not nt.nodes.get('Rollout camera background'):
 output=next(n for n in nt.nodes if n.type=='OUTPUT_WORLD' and n.is_active_output);source=output.inputs['Surface'].links[0].from_socket;path=nt.nodes.new('ShaderNodeLightPath');bg=nt.nodes.new('ShaderNodeBackground');bg.name='Rollout camera background';bg.inputs['Color'].default_value=(.009,.007,.009,1);mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(path.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(source,mix.inputs[1]);nt.links.new(bg.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],output.inputs['Surface']);sc.render.film_transparent=False
floors=[o for o in sc.objects if o.type=='MESH' and 'floor' in o.name.lower()];parts=[o for o in sc.objects if o.type=='MESH' and not o.hide_render and 'floor' not in o.name.lower()];bottom=min((o.matrix_world@Vector(q)).z for o in parts for q in o.bound_box)
for floor in floors:floor.location.z+=bottom-max((floor.matrix_world@Vector(q)).z for q in floor.bound_box)+.0005
if view=='back':
 for n in nt.nodes:
  if n.type=='BACKGROUND' and n.inputs['Color'].is_linked:n.inputs['Strength'].default_value=.65
sc.render.resolution_percentage=100;sc.cycles.samples=128 if final else 32;sc.cycles.seed=17;sc.cycles.use_denoising=True;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.render.filepath=str(out);start=time.time();bpy.ops.render.render(write_still=True);print('RENDERED',view,'samples',sc.cycles.samples,'seconds',time.time()-start,flush=True)
