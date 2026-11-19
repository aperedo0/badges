from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import gaussian_filter,grey_opening
W=Path(__file__).resolve().parent;B=W/'M_scanned_knot';out=W/'O_timber_balanced';out.mkdir(exist_ok=True)
full=np.load(B/'master_height.npz')['height'].astype(float);h,w=full.shape;dx,dy=5.1/(w-1),1.3775/(h-1)
broad=gaussian_filter(full,(.020/dy,.055/dx))
detail=full-broad
# Preserve longitudinal structural crevices; quiet isotropic pore chatter.
furrow=np.maximum(-detail,0)
furrow=grey_opening(furrow,size=(1,max(3,int(.042/dx))))
furrow=gaussian_filter(furrow,(.002/dy,.002/dx))
full=np.minimum(broad+.65*detail-.30*furrow,0)
low=gaussian_filter(full,(.0045/dy,.0045/dx));res=full-low;gy,gx=np.gradient(res,dy,dx);n=np.stack([-gx,gy,np.ones_like(gx)],2);n/=np.linalg.norm(n,axis=2)[:,:,None]
rgb=np.asarray(Image.open(B/'albedo.png').convert('RGB'),float)[16:-16,16:-16]/255
medium=np.stack([gaussian_filter(rgb[:,:,i],(.0045/dy,.010/dx)) for i in range(3)],2)
rgb=.75*rgb+.25*medium
rough=np.asarray(Image.open(B/'roughness.png').convert('L'),float)[16:-16,16:-16]/255
rough=gaussian_filter(rough,(.003/dy,.008/dx))
def save(name,a):
 pads=((16,16),(16,16))+(((0,0),) if a.ndim==3 else ())
 Image.fromarray(np.uint8(np.clip(np.pad(a,pads,mode='edge'),0,1)*255+.5)).save(out/name)
save('albedo.png',rgb);save('normal.png',n*.5+.5);save('roughness.png',rough)
np.savez_compressed(out/'surface.npz',height=low.astype('float32'));np.savez_compressed(out/'master_height.npz',height=full.astype('float32'))
d=json.loads((B/'design.json').read_text());d.update(refinement='Retain crisp middle scale fibers while moderating the highest pore contrast, retaining coherent scanned knot',depth_min=float(full.min()),normal_split=.0045);(out/'design.json').write_text(json.dumps(d,indent=2))
print('Prepared scale separation',float(full.min()),flush=True)
