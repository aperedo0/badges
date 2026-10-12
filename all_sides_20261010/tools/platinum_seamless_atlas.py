"""Reuse the installed front polish, filling only its hidden ribbon areas."""
from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import map_coordinates
ROOT=Path(__file__).resolve().parents[1]
w=Path(json.loads((ROOT/'manifest.json').read_text())['platinum']['work'])
g=np.load(ROOT/'platinum_source_atlas_geometry.npz');p=g['p'];f=g['f'];uv=g['uv'];n=g['n']
values=np.zeros((len(p),2));counts=np.zeros(len(p))
for k in range(3):np.add.at(values,f[:,k],uv[:,k]);np.add.at(counts,f[:,k],1)
values/=counts[:,None]
N=1024;depth=np.full((N,N),-np.inf);gn=np.cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]])
for idx in np.where(gn[:,2]>0)[0]:
 xy=uv[idx]*[N-1,-(N-1)]+[0,N-1];z=p[f[idx],2]
 x0,y0=np.maximum(0,np.floor(xy.min(0)).astype(int));x1,y1=np.minimum(N-1,np.ceil(xy.max(0)).astype(int))
 if x1<x0 or y1<y0:continue
 A=np.stack([xy[1]-xy[0],xy[2]-xy[0]],1)
 if abs(np.linalg.det(A))<1e-9:continue
 yy,xx=np.mgrid[y0:y1+1,x0:x1+1];b=np.linalg.solve(A,np.stack([xx-xy[0,0],yy-xy[0,1]],0).reshape(2,-1)).reshape(2,*xx.shape)
 inside=(b.min(0)>=-.02)&(b.sum(0)<=1.02);zz=z[0]+b[0]*(z[1]-z[0])+b[1]*(z[2]-z[0]);q=depth[y0:y1+1,x0:x1+1];q[inside]=np.maximum(q[inside],zz[inside])
ids=np.arange(len(p)).reshape(-1,28)[:,np.arange(2,13)];coord=values[ids];px=np.clip(np.rint(coord[...,0]*(N-1)).astype(int),0,N-1);py=np.clip(np.rint((1-coord[...,1])*(N-1)).astype(int),0,N-1)
visible=p[ids,2]>=depth[py,px]-.025
out=w/'candidates/10/atlas';out.mkdir(parents=True,exist_ok=True)
for name in ['color','emissive']:
 im=np.asarray(Image.open(w/'source/installed/0'/f'{name}.png').convert('RGB'),float);h,ww=im.shape[:2]
 sampled=np.stack([map_coordinates(im[:,:,c],[(1-coord[...,1])*(h-1),coord[...,0]*(ww-1)],order=1,mode='nearest') for c in range(3)],-1)
 for k in range(11):
  valid=np.where(visible[:,k])[0];assert len(valid)>100,(k,len(valid))
  q=np.arange(768);periodic=np.r_[valid-768,valid,valid+768]
  for c in range(3):sampled[:,k,c]=np.interp(q,periodic,np.tile(sampled[valid,k,c],3))
 # j is the horizontal atlas axis; front ribbon cross section runs vertically.
 jj=np.linspace(0,768,1024,endpoint=False);kk=np.linspace(0,10,256)
 y,x=np.meshgrid(kk,jj,indexing='ij')
 data=np.stack([map_coordinates(sampled[:,:,c],[x,y],order=1,mode='grid-wrap') for c in range(3)],-1)
 Image.fromarray(np.clip(np.rint(data),0,255).astype('uint8')).save(out/f'rear_{name}.png')
(out/'atlas.json').write_text(json.dumps({'source_visible_samples':visible.sum(0).tolist(),'hidden_samples_filled':int((~visible).sum()),'method':'Reuse each ribbon cross section of the installed front. Fill front-occluded portions by interpolating nearby visible portions along the same ribbon; no hidden crossing shadow is painted on the exposed back.'},indent=2)+'\n')
print('visible',visible.sum(0),'filled',(~visible).sum())
