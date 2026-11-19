import bpy,numpy as np
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/ruby_heart_gem_20261113');a=np.load(R.parent/'ruby_heart_claude_20261107/tools/studio.npz')['rgb']
for lv in range(9):
 if lv in (1,2,3,8):
  h,w=a.shape[:2];im=bpy.data.images.new('Ruby numeric linear studio '+str(lv),width=w,height=h,float_buffer=True);print('Default map space',im.colorspace_settings.name);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.flipud(np.dstack([a,np.ones((h,w),np.float32)])).ravel());im.filepath_raw=str(R/'optics'/f'studio_linear_mip{lv}.exr');im.file_format='OPEN_EXR';im.save()
 if lv<8:
  h,w=a.shape[:2];a=a[:h//2*2,:w//2*2].reshape(h//2,2,w//2,2,3).mean((1,3))
sc=bpy.context.scene;script=next(n for n in sc.objects['Ruby Heart gem'].data.materials[0].node_tree.nodes if n.bl_idname=='ShaderNodeScript')
for lv in (1,2,3,8):script.inputs['Mip'+str(lv)].default_value=str(R/'optics'/f'studio_linear_mip{lv}.exr')
print('Wrote raw numeric light maps with no sRGB encoding.')
