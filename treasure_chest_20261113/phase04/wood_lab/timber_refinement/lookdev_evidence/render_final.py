import bpy,sys,json,time
from pathlib import Path
D=Path(__file__).resolve().parent;W=D.parent;P=W.parent;view=sys.argv[sys.argv.index('--')+1];C=W/'V_lookdev_refinement'
bpy.ops.wm.open_mainfile(filepath=str(C/'master.blend'))
code=(P/'render_batch.py').read_text().split('jobs=')[0].replace("sc=bpy.data.scenes['Wood surface comparison']","sc=bpy.data.scenes['Test plank master']")
exec(compile(code,'existing_camera_and_render_setup','exec'))
sc.frame_set(0);frame('full' if view=='full' else 'plank' if view=='plank' else 'close');sc.render.resolution_x=1400 if view=='full' else 2160 if view=='plank' else 1600 if view in ['close','filter','texture_filter'] else 1200;sc.render.resolution_y=1400 if view=='full' else 1000 if view=='plank' else 1184 if view in ['close','filter','texture_filter'] else 888
if view=='right':
 target=world((1.4,-1.45,1.6));forward=camera.to_quaternion()@Vector((0,0,-1));cam.location=target-forward*12;cam.rotation_euler=camera.to_euler()
if view=='filter':sc.cycles.filter_width=.8
if view=='texture_filter':
 m=next(m for m in sc.objects['Master Chest Body Envelope'].data.materials if m and m.name.startswith('Wood Lab V_'));m.node_tree.nodes['Single plank normal'].interpolation='Closest'
sc.render.resolution_percentage=100;sc.cycles.samples=128;sc.cycles.seed=17;sc.cycles.use_denoising=True;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_depth='16';sc.render.filepath=str(C/(view+'.png'));st=time.time();bpy.ops.render.render(write_still=True);print('FINAL',view,time.time()-st,flush=True)
(C/(view+'_render.json')).write_text(json.dumps(dict(view=view,camera=[list(row) for row in cam.matrix_world],ortho=cam.data.ortho_scale,resolution=[sc.render.resolution_x,sc.render.resolution_y],samples=sc.cycles.samples,pixel_filter_width=sc.cycles.filter_width,normal_texture_interpolation=next(m for m in sc.objects['Master Chest Body Envelope'].data.materials if m and m.name.startswith('Wood Lab V_')).node_tree.nodes['Single plank normal'].interpolation,view_transform=sc.view_settings.view_transform,look=sc.view_settings.look,exposure=sc.view_settings.exposure),indent=2))
