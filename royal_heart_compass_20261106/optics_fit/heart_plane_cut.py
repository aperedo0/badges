"""Construct one coordinated crown and pavilion from actual cutting planes."""
from pathlib import Path
import json,numpy as np
from scipy.spatial import ConvexHull,HalfspaceIntersection
from scipy.optimize import linprog
from PIL import Image,ImageDraw
import forward as f
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate20';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose'];whole=np.vstack([p[:48,:2] for p in parts]);center=np.array([0.,.30]);peak=np.array([0.,.99]);front=.03;rear=-.03
Y,X=np.mgrid[350:835:4,360:850:4];shape=X.shape;x=X.ravel();y=Y.ravel();axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
ray=f.unit(axis[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();studio=f.Studio()
source=Path(f.__file__).read_text();a=source.index('def optical(');b=source.index('\ndef render',a)
code=source[a:b].replace('def optical(hulls,o,d,studio):','def optical(hulls,o,d,studio,thickness):').replace('absorption=np.array([.16,9.,2.8])*.5','absorption=np.array([.16,9.,2.8])/thickness').replace('*.32','*.434211563');ns=dict(f.__dict__);exec(code,ns);optical=ns['optical']
variants=[];reports=[]
for slope in [.45,.65]:
 for depth in [1.2,1.7,2.2]:
  shared=[]
  for angle in np.arange(16)*np.pi/8:
   u=np.array([np.cos(angle),np.sin(angle)]);h=float(np.max(whole@u));shared.append([slope*u[0],slope*u[1],1.,-(front+slope*h)])
   p_slope=depth/(h-u@center);shared.append([p_slope*u[0],p_slope*u[1],-1.,rear-depth-p_slope*(u@center)])
  for angle in np.arange(8)*np.pi/4+np.pi/8:
   u=np.array([np.cos(angle),np.sin(angle)])*.22;shared.append([u[0],u[1],1.,-(.85+u@peak)])
  ps=[]
  for old in parts:
   xy=ConvexHull(old[:48,:2]).equations;hs=np.vstack([np.c_[xy[:,:2],np.zeros(len(xy)),xy[:,2]],shared]);A=np.c_[hs[:,:3],np.linalg.norm(hs[:,:3],axis=1)];res=linprog([0,0,0,-1],A_ub=A,b_ub=-hs[:,3],bounds=[(None,None)]*3+[(0,None)],method='highs');assert res.success and res.x[3]>.01
   p=HalfspaceIntersection(hs,res.x[:3]).intersections;ps.append(p)
  hulls=[f.planes_of(p) for p in ps];counts=[len(h[0]) for h in hulls];assert max(counts)<=256
  np.savez_compressed(R/f'heart_plane_cut_{slope}_{depth}.npz',**{f'{i}_points':p for i,p in enumerate(ps)})
  ids,lin=optical(hulls,eye,ray,studio,np.ptp(ps[0][:,2]));frame=np.full((len(x),3),.03);frame[ids]=np.clip(f.agx(lin),0,1)
  variants.append((f'Coordinated planes, crown slope {slope}, pavilion {depth}',frame.reshape(*shape,3)));reports.append(dict(crown_slope=slope,pavilion_depth=depth,planes=counts))
for j in range(3):
 sheet=Image.new('RGB',(1000,535),(12,12,15));draw=ImageDraw.Draw(sheet)
 for i,(title,a) in enumerate(variants[j*2:j*2+2]):
  sheet.paste(Image.fromarray(np.uint8(a*255)).resize((500,500)),(i*500,30));draw.text((i*500+5,8),title,fill='white')
 sheet.save(R/f'heart_plane_cut_{j}.png')
(R/'heart_plane_cut.json').write_text(json.dumps(dict(status='diagnostic_only_not_native',one_shared_crown_and_pavilion_plane_field=True,exact_original_front_silhouette=True,no_appearance_maps=True,original_clear_optical_shader=True,variants=reports),indent=2));print('Coordinated plane cut ready',flush=True)
