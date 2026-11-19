from pathlib import Path
import numpy as np,json,shutil
from PIL import Image
from scipy.ndimage import gaussian_filter
D=Path(__file__).resolve().parent;W=D.parent;A=W/'AW_depth_hierarchy';C=W/'AY_fiber_finish';C.mkdir(exist_ok=True)
for name in ['albedo.png','normal.png','master_height.npz','surface.npz','normal_masks.npz']:shutil.copy2(A/name,C/name)
r=np.asarray(Image.open(A/'roughness.png'),dtype=np.float32)/255
# Only the smoother existing wood patches receive a roughness floor. Existing rough regions remain.
h,w=r.shape;plate=np.load(W/'final_fibers/structure_layers.npz')['plate'];plate=np.asarray(Image.fromarray(plate).resize((4032,1472),Image.Resampling.BICUBIC),dtype=np.float32);plate=np.pad(np.clip(plate,0,1),32,mode='edge')
X,Y=np.meshgrid(np.linspace(-2.55,2.55,4032,dtype=np.float32),np.linspace(-.84,-2.2175,1472,dtype=np.float32));knot=np.exp(-(((X+1.31)/.14)**2+((Y+1.35)/.17)**2)*.5);knot=np.pad(knot,32,mode='edge')
weight=np.maximum(.8*plate,.7*knot);delta=np.maximum(.69-r,0)*weight*.85;delta=np.minimum(delta,.08)
Image.fromarray(np.uint8(np.clip(r+delta,0,1)*255+.5)).save(C/'roughness.png');(C/'design.json').write_text(json.dumps(dict(source='AW_depth_hierarchy',change='Roughness floor on smoother existing raised wood only',floor=.69,max_added_roughness=float(delta.max()),geometry_pigment_normal_light_unchanged=True),indent=2));(C/'.gitignore').write_text('geometry.blend\nnormal_frames.npz\n')
print('Prepared local finish control',float(delta.max()))
