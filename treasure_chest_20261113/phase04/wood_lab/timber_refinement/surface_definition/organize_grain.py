from pathlib import Path
import numpy as np,json,shutil
from scipy.ndimage import gaussian_filter,map_coordinates
from PIL import Image
D=Path(__file__).resolve().parent;W=D.parent;A=W/'AI_core_definition';C=W/'AK_cohesive_grain';C.mkdir(exist_ok=True)
M=np.load(W/'grain_hierarchy/detail_layers.npz');m=(M['medium']+M['knot']).astype('float32');h,w=m.shape;dx,dy=5.1/(w-1),1.3775/(h-1);m=gaussian_filter(m,(.003/dy,.007/dx));X,Y=np.meshgrid(np.linspace(-2.55,2.55,w,dtype='float32'),np.linspace(-.84,-2.2175,h,dtype='float32'));angle=np.load(W/'final_fibers/broken_fiber_layers.npz')['angle'].astype('float32')
def ss(a,b,v):q=np.clip((v-a)/(b-a),0,1);return q*q*(3-2*q)
def sample(a,x,y):return map_coordinates(a,[(y+.84)/-1.3775*(h-1),(x+2.55)/5.1*(w-1)],order=1,mode='nearest')
# Curved grain transport avoids independent column profiles and their vertical discontinuities.
coords=[]
for distance in [-.075,-.050,-.025,0,.025,.050,.075]:
 xx=X.copy();yy=Y.copy();steps=max(1,int(abs(distance)/.0125+.5));step=distance/steps
 for _ in range(steps):
  theta=sample(angle,xx,yy);xx+=step*np.cos(theta);yy+=step*np.sin(theta)
 coords.append(np.array([(yy+.84)/-1.3775*(h-1),(xx+2.55)/5.1*(w-1)],dtype='float32'))
def extent(a,maximum):
 out=a.copy()
 for q in coords:
  v=map_coordinates(a,q,order=1,mode='nearest')
  if maximum:np.maximum(out,v,out=out)
  else:np.minimum(out,v,out=out)
 return out
closed=extent(extent(m,True),False);opened=extent(extent(m,False),True)
# Connect shallow interruptions and trim isolated high lumps along their existing grain paths.
fill=np.clip(closed-m,0,.0045);trim=np.clip(opened-m,-.0030,0);delta=.72*fill+.28*trim
# Major fractures, deep grain channels, knot outline and all contact boundaries are protected.
cut=-M['fractures'];guard=1-ss(.0015,.009,cut);channel=1-ss(.008,.016,-m);knot=ss(.26,.40,np.hypot(X+1.31,Y+1.35));edge=np.minimum.reduce([2.35-abs(X),Y+2.16,-.8625-Y]);boundary=ss(.025,.09,edge)
# Correction is driven by local fragmentation response, not a blanket change to detail amplitude.
response=ss(.0007,.0025,np.maximum(fill,-trim));mask=gaussian_filter(response,(.008/dy,.018/dx))*guard*channel*knot*boundary;delta=gaussian_filter(delta,(.0015/dy,.003/dx))*mask
source=np.load(A/'master_height.npz');H=source['height'];newdelta=np.asarray(Image.fromarray(delta).resize((H.shape[1],H.shape[0]),Image.Resampling.BICUBIC),dtype='float32');full=np.minimum(H+newdelta,0);newdelta=full-H
geo=np.load(A/'surface.npz')['height'];lo=gaussian_filter(newdelta,(.0038/(1.3775/(H.shape[0]-1)),.0038/(5.1/(H.shape[1]-1))));lo=np.asarray(Image.fromarray(lo).resize((geo.shape[1],geo.shape[0]),Image.Resampling.BICUBIC),dtype='float32');np.savez_compressed(C/'surface.npz',height=np.minimum(geo+lo,0));np.savez_compressed(C/'master_height.npz',height=full,delta=source['delta']+newdelta)
for name in ['albedo.png','roughness.png','normal_masks.npz']:shutil.copy2(A/name,C/name)
np.savez_compressed(D/'cohesion_layers.npz',medium_before=m,medium_after=m+delta,correction=delta,mask=mask,closing_fill=fill,opening_trim=trim)
d=json.loads((A/'design.json').read_text());d.update(source='AI with selective flow aligned organization of medium formations; tertiary fibers, material and fracture source unchanged',organization_halfspan=.075,organization_method='Curved directional closing of short interruptions and opening of isolated lumps, restricted by local fragmentation response',correction_min=float(newdelta.min()),correction_max=float(newdelta.max()),fine_layers_preserved=True,core_and_major_fractures_protected=True,new_cracks=0,new_fibers=0,height_min=float(full.min()));(C/'design.json').write_text(json.dumps(d,indent=2));print(json.dumps(d),flush=True)
