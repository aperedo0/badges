from pathlib import Path
import numpy as np,json,shutil
from PIL import Image
from scipy.ndimage import gaussian_filter,map_coordinates
D=Path(__file__).resolve().parent;W=D.parent;A=W/'AT_hardwood_faces';C=W/'AW_depth_hierarchy';C.mkdir(exist_ok=True);M=np.load(W/'grain_hierarchy/detail_layers.npz');h,w=M['medium'].shape;dx,dy=5.1/(w-1),1.3775/(h-1);X,Y=np.meshgrid(np.linspace(-2.55,2.55,w,dtype='float32'),np.linspace(-.84,-2.2175,h,dtype='float32'));angle=np.load(W/'final_fibers/broken_fiber_layers.npz')['angle']
def ss(a,b,v):q=np.clip((v-a)/(b-a),0,1);return q*q*(3-2*q)
def resize(a,size):return np.asarray(Image.fromarray(a.astype('float32')).resize(size,Image.Resampling.BICUBIC),dtype='float32')
def sample(a,x,y):return map_coordinates(a,[(y+.84)/-1.3775*(h-1),(x+2.55)/5.1*(w-1)],order=1,mode='nearest')
s=np.load(A/'master_height.npz');H=s['height'];coarse=resize(H,(w,h));medium=gaussian_filter(coarse-M['fractures'],(.0035/dy,.008/dx));coords=[]
# Persistence across the local grain distinguishes narrow grain channels from broad formations.
for distance in [-.0225,-.015,-.0075,0,.0075,.015,.0225]:
 xx=X.copy();yy=Y.copy();steps=max(1,int(abs(distance)/.005+.5));step=distance/steps
 for _ in range(steps):
  phi=sample(angle,xx,yy)+np.pi/2;xx+=step*np.cos(phi);yy+=step*np.sin(phi)
 coords.append(np.array([(yy+.84)/-1.3775*(h-1),(xx+2.55)/5.1*(w-1)],dtype='float32'))
def extent(a,maximum):
 out=a.copy()
 for q in coords:
  v=map_coordinates(a,q,order=1,mode='nearest')
  if maximum:np.maximum(out,v,out=out)
  else:np.minimum(out,v,out=out)
 return out
closed=extent(extent(medium,True),False);response=np.maximum(closed-medium,0);guard=1-ss(.0015,.009,-M['fractures']);knot=ss(.25,.40,np.hypot(X+1.31,Y+1.35));edge=np.minimum.reduce([2.35-abs(X),Y+2.16,-.8625-Y]);mask=guard*knot*ss(.025,.09,edge)*ss(.0007,.002,response)
correction=np.minimum(.65*response,.012)*mask;correction=gaussian_filter(correction,(.0015/dy,.004/dx))*guard*knot;addition=resize(correction,(H.shape[1],H.shape[0]));full=np.minimum(H+addition,0);addition=full-H;geo=np.load(A/'surface.npz')['height'];lo=gaussian_filter(addition,(.0038/(1.3775/(H.shape[0]-1)),.0038/(5.1/(H.shape[1]-1))));lo=resize(lo,(geo.shape[1],geo.shape[0]));np.savez_compressed(C/'surface.npz',height=np.minimum(geo+lo,0));np.savez_compressed(C/'master_height.npz',height=full,delta=s['delta']+addition)
for name in ['albedo.png','roughness.png','normal_masks.npz']:shutil.copy2(A/name,C/name)
np.savez_compressed(D/'depth_hierarchy_layers.npz',medium=medium,persistent=closed,response=response,mask=mask,correction=correction)
d=json.loads((A/'design.json').read_text());d.update(source='AT with width selective depth grading: narrow grain channels remain secondary relief inside larger formations',cross_grain_halfspan=.0225,narrow_channel_retained_fraction=.35,primary_fractures_and_core_protected=True,fine_source_layer_retained=True,correction_max=float(addition.max()),new_cracks=0,new_fibers=0,height_min=float(full.min()));(C/'design.json').write_text(json.dumps(d,indent=2));(C/'.gitignore').write_text('geometry.blend\nnormal_frames.npz\n');print('Prepared grain depth hierarchy',float(addition.max()),flush=True)
