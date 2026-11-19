"""Reference guided height interpretation. This is not a measured surface scan."""
from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,map_coordinates,distance_transform_edt
P=Path(__file__).resolve().parent;out=P/'F_reference';out.mkdir(exist_ok=True)
h,w=736,2016;X,Y=np.meshgrid(np.linspace(-2.55,2.55,w),np.linspace(-.84,-2.2175,h));dx=5.1/(w-1);dy=1.3775/(h-1)
# Perspective rectify the owner's lower front wooden panel, excluding the metal.
src=Image.open(P.parents[1]/'reference.png').convert('RGB');a=np.asarray(src,float)/255
corners=np.array([[467,748],[1070,714],[1070,908],[473,939]],float)
uv=np.array([[0,0],[1,0],[1,1],[0,1]],float);A=[];bb=[]
for (u,v),(x,y) in zip(uv,corners):A.extend([[u,v,1,0,0,0,-u*x,-v*x],[0,0,0,u,v,1,-u*y,-v*y]]);bb.extend([x,y])
H=np.r_[np.linalg.solve(A,bb),1].reshape(3,3);U,V=np.meshgrid(np.linspace(0,1,w),np.linspace(0,1,h));q=H@np.array([U.ravel(),V.ravel(),np.ones(U.size)]);sx=(q[0]/q[2]).reshape(h,w);sy=(q[1]/q[2]).reshape(h,w)
rect=np.stack([map_coordinates(a[:,:,c],[sy,sx],order=1,mode='nearest') for c in range(3)],axis=2)
maskim=Image.new('L',src.size,0);d=ImageDraw.Draw(maskim);d.polygon([(609,578),(944,578),(944,686),(914,712),(914,815),(802,919),(641,824),(641,705),(609,684)],fill=255)
mask=map_coordinates(np.asarray(maskim,float),[sy,sx],order=0)>0
# Unseen areas under the lock use nearby right hand timber, never projected metal.
u2=.77+.20*np.mod(U*2.2,1);q2=H@np.array([u2.ravel(),V.ravel(),np.ones(U.size)]);s2x=(q2[0]/q2[2]).reshape(h,w);s2y=(q2[1]/q2[2]).reshape(h,w)
fill=np.stack([map_coordinates(a[:,:,c],[s2y,s2x],order=1,mode='nearest') for c in range(3)],axis=2)
feather=gaussian_filter(mask.astype(float),6);rect=rect*(1-feather[:,:,None])+fill*feather[:,:,None]
Image.fromarray(np.uint8(rect*255)).save(out/'rectified_source.jpg')
lum=np.dot(rect,[.2126,.7152,.0722]);log=np.log(np.maximum(lum,.01));broad=gaussian_filter(log,(.06/dy,.18/dx));detail=log-broad
lo,hi=np.percentile(detail,[6,88]);t=np.clip((detail-lo)/(hi-lo),0,1)
def ss(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
# Flat wood plates and narrow recessed grain, rather than broad swollen ridges.
height=-.039*(1-ss(.02,.72,t))**1.25
height=gaussian_filter(height,(.0016/dy,.0018/dx))
# Retain the reference grain shapes, with independent scanned microscopic fibers.
scan=np.load(P/'C_scan/surface.npz')['height'];scan=scan-gaussian_filter(scan,(.012/dy,.08/dx));height+=.16*scan
low=gaussian_filter(height,(.0015/dy,.0015/dx));fine=height-low;gy,gx=np.gradient(fine,dy,dx);n=np.stack([-gx,gy,np.ones_like(gx)],axis=2);n/=np.linalg.norm(n,axis=2)[:,:,None]
# Remove reference light intensity from pigmentation. Use only broad chromatic stains.
chrom=rect/np.maximum(lum[:,:,None],.01);chrom=np.stack([gaussian_filter(chrom[:,:,c],(.04/dy,.09/dx)) for c in range(3)],axis=2);chrom/=np.median(chrom,axis=(0,1));chrom=np.clip(chrom**.25,.85,1.15)
color=np.array([.52,.26,.12])*chrom;stain=.12*np.exp(-((X+1.5)/.6)**2-((Y+1.6)/.4)**2);color*= (1-stain)[:,:,None]
cavity=ss(.032,.038,-low);color*= (1-.12*cavity)[:,:,None]
rough=np.clip(.64+.05*cavity+.025*(scan/np.std(scan)),.54,.79)
def save(name,a):
 a=np.pad(a,((16,16),(16,16))+(((0,0),) if a.ndim==3 else ()),mode='edge');Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).save(out/name)
save('albedo.png',color);save('normal.png',n*.5+.5);save('roughness.png',rough);np.savez_compressed(out/'surface.npz',height=low.astype('float32'));np.savez_compressed(out/'master_height.npz',height=height.astype('float32'))
Image.fromarray(np.uint16(np.clip((height+.06)/.06,0,1)*65535+.5)).save(out/'height16.png')
(out/'design.json').write_text(json.dumps(dict(source='Owner reference guided relief interpretation, not a measured scan',corners=corners.tolist(),occluded_area='right panel timber fill',pigment='broad chroma only, reference intensity discarded',relief_min=float(height.min()),relief_max=float(height.max()),fine_detail='CC0 Rough Wood residual'),indent=2))
