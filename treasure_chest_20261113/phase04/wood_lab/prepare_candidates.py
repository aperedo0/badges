from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import gaussian_filter,zoom
P=Path(__file__).resolve().parent;R=P.parents[1];B=R/'phase03/stylized_wood45/candidate05'
D=json.loads((B/'design.json').read_text());pad=D['padding'];height=np.load(B/'physical_height.npz')['height'];h,w=height.shape;dx=5.1/(w-1);dy=1.3775/(h-1)
def save(out,name,a):
 a=np.pad(a,((pad,pad),(pad,pad))+(((0,0),) if a.ndim==3 else ()),mode='edge');Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).save(out/name)
def normal(a):
 gy,gx=np.gradient(a,dy,dx);n=np.stack([-gx,gy,np.ones_like(gx)],axis=2);n/=np.linalg.norm(n,axis=2)[:,:,None];return n*.5+.5
d=P/'B_true_relief';d.mkdir(exist_ok=True);low=gaussian_filter(height,1.5)
np.savez_compressed(d/'surface.npz',height=low.astype('float32'))
save(d,'normal.png',normal(height-low));
for n in ['albedo','roughness']:Image.open(B/'textures'/('wood_'+n+'.png')).save(d/(n+'.png'))
# One continuous scanned board, with grain rotated along the plank's length.
src=P/'resources/rough_wood';out=P/'C_scan';out.mkdir(exist_ok=True)
for role,pat in [('color','*diff*'),('height','*disp*'),('rough','*rough*')]:
 im=Image.open(next(src.glob(pat))).crop((500,0,1000,2048)).transpose(Image.Transpose.ROTATE_90).resize((w,h),Image.Resampling.LANCZOS)
 a=np.asarray(im,float)
 if role=='color':
  rgb=a/255;lum=np.dot(rgb,[.2126,.7152,.0722]);broad=gaussian_filter(lum,55);variation=np.clip((lum/np.maximum(broad,.03))**.42,.65,1.3)
  # Intrinsic chestnut color with measured low frequency scanned variation.
  rgb=np.array([.40,.205,.112])[None,None,:]*variation[:,:,None]*(.85+.30*broad/np.median(broad))[:,:,None]
  save(out,'albedo.png',rgb)
 elif role=='height':
  if a.ndim>2:a=a[:,:,0]
  a=(a-np.percentile(a,2))/(np.percentile(a,98)-np.percentile(a,2));a=np.clip(a,0,1)
  full=(a-1)*.045;low=gaussian_filter(full,1.5);np.savez_compressed(out/'surface.npz',height=low.astype('float32'));save(out,'normal.png',normal(full-low))
 else:save(out,'roughness.png',np.clip(a/255*.30+.43,.48,.85))
(P/'candidate_design.json').write_text(json.dumps(dict(B=dict(source=str(B),height_depth=float(height.min()),normal='high frequency residual only'),C=dict(source='Poly Haven rough_wood, CC0',crop=[500,0,1000,2048],grain_rotation=90,relief_range=.045,pigment='chestnut with scanned variation'),bounds=D['bounds'],padding=pad),indent=2))
