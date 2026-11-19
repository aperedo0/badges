from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import map_coordinates,gaussian_filter
D=Path(__file__).resolve().parent;OLD=D.parent/'lower_iron';F=D/'material_masks';F.mkdir(exist_ok=True);w,h=8192,256;L,H=18.04,.5035;X,Y=np.meshgrid(np.linspace(0,L,w,dtype=np.float32),np.linspace(H,0,h,dtype=np.float32))
def ss(a,b,z):t=np.clip((z-a)/max(b-a,1e-8),0,1);return t*t*(3-2*t)
def sample(asset,role,period,offset):
 a=np.asarray(Image.open(next((OLD/'resources'/asset).glob('*'+role+'.png'))).convert('L'),dtype=np.float32)/255;u=((X+.035*np.sin(X*3.7+Y*5.1))/period+offset)%1*(a.shape[1]-1);v=((Y+.02*np.sin(X*2.1))/period+.23)%1*(a.shape[0]-1);return map_coordinates(a,[v,u],order=1,mode='wrap')
r=sample('Metal055A','Roughness',1.25,0);oxide=ss(float(np.percentile(r,30)),float(np.percentile(r,76)),gaussian_filter(r,(.002/.00197,.004/.0022)));rough=sample('Metal003','Roughness',1.6,.38);s=gaussian_filter(rough,(2,5));body=.34*(1-ss(float(np.percentile(s,8)),float(np.percentile(s,32)),s))*(1-.65*oxide)
rng=np.random.default_rng(261121);line=gaussian_filter(rng.normal(size=w).astype(np.float32),.075/(L/(w-1)));line=(line-np.percentile(line,5))/max(float(np.percentile(line,95)-np.percentile(line,5)),1e-8);intermittent=ss(.40,.72,line)[None,:];oldwear=np.asarray(Image.open(OLD/'surface09/wear.png'),dtype=np.float32)/255;edge=oldwear*intermittent
# Existing physical notches add localized wear; their positions come from the saved sculpt, not noise.
f=np.load(OLD/'09_pitted_iron/sculpt_fields.npz');rest=f['local_rest'];delta=f['local_deformed']-rest;mask=(rest[:,2]>1.75)&(rest[:,1]>-1.735);damage=np.zeros(w,np.float32);idx=np.clip(((rest[mask,0]+2.73)/L*(w-1)).astype(int),0,w-1);np.maximum.at(damage,idx,np.maximum(-delta[mask,1],0));damage=gaussian_filter(damage,.015/(L/(w-1)));damage=ss(.001,.008,damage);edge=np.maximum(edge,.8*damage[None,:]*np.exp(-((H-Y)/.026)**2));wear=np.maximum(body,edge);proximity=1-ss(.014,.040,np.minimum(Y,H-Y));oxide=np.maximum(oxide,.86*proximity*(1-edge));oxide*=1-.85*wear
for name,a in [('oxide.png',oxide),('wear.png',wear),('roughness.png',rough)]:Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).save(F/name)
np.savez_compressed(F/'fields.npz',oxide=oxide,wear=wear,roughness=rough,damage=damage);(F/'design.json').write_text(json.dumps(dict(surface_relief_unchanged=True,source='Independent roughness sources, intermittent edge proximity and saved actual damage geometry',edge_pattern_seed=261121,metal_tint='Neutral clean iron, no golden edge color'),indent=2));print('Prepared independent scale and intermittent wear masks')
