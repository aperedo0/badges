import bpy,numpy as np,math
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/ruby_heart_gem_20261113');sc=bpy.context.scene;ob=sc.objects['Ruby Heart gem'];print('Matrix',list(ob.matrix_world))
a=np.load(R.parent/'ruby_heart_claude_20261107/tools/studio.npz')['rgb'];h,w=a.shape[:2];a=a.reshape(h//2,2,w//2,2,3).mean((1,3));h,w=a.shape[:2];u=.5+math.atan2(.773,.393)/(2*math.pi);v=.5-math.asin(.497)/math.pi;x=int(u*w);y=int(v*h)
im=bpy.data.images.load(str(R/'optics/studio_mip1.exr'),check_existing=False);aa=np.array(im.pixels[:]).reshape(h,w,4);print('u v',u,v,'NP',a[y,x],a[h-1-y,x], 'EXR bottom top',aa[y,x,:3],aa[h-1-y,x,:3], 'max',aa.max())
p=R/'optics/probe_variables.osl';s=p.read_text().replace('float v=.5-asin(clamp(e[1],-1,1))/M_PI;','float v=1-(.5-asin(clamp(e[1],-1,1))/M_PI);');p2=R/'optics/probe_flip.osl';p2.write_text(s);script=next(n for n in ob.data.materials[0].node_tree.nodes if n.bl_idname=='ShaderNodeScript');script.filepath=str(p2);script.update()
for lv in (1,2,3,8):script.inputs['Mip'+str(lv)].default_value=str(R/'optics'/f'studio_linear_mip{lv}.exr')
script.inputs['Probe'].default_value=4;sc.cycles.samples=1;sc.cycles.use_denoising=False;sc.render.image_settings.file_format='OPEN_EXR';sc.render.image_settings.color_depth='32';sc.render.filepath=str(R/'optics/probe_flip.exr');bpy.ops.render.render(write_still=True);im=bpy.data.images.load(sc.render.filepath,check_existing=False);w,h=im.size;arr=np.array(im.pixels[:]).reshape(h,w,4);print('FLIPPED texture actual',arr[h-1-153,168,:3])
script.filepath=str(R/'optics/ruby_foil.osl');script.update()
for lv in (1,2,3,8):script.inputs['Mip'+str(lv)].default_value=str(R/'optics'/f'studio_linear_mip{lv}.exr')
sc.cycles.samples=64;sc.cycles.use_denoising=True;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_depth='8'
