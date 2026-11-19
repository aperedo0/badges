"""Use fewer real perimeter facets beneath the setting and smooth the actual metal walls."""
from pathlib import Path
import numpy as np,json,shutil
from scipy.spatial import ConvexHull,HalfspaceIntersection
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
R=Path(__file__).resolve().parent;A=R/'sapphire_teardrop/candidate17';C=A.parent/'candidate18';assert not C.exists();C.mkdir()
D=dict(np.load(A/'parts.npz'));M=json.loads((A/'parts.json').read_text());v=D['gem_v'].astype(float);n=D['gem_n'][:,0].astype(float);off=(n*v[:,0]).sum(1);raw=np.unique(np.round(np.c_[n,off],6),axis=0)
# Keep the real measured front and rear crown planes and tables unchanged.
planes=[np.r_[p[:3],-p[3]] for p in raw if abs(p[2])>.001]
pts=np.unique(v.reshape(-1,3),axis=0);ring=Polygon(pts[ConvexHull(pts[:,:2]).vertices,:2]);curve=orient(ring,sign=1).exterior
p=np.array([curve.interpolate(t,normalized=True).coords[0] for t in np.linspace(0,1,24,endpoint=False)])
for a,b in zip(p,np.roll(p,-1,axis=0)):
 q=np.r_[b[1]-a[1],a[0]-b[0]];q/=np.linalg.norm(q);support=np.max(pts[:,:2]@q);planes.append([*q,0,-support])
hs=np.array(planes);inside=np.r_[ring.centroid.coords[0],0.];assert (hs[:,:3]@inside+hs[:,3]<0).all();vertices=HalfspaceIntersection(hs,inside).intersections;h=ConvexHull(vertices);f=h.simplices.copy();V=vertices[f];N=np.cross(V[:,1]-V[:,0],V[:,2]-V[:,0]);flip=(N*h.equations[:,:3]).sum(1)<0;f[flip]=f[flip,::-1];V=vertices[f];N=np.cross(V[:,1]-V[:,0],V[:,2]-V[:,0]);N/=np.linalg.norm(N,axis=1)[:,None]
D['gem_v']=V.astype(np.float32);D['gem_n']=np.repeat(N[:,None],3,axis=1).astype(np.float32);D['gem_uv']=np.zeros((len(V),3,2),np.float32);D['gem_m']=np.zeros(len(V),np.int16)
for part in M['parts']:
 if part['name']=='gem':part.update(triangles=len(V),front=0)
 if part['name']!='solid_gold_teardrop_setting':continue
 name=part['name'];nf=part['front'];wallv=D[name+'_v'][2*nf:];walln=D[name+'_n'][2*nf:];P,inv=np.unique(wallv.reshape(-1,3),axis=0,return_inverse=True);F=inv.reshape(-1,3);fn=np.cross(wallv[:,1]-wallv[:,0],wallv[:,2]-wallv[:,0]);fn/=np.linalg.norm(fn,axis=1)[:,None];acc=np.zeros_like(P,dtype=float)
 for k in range(3):
  a=wallv[:,(k+1)%3]-wallv[:,k];b=wallv[:,(k+2)%3]-wallv[:,k];a/=np.linalg.norm(a,axis=1)[:,None];b/=np.linalg.norm(b,axis=1)[:,None];ang=np.arccos(np.clip((a*b).sum(1),-1,1));np.add.at(acc,F[:,k],fn*ang[:,None])
 acc/=np.linalg.norm(acc,axis=1)[:,None];D[name+'_n'][2*nf:]=acc[F]
np.savez_compressed(C/'parts.npz',**D);(C/'parts.json').write_text(json.dumps(M,indent=1)+'\n')
for file in ['palette_overrides.json','optical_profile.json']:shutil.copy2(A/file,C/file)
(C/'cut_design.json').write_text(json.dumps(dict(change='Measured crown and table planes retained. Twenty four real perimeter facets under the metal setting replace the dense perimeter facets. Metal side walls use angle weighted true geometry normals.',gem_planes=len(hs),gem_triangles=len(V),no_app_changes=True,no_appearance_texture=True,blender_review_pending=True),indent=2)+'\n')
print('Prepared candidate18',len(V),'gem triangles',len(hs),'construction planes')
