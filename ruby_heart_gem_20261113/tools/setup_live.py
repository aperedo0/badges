import bpy,numpy as np,json,math
from pathlib import Path
from mathutils import Vector
R=Path('/Users/antonioperedo/Desktop/badges/ruby_heart_gem_20261113')
sc=bpy.context.scene;sc.name='Ruby Heart Gem';bpy.ops.wm.save_as_mainfile(filepath=str(R/'ruby_heart.blend'))
a=np.load(R.parent/'ruby_heart_claude_20261107/tools/studio.npz')['rgb']
for level in range(9):
 if level in (1,2,3,8):
  h,w=a.shape[:2];im=bpy.data.images.new('Ruby studio mip'+str(level),width=w,height=h,float_buffer=True)
  im.colorspace_settings.name='Non-Color'
  rgba=np.dstack([a,np.ones((h,w),np.float32)]);im.pixels.foreach_set(np.flipud(rgba).ravel());im.filepath_raw=str(R/'optics'/f'studio_linear_mip{level}.exr');im.file_format='OPEN_EXR';im.save()
 if level<8:
  h,w=a.shape[:2];a=a[:h//2*2,:w//2*2].reshape(h//2,2,w//2,2,3).mean((1,3))
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.shading_system=True;sc.cycles.samples=64;sc.cycles.use_denoising=True
mat=bpy.data.materials.new('Ruby Heart native foil development');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');script=nt.nodes.new('ShaderNodeScript');script.mode='EXTERNAL';script.filepath=str(R/'optics/ruby_foil.osl');script.update()
for lv in (1,2,3,8):script.inputs['Mip'+str(lv)].default_value=str(R/'optics'/f'studio_linear_mip{lv}.exr')
nt.links.new(script.outputs['BSDF'],out.inputs['Surface']);ob=sc.objects['Ruby Heart gem'];ob.data.materials.clear();ob.data.materials.append(mat)
cam=sc.camera;cam.location=(0,-23,1.8);target=Vector((0,0,-.55));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.sensor_fit='HORIZONTAL';cam.data.sensor_width=36;cam.data.lens=1762.5*36/1206;cam.data.shift_x=0;cam.data.shift_y=(633.3-2622/2)/1206
sc.render.resolution_x=1206;sc.render.resolution_y=2622;sc.render.resolution_percentage=100;sc.render.use_border=True;sc.render.use_crop_to_border=True;sc.render.border_min_x=300/1206;sc.render.border_max_x=906/1206;sc.render.border_min_y=1-950/2622;sc.render.border_max_y=1-300/2622
sc.render.filepath=str(R/'baseline/blender_front.png');bpy.ops.wm.save_as_mainfile(filepath=str(R/'ruby_heart.blend'));bpy.ops.render.render(write_still=True)
print('Saved live native optics baseline')
