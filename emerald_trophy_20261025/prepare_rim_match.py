"""Match the trophy rim's intrinsic gold finish while preserving geometry."""
from pathlib import Path
import zipfile,json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,map_coordinates
R=Path(__file__).resolve().parent;C=R/'candidate06';T=C/'textures';T.mkdir(parents=True,exist_ok=True);(C/'mobile').mkdir(exist_ok=True)
S=R/'candidate05/mobile/emerald_trophy_badge_mobile.usdz'
def decode(a):
 a=np.asarray(a,float)/255.;return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
def encode(a):return np.uint8(np.clip(np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)*255+.5,0,255))
with zipfile.ZipFile(S) as z:
 color=decode(Image.open(z.open('textures/Rim_brushed_reference_color.png')))
 rough=np.asarray(Image.open(z.open('textures/Rim_brushed_reference_roughness.png')),float)/255.
old=np.array([.80,.58,.23]);gold=np.array([.84,.45,.10])
# A clear area of the cup contains the reference's fine brushed grain.
photo=decode(Image.open(R/'reference.png').convert('RGB'))[490:575,590:664]
lum=photo@np.array([.2126,.7152,.0722]);log=np.log(np.maximum(lum,1e-5))
fine=log-gaussian_filter(log,1.0);fine-=np.mean(fine)
fine=np.clip(fine,-.035,.035)
# Mirror every chart join. Only fine intrinsic variation remains, with no broad light bands.
fine=np.concatenate([fine,fine[:,::-1]],axis=1);fine=np.concatenate([fine,fine[::-1]],axis=0)
yy,xx=np.mgrid[:1024,:1024]
q=map_coordinates(fine,[(yy/1024*6%1)*(fine.shape[0]-1),(xx/1024*4%1)*(fine.shape[1]-1)],order=1,mode='wrap')
grain=1+q*.35
Image.fromarray(encode(np.clip(gold[None,None,:]*grain[...,None],0,1))).save(T/'Rim_brushed_reference_color.png')
v=1-(np.arange(1024)+.5)/1024
for lo,hi,mean in [(.006,.494,.205),(.526,.744,.195)]:
 rows=(v>=lo)&(v<=hi);src=rough[rows];rough[rows]=mean
Image.fromarray(np.uint8(np.clip(rough*255+.5,0,255))).save(T/'Rim_brushed_reference_roughness.png')
meta={'source':'candidate05/mobile/emerald_trophy_badge_mobile.usdz','gold_linear':gold.tolist(),'grain_source':'Clean central cup area from the owner reference, with broad illumination removed',
 'band_roughness':.205,'wall_roughness':.195,'rim_emission':0,'geometry_changed':False,
 'authorization':'Owner: make the rim texture match the trophy',
 'preserved':'All geometry, normals, UVs, relief materials and maps, field, border roughness graphs, glints and runtime brushing'}
(C/'rim_finish.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta,indent=2))
