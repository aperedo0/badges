from pathlib import Path
import numpy as np,json,shutil
from scipy.ndimage import gaussian_filter
from scipy.signal import find_peaks
D=Path(__file__).resolve().parent;W=D.parent;A=W/'AA_rich_fibers';M=np.load(W/'grain_hierarchy/detail_layers.npz');m=(M['medium']+M['knot']).astype(float);h,w=m.shape;dx,dy=5.1/(w-1),1.3775/(h-1);X,Y=np.meshgrid(np.linspace(-2.55,2.55,w),np.linspace(-.84,-2.2175,h));smooth=gaussian_filter(m,(.0020/dy,.006/dx));target=smooth.copy();changed=0
# Retain every channel center and depth. Straighten only the rounded middle of broad shoulders.
for col in range(w):
 a=smooth[:,col];valleys,_=find_peaks(-a,prominence=.0035,distance=max(5,int(.016/dy)))
 for j,v in enumerate(valleys):
  lprev=valleys[j-1] if j else 0;rnext=valleys[j+1] if j+1<len(valleys) else h-1;l=lprev+int(np.argmax(a[lprev:v+1]));r=v+int(np.argmax(a[v:rnext+1]))
  for ids in [np.arange(l,v+1),np.arange(r,v-1,-1)]:
   if len(ids)<9:continue
   z=a[ids];depth=z[0]-z[-1]
   if depth<.005:continue
   progress=(z[0]-z)/depth;p=np.flatnonzero(progress>.12);q=np.flatnonzero(progress>.88)
   if len(p)==0 or len(q)==0:continue
   i0,i1=int(p[0]),int(q[0])
   if i1-i0<4:continue
   # Piecewise planar wood side, with the original rounded end transitions retained as bevels.
   segment=ids[i0:i1+1];line=np.linspace(z[i0],z[i1],len(segment));target[segment,col]=line;changed+=1
profile=gaussian_filter(target-smooth,(.001/dy,.006/dx));radius=np.hypot(X+1.31,Y+1.35);blend=np.clip((radius-.19)/.11,0,1);blend=blend*blend*(3-2*blend);cut=-M['fractures'].astype(float);protect=1-np.clip((cut-.003)/.008,0,1);profile*=blend*protect*.85
fullA=np.load(A/'master_height.npz')['height'].astype(float);base=np.load(W/'U_scan_fibers/master_height.npz')['height'].astype(float);geo=np.load(W/'U_scan_fibers/surface.npz')['height'].astype(float);full=np.minimum(fullA+profile,0);delta=full-base;geometry=np.minimum(geo+gaussian_filter(delta,(.0038/dy,.0038/dx)),0);C=W/'AB_carved_profiles';C.mkdir(exist_ok=True)
np.savez_compressed(C/'surface.npz',height=geometry.astype('float32'));np.savez_compressed(C/'master_height.npz',height=full.astype('float32'),delta=delta.astype('float32'));np.savez_compressed(D/'profile_correction.npz',height=profile.astype('float32'))
for role in ['albedo','roughness']:shutil.copy2(A/(role+'.png'),C/(role+'.png'))
d=json.loads((A/'design.json').read_text());d.update(source='AA internal fibers with rounded channel shoulders locally replaced by planar wood side profiles',channel_centers_and_bottom_depths_preserved=True,primary_fractures_protected=True,core_outline_protected=True,profile_sides=changed,profile_delta_min=float(profile.min()),profile_delta_max=float(profile.max()),height_min=float(full.min()));(C/'design.json').write_text(json.dumps(d,indent=2));print(json.dumps(d),flush=True)
