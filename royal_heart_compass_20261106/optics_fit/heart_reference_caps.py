"""Add measured light facing upper facets without altering the shared ruby keel."""
from pathlib import Path
import json,numpy as np
from scipy.spatial import ConvexHull,HalfspaceIntersection
from scipy.optimize import linprog
from PIL import Image,ImageDraw
import forward as f
R=Path(__file__).resolve().parent;raw=np.load(R/'heart_plane_cut_0.65_1.7.npz');parts=[raw[f'{i}_points'].astype(float) for i in range(2)];C=R.parent/'ruby_heart/candidate20';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());rings=[D[f'{i}_points'][:48,:2] for i,g in enumerate(G) if g['mat']=='CrestGem_Rose']
Y,X=np.mgrid[350:835:4,360:850:4];shape=X.shape;x=X.ravel();y=Y.ravel();axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
ray=f.unit(axis[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();studio=f.Studio()
source=Path(f.__file__).read_text();a=source.index('def optical(');b=source.index('\ndef render',a)
code=source[a:b].replace('def optical(hulls,o,d,studio):','def optical(hulls,o,d,studio,thickness):').replace('absorption=np.array([.16,9.,2.8])*.5','absorption=np.array([.16,9.,.65])*max(.5,1/thickness)').replace('*.32','*.434211563');ns=dict(f.__dict__);exec(code,ns);optical=ns['optical'];variants=[];reports=[]
for margin in [.015,.07,.15]:
 ps=[];cuts=[]
 for p,ring in zip(parts,rings):
  left=p[:,0].mean()<0;g=np.array([.35,-.35]) if left else np.array([-.122,-.5455]);seam=p[abs(p[:,0])<1e-6];h=max(float(np.max(.03-ring@g))+margin,float(np.max(seam[:,2]-seam[:,:2]@g))+.01)
  hs=np.vstack([ConvexHull(p).equations,[-g[0],-g[1],1.,-h]]);hs=np.unique(np.round(hs,10),axis=0);A=np.c_[hs[:,:3],np.linalg.norm(hs[:,:3],axis=1)];res=linprog([0,0,0,-1],A_ub=A,b_ub=-hs[:,3],bounds=[(None,None)]*3+[(0,None)],method='highs');assert res.success
  points=HalfspaceIntersection(hs,res.x[:3]).intersections;ps.append(points);cuts.append(dict(side='left' if left else 'right',actual_facet_gradient=g.tolist(),offset=h,common_keel_unchanged=True))
 hulls=[f.planes_of(p) for p in ps];counts=[len(h[0]) for h in hulls];assert max(counts)<=256
 np.savez_compressed(R/f'heart_reference_caps_{margin}.npz',**{f'{i}_points':p for i,p in enumerate(ps)})
 ids,lin=optical(hulls,eye,ray,studio,np.ptp(ps[0][:,2]));frame=np.full((len(x),3),.03);frame[ids]=np.clip(f.agx(lin),0,1);variants.append((f'Real upper facet support margin {margin}',frame.reshape(*shape,3)));reports.append(dict(margin=margin,planes=counts,cuts=cuts))
sheet=Image.new('RGB',(1500,535),(12,12,15));draw=ImageDraw.Draw(sheet)
for i,(title,a) in enumerate(variants):
 sheet.paste(Image.fromarray(np.uint8(a*255)).resize((500,500)),(i*500,30));draw.text((i*500+5,8),title,fill='white')
sheet.save(R/'heart_reference_caps.png');(R/'heart_reference_caps.json').write_text(json.dumps(dict(status='diagnostic_only_not_native',actual_facet_planes_only=True,shared_keel_and_original_silhouette_preserved=True,current_native24_unmodified=True,no_appearance_images=True,variants=reports),indent=2));print('Reference upper facet diagnostic ready',flush=True)
