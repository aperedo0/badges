import bpy,numpy as np
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/royal_heart_compass_20261106')
p=R.parent/'emerald_trophy_20261025/preview/ScreenTime/SupportingFiles/Assets.xcassets/Badge3DGemEnvironment.dataset/badge_studio_1024.exr'
im=bpy.data.images.load(str(p));w,h=im.size;pixels=np.empty(w*h*4,np.float32);im.pixels.foreach_get(pixels)
rgb=pixels.reshape(h,w,4)[::-1,:,:3].copy();np.savez_compressed(R/'optics_fit/studio.npz',rgb=rgb)
print('Studio light sampled into numeric linear RGB',w,h,'peak',rgb.max(),'space',im.colorspace_settings.name)
