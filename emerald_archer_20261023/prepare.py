"""Prepare subtle intrinsic green metal maps for the complete Blender badge."""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'candidate01/textures';OUT.mkdir(parents=True,exist_ok=True)
N=1024;y,x=np.indices((N,N));wx=(x+.5)/N*6.03-3.015;wy=3.015-(y+.5)/N*6.03
r=np.hypot(wx,wy);a=np.arctan2(wy,wx)
rng=np.random.default_rng(2410)
# Very fine concentric machining is a reflectance variation, without broad bands.
grain=gaussian_filter(rng.normal(size=(N,N)),(.35,2))
grain=grain/np.std(grain)*.010
grain+=.007*np.sin(r*890+1.7*np.sin(a*5))
color=np.array([.004,.075,.025])[None,None,:]*(1+grain[:,:,None])
encoded=np.where(color<=.0031308,color*12.92,1.055*color**(1/2.4)-.055)
Image.fromarray(np.uint8(np.clip(encoded*255+.5,0,255))).save(OUT/'field_color.png')
Image.fromarray(np.uint8(np.clip((.32+grain*.05)*255+.5,0,255))).save(OUT/'field_roughness.png')
print('Intrinsic green field maps prepared')
