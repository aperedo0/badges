import bpy,numpy as np
from pathlib import Path
path='/Users/antonioperedo/Desktop/badges/emerald_trophy_20261025/preview/ScreenTime/SupportingFiles/Assets.xcassets/Badge3DGemEnvironment.dataset/badge_studio_1024.exr'
im=bpy.data.images.load(path,check_existing=True);W,H=im.size
p=np.array(im.pixels[:],np.float32).reshape(H,W,4)[::-1,:,:3]
np.save('/Users/antonioperedo/Desktop/badges/royal_heart_compass_20261106/gem_light.npy',p)
print(W,H,float(p.max()))
