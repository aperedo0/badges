from pathlib import Path
import numpy as np,json,shutil
from scipy.ndimage import gaussian_filter,map_coordinates
from PIL import Image
D=Path(__file__).resolve().parent
# Reuse the existing curved transport coordinates and physical grid.
code=(D/'organize_grain.py').read_text().split('closed=')[0];exec(compile(code,'existing_grain_transport','exec'))
A=W/'AM_readable_layers';C=W/'AN_layered_hardwood';C.mkdir(exist_ok=True)
def resize(a,shape):return np.asarray(Image.fromarray(a.astype('float32')).resize(shape,Image.Resampling.BICUBIC),dtype='float32')
current=np.load(A/'master_height.npz');H=current['height'];origin=resize(np.load(W/'AI_core_definition/master_height.npz')['height'],(w,h));primary=M['broad']+M['medium']+M['knot']+M['fractures'];secondary=origin-primary
mid=gaussian_filter(secondary,(.0045/dy,.010/dx))-gaussian_filter(secondary,(.032/dy,.13/dx));total=np.zeros_like(mid);weight=0
for q,k in zip(coords,[1,2,3,4,3,2,1]):total+=k*map_coordinates(mid,q,order=1,mode='nearest');weight+=k
aligned=total/weight;oldr=np.sqrt(gaussian_filter(mid*mid,(.025/dy,.10/dx)));newr=np.sqrt(gaussian_filter(aligned*aligned,(.025/dy,.10/dx)));gain=np.clip(oldr/np.maximum(newr,.00008),.85,1.4);aligned*=gain
gy,gx=np.gradient(mid,dy,dx);gy=-gy;along=gx*np.cos(angle)+gy*np.sin(angle);across=-gx*np.sin(angle)+gy*np.cos(angle);a=gaussian_filter(along*along,(.012/dy,.045/dx));b=gaussian_filter(across*across,(.012/dy,.045/dx));crosswise=a/np.maximum(a+b,1e-8)
face=np.load(W/'final_fibers/structure_layers.npz')['plate'];guard=1-ss(.0015,.009,-M['fractures']);knot=ss(.28,.40,np.hypot(X+1.31,Y+1.35));edge=np.minimum.reduce([2.35-abs(X),Y+2.16,-.8625-Y]);mask=ss(.22,.52,crosswise)*ss(.00025,.0009,oldr)*face*guard*knot*ss(.025,.09,edge)
correction=np.clip((aligned-mid)*mask*.82,-.0035,.0035);correction=gaussian_filter(correction,(.0013/dy,.003/dx));addition=resize(correction,(H.shape[1],H.shape[0]));full=np.minimum(H+addition,0);addition=full-H;geo=np.load(A/'surface.npz')['height'];lo=gaussian_filter(addition,(.0038/(1.3775/(H.shape[0]-1)),.0038/(5.1/(H.shape[1]-1))));lo=resize(lo,(geo.shape[1],geo.shape[0]));np.savez_compressed(C/'surface.npz',height=np.minimum(geo+lo,0));np.savez_compressed(C/'master_height.npz',height=full,delta=current['delta']+addition)
for name in ['albedo.png','roughness.png','normal_masks.npz']:shutil.copy2(A/name,C/name)
np.savez_compressed(D/'secondary_organization.npz',before=mid,after=mid+correction,mask=mask,correction=correction,crosswise_fraction=crosswise)
d=json.loads((A/'design.json').read_text());d.update(source='AM with selective alignment of crosswise secondary modulation; fine band and macro anatomy unchanged',secondary_policy='Transport existing middle band along grain, preserve local variance with gain limited to 1.4; blend only where crosswise response is high',new_fibers=0,new_cracks=0,secondary_correction_min=float(addition.min()),secondary_correction_max=float(addition.max()),height_min=float(full.min()));(C/'design.json').write_text(json.dumps(d,indent=2));print('Prepared secondary organization',float(addition.min()),float(addition.max()),flush=True)
