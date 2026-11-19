"""Retain measured reference crowns while using the coordinated clear pavilion."""
from pathlib import Path
import json,numpy as np
from scipy.spatial import ConvexHull,HalfspaceIntersection
from scipy.optimize import linprog
from PIL import Image,ImageDraw
import forward as f
R=Path(__file__).resolve().parent;raw=np.load(R/'heart_plane_cut_0.65_1.7.npz')
Y,X=np.mgrid[350:835:4,360:850:4];shape=X.shape;x=X.ravel();y=Y.ravel();axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
ray=f.unit(axis[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();studio=f.Studio()
source=Path(f.__file__).read_text();a=source.index('def optical(');b=source.index('\ndef render',a)
code=source[a:b].replace('def optical(hulls,o,d,studio):','def optical(hulls,o,d,studio,thickness):').replace('absorption=np.array([.16,9.,2.8])*.5','absorption=np.array([.16,9.,.65])*max(.5,1/thickness)').replace('*.32','*.434211563');ns=dict(f.__dict__);exec(code,ns);optical=ns['optical'];variants=[];reports=[]
for candidate in ['candidate16','candidate18','candidate20','candidate21']:
 C=R.parent/'ruby_heart'/candidate;D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose'];ps=[]
 for j,p in enumerate(parts):
  upper=ConvexHull(p).equations;upper=upper[upper[:,2]>-1e-6]
  back=ConvexHull(raw[f'{j}_points']).equations;back=back[back[:,2]<-.01].copy();shift=p[48:96,2].mean()+.03;back[:,3]-=back[:,2]*shift
  hs=np.vstack([upper,back]);hs=np.unique(np.round(hs,9),axis=0);A=np.c_[hs[:,:3],np.linalg.norm(hs[:,:3],axis=1)];result=linprog([0,0,0,-1],A_ub=A,b_ub=-hs[:,3],bounds=[(None,None)]*3+[(0,None)],method='highs');assert result.success
  points=HalfspaceIntersection(hs,result.x[:3]).intersections;ps.append(points)
 hulls=[f.planes_of(p) for p in ps];counts=[len(h[0]) for h in hulls];assert max(counts)<=256,counts
 np.savez_compressed(R/f'heart_reference_crown_{candidate}.npz',**{f'{i}_points':p for i,p in enumerate(ps)})
 ids,lin=optical(hulls,eye,ray,studio,np.ptp(ps[0][:,2]));frame=np.full((len(x),3),.03);frame[ids]=np.clip(f.agx(lin),0,1);variants.append((f'Reference front {candidate}, coordinated real pavilion',frame.reshape(*shape,3)));reports.append(dict(crown_source=candidate,planes=counts))
for j in range(2):
 sheet=Image.new('RGB',(1000,535),(12,12,15));draw=ImageDraw.Draw(sheet)
 for i,(title,a) in enumerate(variants[j*2:j*2+2]):
  sheet.paste(Image.fromarray(np.uint8(a*255)).resize((500,500)),(i*500,30));draw.text((i*500+5,8),title,fill='white')
 sheet.save(R/f'heart_reference_crown_pavilion_{j}.png')
(R/'heart_reference_crown_pavilion.json').write_text(json.dumps(dict(status='diagnostic_only_not_native',measured_reference_crown_faces_preserved=True,pavilion_shared_across_entire_ruby=True,no_appearance_map=True,current_reviewed_candidate24_unmodified=True,variants=reports),indent=2));print('Reference crown comparison ready',flush=True)
