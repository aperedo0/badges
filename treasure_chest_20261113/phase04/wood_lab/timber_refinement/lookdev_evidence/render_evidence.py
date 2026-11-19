import bpy,sys,time,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parent;W=D.parent;P=W.parent
mode=sys.argv[sys.argv.index('--')+1]
base=D/'baseline_live.blend';bpy.ops.wm.open_mainfile(filepath=str(base))
code=(P/'render_batch.py').read_text().split('jobs=')[0].replace("sc=bpy.data.scenes['Wood surface comparison']","sc=bpy.data.scenes['Test plank master']")
exec(compile(code,'existing_render_infrastructure','exec'))
sc.frame_set(0);frame('close');sc.render.resolution_x=1600;sc.render.resolution_y=1184;sc.render.resolution_percentage=100;sc.cycles.samples=128;sc.cycles.use_denoising=True;sc.cycles.seed=17;sc.view_settings.exposure=0;sc.render.image_settings.color_depth='16'
key=sc.objects['Lab Chest Development Key'];body=sc.objects['Master Chest Body Envelope'];mat=next(m for m in body.data.materials if m and m.name.startswith('Wood Lab '))
if mode in ['direction','smaller_source','warm_key','calibrated','golden','core_candidate']:
 key.location=(-2,-7,4.6);key.rotation_euler=(world((-1.1,-1.35,1.6))-key.location).to_track_quat('-Z','Y').to_euler()
if mode in ['smaller_source','warm_key','calibrated','golden','core_candidate']:key.data.size=1.0
if mode in ['warm_key','calibrated','golden','core_candidate']:key.data.color=(1,.76,.50);key.data.energy=2200
if mode=='raw_control':sc.cycles.use_denoising=False
if mode in ['calibrated','golden','core_candidate']:
 mat=mat.copy();body.data=body.data.copy();slot=next(i for i,m in enumerate(body.data.materials) if m and m.name.startswith('Wood Lab '));body.data.materials[slot]=mat
 im=bpy.data.images.load(str(D/'calibrated_normal.png'),check_existing=False);im.colorspace_settings.name='Non-Color';mat.node_tree.nodes['Single plank normal'].image=im
if mode in ['golden','core_candidate']:key.data.color=(1,.62,.28)
if mode=='core_candidate':
 for role in ['albedo','roughness','normal']:
  im=bpy.data.images.load(str(W/'V_lookdev_refinement'/(role+'.png')),check_existing=False);im.colorspace_settings.name='sRGB' if role=='albedo' else 'Non-Color';mat.node_tree.nodes['Single plank '+role].image=im
if mode=='warm_key':
 sc.view_layers[0].cycles.denoising_store_passes=True
 ng=bpy.data.node_groups.new('Paired raw evidence','CompositorNodeTree');sc.compositing_node_group=ng;sc.render.use_compositing=True
 ng.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');rl=ng.nodes.new('CompositorNodeRLayers');rl.scene=sc;rl.layer=sc.view_layers[0].name
 composite=ng.nodes.new('NodeGroupOutput');ng.links.new(rl.outputs['Image'],composite.inputs['Image'])
 fo=ng.nodes.new('CompositorNodeOutputFile');fo.file_output_items.new('RGBA','raw');fo.directory=str(D/'renders');fo.file_name='paired_raw';fo.format.exr_codec='ZIP';fo.save_as_render=True
 print('PASSES',list(rl.outputs.keys()),flush=True);ng.links.new(rl.outputs['Noisy Image'],fo.inputs[0])
if mode=='filter_control':
 # Same scene, image sampling, material and geometry; narrower image reconstruction filter only.
 sc.cycles.filter_width=.8
if mode=='normal_control':
 mat=mat.copy();slot=next(i for i,m in enumerate(body.data.materials) if m and m.name.startswith('Wood Lab '));body.data=body.data.copy();body.data.materials[slot]=mat;mat.node_tree.nodes['Single plank physical tangent normal'].inputs['Strength'].default_value=0
out=D/'renders';out.mkdir(exist_ok=True);sc.render.filepath=str(out/(mode+'.png'))
a=np.empty(len(body.data.vertices)*3,dtype=np.float32);body.data.vertices.foreach_get('co',a);assert hashlib.sha256(a.tobytes()).hexdigest()==json.loads((D/'baseline_inventory.json').read_text())['geometry_sha256']
normal=world((0,0,1));target=world((-1.31,-1.35,1.6));direction=(key.location-target).normalized();angle=float(np.degrees(np.arccos(np.clip(normal.dot(direction),-1,1))))
metadata=dict(mode=mode,geometry_unchanged=True,material_unchanged=mode not in ['normal_control','calibrated','golden','core_candidate'],camera=[list(row) for row in cam.matrix_world],ortho=cam.data.ortho_scale,resolution=[1600,1184],samples=sc.cycles.samples,seed=sc.cycles.seed,denoise=sc.cycles.use_denoising,filter_width=sc.cycles.filter_width,view=sc.view_settings.view_transform,look=sc.view_settings.look,exposure=sc.view_settings.exposure,key=dict(location=list(key.location),size=key.data.size,power=key.data.energy,color=list(key.data.color),incidence_degrees_from_board_normal=angle))
(out/(mode+'.json')).write_text(json.dumps(metadata,indent=2));st=time.time();bpy.ops.render.render(write_still=True);print('COMPLETE',mode,time.time()-st,flush=True)
if mode=='warm_key':
 import shutil
 files=list((D/'renders').glob('paired_raw*.exr'));assert len(files)==1,[str(f) for f in files];raw=bpy.data.images.load(str(files[0]),check_existing=False);raw.save_render(str(D/'renders/warm_key_raw.png'),scene=sc)
