from pathlib import Path
import sys
import json,numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,distance_transform_edt
ROOT=Path(__file__).resolve().parents[1];w=Path(json.loads((ROOT/'manifest.json').read_text())['diamond']['work']);number=sys.argv[1] if len(sys.argv)>1 else '02';out=w/'candidates'/number
d=np.load(out/'optical_geometry.npz');p=d['source_points'];f=d['source_faces'];uv=d['source_uv'];newp=d['points'];newf=d['faces'];newuv=np.load(out/'new_uv.npz')['uv'];S=1024
lo=p[f].reshape(-1,3).min(0);hi=p[f].reshape(-1,3).max(0)
def decode(a):return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
def encode(a):return np.uint8(np.clip(np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055),0,1)*255+.5)
def sample(im,x,y):return np.stack([map_coordinates(im[...,c],[y,x],order=1,mode='nearest') for c in range(3)],-1)
def tri_raster(q):
 low=np.maximum(np.floor(q.min(0)).astype(int),0);high=np.minimum(np.ceil(q.max(0)).astype(int),S-1)
 x,y=np.meshgrid(np.arange(low[0],high[0]+1),np.arange(low[1],high[1]+1));A=np.stack([q[1]-q[0],q[2]-q[0]],1)
 if abs(np.linalg.det(A))<1e-10:return None
 b=np.linalg.solve(A,np.stack([x.ravel()-q[0,0],y.ravel()-q[0,1]]));weights=np.c_[1-b.sum(0),b.T];good=weights.min(1)>=-1e-5
 return x.ravel()[good],y.ravel()[good],weights[good]
def field_xy(world):return np.stack([(world[:,0]-lo[0])/(hi[0]-lo[0])*(S-1),(hi[1]-world[:,1])/(hi[1]-lo[1])*(S-1)],-1)
for name in ['color.png','emissive.png']:
 source=decode(np.array(Image.open(next((w/'source/installed').rglob(name))).convert('RGB'),float)/255)
 field=np.zeros((S,S,3));z=np.full((S,S),-1e9)
 for tri,tex in zip(f,uv):
  world=p[tri];q=field_xy(world);r=tri_raster(q)
  if r is None:continue
  x,y,b=r;zz=b@world[:,2];visible=zz>z[y,x];x,y,b,zz=x[visible],y[visible],b[visible],zz[visible]
  texel=b@tex;field[y,x]=sample(source,texel[:,0]*S-.5,(1-texel[:,1])*S-.5);z[y,x]=zz
 cover=z>-1e8;_,(ey,ex)=distance_transform_edt(~cover,return_indices=True);field=field[ey,ex]
 if int(number)>=3:
  Image.fromarray(encode(field)).save(next((out/'usd').rglob(name)),optimize=True)
  continue
 result=np.zeros((S,S,3));filled=np.zeros((S,S),bool)
 for tri,tex in zip(newf,newuv):
  q=np.stack([tex[:,0]*S-.5,(1-tex[:,1])*S-.5],-1);x,y,b=tri_raster(q)
  xy=field_xy(b@newp[tri]);result[y,x]=sample(field,xy[:,0],xy[:,1]);filled[y,x]=True
 _,(ey,ex)=distance_transform_edt(~filled,return_indices=True);result=result[ey,ex]
 Image.fromarray(encode(result)).save(next((out/'usd').rglob(name)),optimize=True)
(out/'optics.json').write_text(json.dumps({'method':'Rasterize installed optical maps into one continuous shared XY chart over the entire closed gem; shared vertices share exact UVs, eliminating atlas tile fringing.' if int(number)>=3 else 'Rasterize installed optical maps into a continuous front XY field, then reproject into individual atlas regions for every real facet.','source':'Installed blue crystal color and emissive maps.','texture_size':S,'facets':len(newf)},indent=2)+'\n')
print('Generated continuous crystal optical fields for',len(newf),'facets.')
