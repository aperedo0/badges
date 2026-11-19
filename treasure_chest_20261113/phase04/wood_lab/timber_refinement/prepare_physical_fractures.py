from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import gaussian_filter,label,find_objects,distance_transform_edt,binary_closing,binary_opening
W=Path(__file__).resolve().parent;B=W/'O_timber_balanced';out=W/'P_physical_fractures';out.mkdir(exist_ok=True)
full=np.load(B/'master_height.npz')['height'].astype(float);h,w=full.shape;dx,dy=5.1/(w-1),1.3775/(h-1)
# Detect only elongated natural crevices, never invert the entire image as height.
rgb=np.asarray(Image.open(B/'albedo.png').convert('RGB'),float)[16:-16,16:-16]/255
lum=rgb@np.array([.2126,.7152,.0722]);local=gaussian_filter(lum,(.04/dy,.10/dx));contrast=(local-lum)/np.maximum(local,.02)
response=np.zeros_like(lum)
for scale in [.006,.012,.022]:
    sigma=(scale/dy,scale/dx)
    xx=gaussian_filter(lum,sigma,order=(0,2))/dx**2*scale**2
    yy=gaussian_filter(lum,sigma,order=(2,0))/dy**2*scale**2
    xy=gaussian_filter(lum,sigma,order=(1,1))/(dx*dy)*scale**2
    root=np.sqrt((xx-yy)**2+4*xy*xy)
    a=(xx+yy+root)/2;b=(xx+yy-root)/2
    large=np.where(abs(a)>abs(b),a,b);small=np.where(abs(a)>abs(b),b,a)
    line=np.maximum(large,0)*np.exp(-.5*(small/np.maximum(abs(large),1e-8)/.40)**2)
    response=np.maximum(response,line)
threshold=np.percentile(response,91)
mask=(response>threshold)&(contrast>.10)
mask=binary_closing(mask,structure=np.ones((2,3)))
components,count=label(mask)
keep=np.zeros(count+1,bool)
for i,slices in enumerate(find_objects(components),1):
    if slices is None:continue
    yy,xx=slices
    length=(xx.stop-xx.start)*dx;height=(yy.stop-yy.start)*dy
    area=np.sum(components[slices]==i)*dx*dy
    if length>.085 and length>height*1.5 and area>.00025:keep[i]=True
mask=keep[components]
assert mask.any(),'No coherent fractures found; do not build an empty correction'
distance=distance_transform_edt(~mask,sampling=(dy,dx))
weight=np.clip(gaussian_filter(np.maximum(contrast,0),(.003/dy,.003/dx))/.30,.35,1)
core=gaussian_filter(mask.astype(float),(.0015/dy,.0015/dx))
cuts=.022*core*weight+.004*np.exp(-(distance/.006)**2)*weight
full-=cuts
low=gaussian_filter(full,(.0045/dy,.0045/dx));res=full-low;gy,gx=np.gradient(res,dy,dx);n=np.stack([-gx,gy,np.ones_like(gx)],2);n/=np.linalg.norm(n,axis=2)[:,:,None]
def save(name,a):
    pads=((16,16),(16,16))+(((0,0),) if a.ndim==3 else ())
    Image.fromarray(np.uint8(np.clip(np.pad(a,pads,mode='edge'),0,1)*255+.5)).save(out/name)
save('albedo.png',rgb)
rough=np.asarray(Image.open(B/'roughness.png').convert('L'),float)[16:-16,16:-16]/255
save('roughness.png',rough);save('normal.png',n*.5+.5)
np.savez_compressed(out/'surface.npz',height=low.astype('float32'));np.savez_compressed(out/'master_height.npz',height=full.astype('float32'),cut=cuts.astype('float32'))
Image.fromarray(np.uint8(mask)*255).save(out/'selected_fractures.png')
overlay=rgb.copy();overlay[mask]=overlay[mask]*.3+np.array([0,.8,.8])*.7;Image.fromarray(np.uint8(np.clip(overlay,0,1)*255+.5)).save(out/'fracture_overlay.png')
d=json.loads((B/'design.json').read_text());d.update(refinement='Selected elongated natural fractures reconstructed as physical cuts after clay diagnosis; pigment unchanged',normal_split=.0045,fracture_area=float(mask.mean()),fracture_components=int(keep.sum()),height_min=float(full.min()),no_global_displacement_or_pigment_increase=True);(out/'design.json').write_text(json.dumps(d,indent=2))
print('Physical fractures',int(keep.sum()),float(mask.mean()),float(full.min()),flush=True)
