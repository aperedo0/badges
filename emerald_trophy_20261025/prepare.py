"""Prepare low contrast intrinsic emerald mineral maps without studio lighting."""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,zoom
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'candidate01/textures';OUT.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(2525);N=512
coarse=zoom(rng.normal(size=(32,32)),N/32,order=3)
fine=gaussian_filter(rng.normal(size=(N,N)),2)
grain=.07*coarse/np.std(coarse)+.018*fine/np.std(fine)
color=np.array([.001,.020,.0042])[None,None,:]*(1+grain[:,:,None])
encoded=np.where(color<=.0031308,12.92*color,1.055*color**(1/2.4)-.055)
Image.fromarray(np.uint8(np.clip(encoded*255+.5,0,255))).save(OUT/'field_color.png')
Image.fromarray(np.uint8(np.clip((.44+grain*.06)*255+.5,0,255))).save(OUT/'field_roughness.png')
for candidate in ['candidate02','candidate03']:
    target=ROOT/candidate/'textures';target.mkdir(parents=True,exist_ok=True)
    color=np.array([.0005,.026,.0022] if candidate=='candidate03' else [.001,.020,.0042])[None,None,:]*(1+grain[:,:,None])
    encoded=np.where(color<=.0031308,12.92*color,1.055*color**(1/2.4)-.055)
    Image.fromarray(np.uint8(np.clip(encoded*255+.5,0,255))).save(target/'field_color.png')
    (target/'field_roughness.png').write_bytes((OUT/'field_roughness.png').read_bytes())
print('Emerald mineral maps ready')
