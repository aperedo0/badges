from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import gaussian_filter
W=Path(__file__).resolve().parent;P=W.parent;R=P/'resources/rough_wood';out=W/'M_scanned_knot';out.mkdir(exist_ok=True)
h,w=736,2016;dx,dy=5.1/(w-1),1.3775/(h-1);box=(160,279,500,1538)
def crop(pattern):
    im=Image.open(next(R.glob(pattern))).crop(box).transpose(Image.Transpose.ROTATE_270)
    return np.asarray(im.resize((w,h),Image.Resampling.BICUBIC),float)
rgb=crop('*diff*')/255
raw=crop('*disp*')
if raw.ndim==3:raw=raw[:,:,0]
lo,hi=np.percentile(raw,[2,98]);e=np.clip((raw-lo)/(hi-lo),0,1)
full=-.042*(1-e)**1.35
low=gaussian_filter(full,(.0045/dy,.0045/dx));res=full-low
gy,gx=np.gradient(res,dy,dx);normal=np.stack([-gx,gy,np.ones_like(gx)],2);normal/=np.linalg.norm(normal,axis=2)[:,:,None]
lum=rgb@np.array([.2126,.7152,.0722]);broad=gaussian_filter(lum,(.10/dy,.30/dx))
fine=np.clip((lum/np.maximum(broad,.01))**.78,.50,1.45)
large=np.clip((broad/np.median(broad))**.45,.80,1.20)
# Intrinsic chestnut pigment retains the scan's irregular worn fibers and stains.
color=np.array([.49,.238,.099])[None,None,:]*fine[:,:,None]*large[:,:,None]
chroma=rgb/np.maximum(lum[:,:,None],.01)
chroma/=np.median(chroma,axis=(0,1))
color*=np.clip(chroma,.90,1.10)
rough=crop('*rough*')
if rough.ndim==3:rough=rough[:,:,0]
rough=np.clip(.55+.30*rough/255,.55,.85)
def save(name,a):
    pads=((16,16),(16,16))+(((0,0),) if a.ndim==3 else ())
    Image.fromarray(np.uint8(np.clip(np.pad(a,pads,mode='edge'),0,1)*255+.5)).save(out/name)
save('albedo.png',color);save('roughness.png',rough);save('normal.png',normal*.5+.5)
np.savez_compressed(out/'surface.npz',height=low.astype('float32'));np.savez_compressed(out/'master_height.npz',height=full.astype('float32'))
Image.fromarray(np.uint16(np.clip((full+.05)/.05,0,1)*65535+.5)).save(out/'height16.png')
(out/'design.json').write_text(json.dumps(dict(source='Existing cached Poly Haven Rough Wood, newly selected naturally knotted interior board region',asset='https://polyhaven.com/a/rough_wood',license='CC0 1.0',crop=list(box),rotation='90 degrees clockwise',physical_aspect=5.1/1.3775,crop_aspect=(box[3]-box[1])/(box[2]-box[0]),depth_min=float(full.min()),normal_split=.0045,no_generated_rings_or_authored_parallel_channels=True,original_chest_preserved=True),indent=2))
print('Prepared coherent scanned knot foundation',float(full.min()),flush=True)
