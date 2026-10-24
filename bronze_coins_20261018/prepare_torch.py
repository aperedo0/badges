"""Intrinsic bronze and charcoal. The app supplies every broad highlight."""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT=Path(__file__).resolve().parent
out=ROOT/'torch_sunburst/textures'
source=np.load(ROOT.parent/'coin_brush_grain.npz')['grain']
grain=np.asarray(Image.fromarray(source.astype(np.float32)).resize((512,512),Image.Resampling.BILINEAR))
grain=gaussian_filter(grain,.45)
grain=np.clip((grain-grain.mean())/max(grain.std(),1e-6),-2.5,2.5)
def encode(v):
    v=np.clip(v,0,1)
    return np.uint8(np.where(v<=.0031308,v*12.92,1.055*v**(1/2.4)-.055)*255+.5)
bronze=np.array([.62,.300,.130])[None,None,:]*np.exp(grain[:,:,None]*.025)
Image.fromarray(encode(bronze)).save(out/'bronze_color.png')
rough=np.clip(.31+grain*.006,.27,.35)
Image.fromarray(np.uint8(rough*255+.5)).save(out/'bronze_roughness.png')
charcoal=np.array([.016,.011,.007])[None,None,:]*np.exp(grain[:,:,None]*.020)
Image.fromarray(encode(charcoal)).save(out/'backdrop_color.png')
print('Torch intrinsic brushed bronze and warm dark backing prepared.')
