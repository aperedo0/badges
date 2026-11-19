from pathlib import Path
import numpy as np,json,shutil
from scipy.ndimage import gaussian_filter,map_coordinates,maximum_filter,minimum_filter
from PIL import Image
D=Path(__file__).resolve().parent;W=D.parent;A=W/'AW_depth_hierarchy';C=W/'AZ_edge_definition';C.mkdir(exist_ok=True)
s=np.load(A/'master_height.npz');H=s['height'];layers=np.load(W/'grain_hierarchy/detail_layers.npz');h,w=layers['medium'].shape;dx,dy=5.1/(w-1),1.3775/(h-1)
def resize(a,shape):return np.asarray(Image.fromarray(a.astype('float32')).resize(shape,Image.Resampling.BICUBIC),dtype=np.float32)
def ss(a,b,v):t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
X,Y=np.meshgrid(np.linspace(-2.55,2.55,w,dtype=np.float32),np.linspace(-.84,-2.2175,h,dtype=np.float32));angle=np.load(W/'final_fibers/broken_fiber_layers.npz')['angle'];nx,ny=-np.sin(angle),np.cos(angle)
m=gaussian_filter(resize(H,(w,h))-layers['fractures'],(.006/dy,.012/dx))
def sample(a,x,y):return map_coordinates(a,[(y+.84)/-1.3775*(h-1),(x+2.55)/5.1*(w-1)],order=1,mode='nearest')
epsilon=.0075;p=sample(m,X+epsilon*nx,Y+epsilon*ny);n=sample(m,X-epsilon*nx,Y-epsilon*ny);slope=(p-n)/(2*epsilon);curve=(p-2*m+n)/(epsilon**2)
# A bounded shock step steepens existing broad transitions without changing the extrema or adding features.
span=maximum_filter(m,size=(int(.09/dy)|1,int(.12/dx)|1))-minimum_filter(m,size=(int(.09/dy)|1,int(.12/dx)|1));width=np.sqrt(np.maximum(span,.0001)/np.maximum(np.abs(curve),.1));resolved=ss(.012,.025,width);edge=ss(.07,.18,np.abs(slope))*(1-ss(.65,1.1,np.abs(slope)))
fracture_guard=1-ss(.0015,.009,-layers['fractures']);core_guard=ss(.25,.40,np.hypot(X+1.31,Y+1.35));bound=np.minimum.reduce([2.35-abs(X),Y+2.16,-.8625-Y]);mask=resolved*edge*fracture_guard*core_guard*ss(.025,.09,bound)
correction=-np.tanh(curve/10)*np.abs(slope)*.0035;correction=np.clip(correction,-.0014,.0014)*mask;correction=gaussian_filter(correction,(.0015/dy,.003/dx))*fracture_guard*core_guard
add=resize(correction,(H.shape[1],H.shape[0]));full=np.minimum(H+add,0);add=full-H;geo=np.load(A/'surface.npz')['height'];low=gaussian_filter(add,(.0038/(1.3775/(H.shape[0]-1)),.0038/(5.1/(H.shape[1]-1))));low=resize(low,(geo.shape[1],geo.shape[0]));np.savez_compressed(C/'surface.npz',height=np.minimum(geo+low,0));np.savez_compressed(C/'master_height.npz',height=full,delta=s['delta']+add)
for name in ['albedo.png','roughness.png','normal_masks.npz']:shutil.copy2(A/name,C/name)
np.savez_compressed(D/'edge_fields.npz',mask=mask,correction=correction,slope=slope,curvature=curve)
(C/'design.json').write_text(json.dumps(dict(source='AW_depth_hierarchy',change='One bounded shock step restricted to existing resolved broad grain transitions',max_change=[float(add.min()),float(add.max())],fine_band_unchanged=True,core_primary_fractures_boundaries_protected=True,new_features=0,material_lighting_unchanged=True),indent=2));(C/'.gitignore').write_text('geometry.blend\nnormal_frames.npz\n')
print('Prepared bounded broad transitions',float(add.min()),float(add.max()))
