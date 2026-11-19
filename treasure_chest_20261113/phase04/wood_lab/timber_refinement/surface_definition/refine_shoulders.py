from pathlib import Path
import numpy as np,json,shutil
from scipy.ndimage import gaussian_filter
from scipy.signal import find_peaks
from PIL import Image
D=Path(__file__).resolve().parent;W=D.parent;A=W/'AI_core_definition';C=W/'AJ_flat_fiber_faces';C.mkdir(exist_ok=True);a=np.load(A/'master_height.npz');full=a['height'];delta=a['delta'];L=np.load(D/'layers.npz');core=L['core'];h,w=full.shape;dx,dy=5.1/(w-1),1.3775/(h-1)
def resize(a):return np.asarray(Image.fromarray(a.astype('float32')).resize((w,h),Image.Resampling.BICUBIC),dtype='float32')
M=np.load(W/'grain_hierarchy/detail_layers.npz');m=resize(M['medium']+M['knot']);m=gaussian_filter(m,(.002/dy,.004/dx));target=m.copy();pins=np.ones_like(m);rng=np.random.default_rng(161149);vari=gaussian_filter(rng.uniform(size=w).astype('float32'),.07/dx);vari=(vari-vari.mean())/max(float(vari.std()),1e-8);width=np.clip(.70+.06*vari,.58,.80);count=0
for col in range(w):
 z=m[:,col];valleys,_=find_peaks(-z,prominence=.0045,distance=max(7,int(.020/dy)))
 for j,v in enumerate(valleys):
  pins[max(0,v-2):min(h,v+3),col]=0
  prev=valleys[j-1] if j else 0;nxt=valleys[j+1] if j+1<len(valleys) else h-1;l=prev+int(np.argmax(z[prev:v+1]));r=v+int(np.argmax(z[v:nxt+1]))
  for ids in [np.arange(v,l-1,-1),np.arange(v,r+1)]:
   depth=z[ids[-1]]-z[v]
   if len(ids)*dy<.055 or depth<.006:continue
   t=np.linspace(0,1,len(ids),dtype='float32');progress=np.minimum(t/width[col],1);new=z[v]+depth*progress;blend=np.clip((t-.10)/.15,0,1);blend=blend*blend*(3-2*blend);target[ids,col]=z[ids]+(new-z[ids])*blend;count+=1
profile=gaussian_filter(target-m,(.0018/dy,.005/dx));X,Y=np.meshgrid(np.linspace(-2.55,2.55,w,dtype='float32'),np.linspace(-.84,-2.2175,h,dtype='float32'))
def ss(a,b,v):q=np.clip((v-a)/(b-a),0,1);return q*q*(3-2*q)
protect=1-ss(.003,.012,-resize(M['fractures']));away=ss(.25,.38,np.hypot(X+1.31,Y+1.35));edge=np.minimum.reduce([2.35-abs(X),Y+2.16,-.8625-Y]);profile*=protect*away*ss(.02,.075,edge)*.58;profile=np.clip(profile,-.003,.006)*pins;new=np.minimum(full+profile,0);profile=new-full;geo=np.load(A/'surface.npz')['height'];lo=gaussian_filter(profile,(.0038/dy,.0038/dx));lo=np.asarray(Image.fromarray(lo).resize((geo.shape[1],geo.shape[0]),Image.Resampling.BICUBIC),dtype='float32');np.savez_compressed(C/'surface.npz',height=np.minimum(geo+lo,0));np.savez_compressed(C/'master_height.npz',height=new,delta=delta+profile);np.savez_compressed(D/'shoulder_correction.npz',height=profile)
for name in ['albedo.png','roughness.png','normal_masks.npz']:shutil.copy2(A/name,C/name)
d=json.loads((A/'design.json').read_text());d.update(source='AI with a partial planar reconstruction only on broad rounded grain shoulders',broad_shoulder_sides=count,minimum_shoulder_width=.055,blend=.58,variable_plateau_onset=[.58,.80],core_and_primary_fractures_protected=True,channel_centers_and_bottom_depths_preserved=True,profile_min=float(profile.min()),profile_max=float(profile.max()),height_min=float(new.min()));(C/'design.json').write_text(json.dumps(d,indent=2));print('Prepared broad shoulder control',count,float(profile.min()),float(profile.max()),flush=True)
