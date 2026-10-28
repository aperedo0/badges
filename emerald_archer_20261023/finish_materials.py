"""Use measured uniform metal tones, keeping fine grain and clear gem facets."""
from pathlib import Path
import shutil
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'candidate02/textures'
OUT.mkdir(parents=True,exist_ok=True)
(ROOT/'candidate02/mobile').mkdir(exist_ok=True)
shutil.copyfile(ROOT/'candidate01/design.json',ROOT/'candidate02/design.json')
shutil.copyfile(ROOT/'candidate01/textures/field_roughness.png',OUT/'field_roughness.png')
def decode(a):
    a=a/255.;return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
def encode(a):
    a=np.clip(a,0,1);return np.uint8(np.clip(np.where(a<=.0031308,a*12.92,1.055*a**(1/2.4)-.055)*255+.5,0,255))
grain=decode(np.asarray(Image.open(ROOT/'candidate01/textures/field_color.png'),float))[:,:,1]/.075
color=np.array([.0006,.014,.0020])[None,None,:]*grain[:,:,None]
Image.fromarray(encode(color)).save(OUT/'field_color.png')
COLORS={'gold':[.7605,.3185,.0409], 'emerald':[.001,.25,.055],
 'emerald_light':[.040,.60,.20], 'emerald_dark':[.0005,.040,.008]}
GLOW={'emerald':[0,.015,.003],'emerald_light':[.025,.15,.060],'emerald_dark':[0,0,0]}
for role,color in COLORS.items():
    Image.fromarray(np.tile(encode(np.array(color)),(512,512,1))).save(OUT/(role+'_color.png'))
    if role in GLOW:Image.fromarray(np.tile(encode(np.array(GLOW[role])),(512,512,1))).save(OUT/(role+'_emission.png'))
print('Uniform measured metal tones, intrinsic fine grain, and emerald facet fill saved')
