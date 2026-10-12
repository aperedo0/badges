"""Calibrated front-look transfer onto the back's continuous ribbon atlas."""
from pathlib import Path
import numpy as np,json,sys
from PIL import Image
from scipy.ndimage import map_coordinates,gaussian_filter
ROOT=Path(__file__).resolve().parents[1];w=Path(json.loads((ROOT/'manifest.json').read_text())['platinum']['work'])
sys.path.insert(0,str(ROOT.parent/'platinum_20261009/scripts'))
from solve import inv_agx,to_screen,encode
G=np.load(ROOT/'platinum_source_atlas_geometry.npz');p=G['p'];f=G['f'];uv=G['uv']
values=np.zeros((len(p),2));count=np.zeros(len(p))
for k in range(3):np.add.at(values,f[:,k],uv[:,k]);np.add.at(count,f[:,k],1)
values/=count[:,None]
# Reuse the front occlusion classification from the atlas preparation.
N=1024;depth=np.full((N,N),-np.inf);gn=np.cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]])
for idx in np.where(gn[:,2]>0)[0]:
 xy=uv[idx]*[N-1,-(N-1)]+[0,N-1];z=p[f[idx],2];lo=np.maximum(0,np.floor(xy.min(0)).astype(int));hi=np.minimum(N-1,np.ceil(xy.max(0)).astype(int));x0,y0=lo;x1,y1=hi
 if x1<x0 or y1<y0:continue
 a=xy[1]-xy[0];b=xy[2]-xy[0];den=a[0]*b[1]-a[1]*b[0]
 if abs(den)<1e-9:continue
 yy,xx=np.mgrid[y0:y1+1,x0:x1+1];uu=((xx-xy[0,0])*b[1]-(yy-xy[0,1])*b[0])/den;vv=(a[0]*(yy-xy[0,1])-a[1]*(xx-xy[0,0]))/den
 inside=(uu>=-.02)&(vv>=-.02)&(uu+vv<=1.02);zz=z[0]+uu*(z[1]-z[0])+vv*(z[2]-z[0]);q=depth[y0:y1+1,x0:x1+1];q[inside]=np.maximum(q[inside],zz[inside])
ids=np.arange(len(p)).reshape(-1,28)[:,np.arange(2,13)];coord=values[ids];px=np.clip(np.rint(coord[...,0]*(N-1)).astype(int),0,N-1);py=np.clip(np.rint((1-coord[...,1])*(N-1)).astype(int),0,N-1);visible=p[ids,2]>=depth[py,px]-.025
front_screen=to_screen(p[ids].reshape(-1,3)).reshape(768,11,2)
rearids=np.arange(768)[:,None]*28+(28-np.arange(2,13))[None,:];rp=p[rearids]*[-1,1,-1];rear_screen=to_screen(rp.reshape(-1,3)).reshape(768,11,2)
ref=np.asarray(Image.open(w/'current/front.png').convert('RGB'),float)/255
cal=np.asarray(Image.open(w/'candidates/11/back_calibration.png').convert('RGB'),float)/255
def sample(im,scr):return np.stack([map_coordinates(im[:,:,c],[scr[:,:,1]-.5,scr[:,:,0]-.5],order=1,mode='nearest') for c in range(3)],-1)
target=sample(ref,front_screen)
for k in range(11):
 valid=np.where(visible[:,k])[0];periodic=np.r_[valid-768,valid,valid+768]
 for c in range(3):target[:,k,c]=np.interp(np.arange(768),periodic,np.tile(target[valid,k,c],3))
# Match screen-left and screen-right when the object faces backwards.
# The continuous trefoil's parameter reflection is j -> 767-j.
target=target[::-1].copy()
light_obs=sample(cal,rear_screen)
# Exclude mixed background, saturated values and hidden rear crossing samples.
# Reject points hidden by the other ribbon on the actual back, too.
whole_rear=p*[-1,1,-1];screen=to_screen(whole_rear);zbuffer=np.full((2622,1206),-np.inf)
for tri in f:
 xyz=whole_rear[tri];normal=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0])
 if normal@((xyz.mean(0))-np.array([0,1.8,23]))>=0:continue
 xy=screen[tri];lo=np.maximum(0,np.floor(xy.min(0)).astype(int));hi=np.minimum([1205,2621],np.ceil(xy.max(0)).astype(int));x0,y0=lo;x1,y1=hi
 if x1<x0 or y1<y0:continue
 a=xy[1]-xy[0];b=xy[2]-xy[0];den=a[0]*b[1]-a[1]*b[0]
 if abs(den)<1e-9:continue
 yy,xx=np.mgrid[y0:y1+1,x0:x1+1];u=((xx-xy[0,0])*b[1]-(yy-xy[0,1])*b[0])/den;v=(a[0]*(yy-xy[0,1])-a[1]*(xx-xy[0,0]))/den
 inside=(u>=-.03)&(v>=-.03)&(u+v<=1.03);z=xyz[0,2]+u*(xyz[1,2]-xyz[0,2])+v*(xyz[2,2]-xyz[0,2]);q=zbuffer[y0:y1+1,x0:x1+1];q[inside]=np.maximum(q[inside],z[inside])
xx=np.clip(np.rint(rear_screen[:,:,0]).astype(int),0,1205);yy=np.clip(np.rint(rear_screen[:,:,1]).astype(int),0,2621)
rear_visible=rp[:,:,2]>=zbuffer[yy,xx]-.03
valid=(light_obs.max(-1)>.11)&(light_obs.max(-1)<.96)&rear_visible
# Interpolate invalid calibration points along the same ribbon section.
for k in range(11):
 ok=np.where(valid[:,k])[0];assert len(ok)>50,(k,len(ok));periodic=np.r_[ok-768,ok,ok+768]
 for c in range(3):light_obs[:,k,c]=np.interp(np.arange(768),periodic,np.tile(light_obs[ok,k,c],3))
print('invert measured light',flush=True);light=inv_agx(light_obs.reshape(-1,3)).reshape(768,11,3)/.12
print('invert front target',flush=True);total=inv_agx(target.reshape(-1,3)).reshape(768,11,3)
light=gaussian_filter(light,[1.2,.35,0]);alb=np.clip(total/np.maximum(light,1e-5),0,1);emit=np.clip(total-alb*light,0,3)
out=w/'candidates/12/atlas';out.mkdir(parents=True,exist_ok=True)
for name,data in [('color',alb),('emissive',emit/3)]:
 jj=np.linspace(0,768,1024,endpoint=False);kk=np.linspace(0,10,256);y,x=np.meshgrid(kk,jj,indexing='ij')
 output=np.stack([map_coordinates(data[:,:,c],[x,y],order=1,mode='grid-wrap') for c in range(3)],-1)
 Image.fromarray(encode(output)).save(out/f'rear_{name}.png')
np.savez_compressed(out/'solve.npz',target=target,total=total,light=light,front_visible=visible,calibration_valid=valid)
(out/'atlas.json').write_text(json.dumps({'method':'Native app front appearance transferred along the continuous ribbon, with front-hidden sections filled from visible neighboring sections. Rear albedo and emission solved against measured rear studio light. Thin side and bevel guards retain the installed front outline and avoid mixed silhouette pixels.','front_visible':visible.sum(0).tolist(),'rear_calibration_valid':valid.sum(0).tolist(),'emission_scale':3},indent=2)+'\n')
