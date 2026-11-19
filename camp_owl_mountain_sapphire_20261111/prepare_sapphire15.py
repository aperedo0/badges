"""Shape the broad gold bezel as a real inward rising chamfer, matching the reference."""
from pathlib import Path
import json,shutil,numpy as np,shapely
from shapely.geometry import Polygon
R=Path(__file__).resolve().parent;A=R/'sapphire_teardrop/candidate14';C=A.parent/'candidate15';assert not C.exists();C.mkdir()
for f in ['parts.npz','parts.json','palette_overrides.json','optical_profile.json','cut_design.json']:shutil.copy2(A/f,C/f)
D=dict(np.load(C/'parts.npz'));M=json.loads((C/'parts.json').read_text());p=next(p for p in M['parts'] if p['name']=='solid_gold_teardrop_setting');name=p['name'];nf=p['front'];V=D[name+'_v'];xy,inv=np.unique(V[...,:2].reshape(-1,2),axis=0,return_inverse=True);oldheight=np.zeros(len(xy));np.maximum.at(oldheight,inv,abs(V[...,2].ravel()-.43))
region=shapely.union_all([Polygon(t[:,:2]) for t in V[:nf]]);assert region.geom_type=='Polygon' and len(region.interiors)==1
P=shapely.points(xy);outer=shapely.distance(P,region.exterior);inner=shapely.distance(P,region.interiors[0]);t=outer/np.maximum(outer+inner,1e-10);h=.26+.14*t
# Keep identity transforms, mirrored complete mounting body and closed topology.
z=V[...,2].reshape(-1)-.43;z=(z/oldheight[inv])*h[inv]+.43;D[name+'_v'][...,2]=z.reshape(V.shape[:2]);V=D[name+'_v'][:nf]
points,fi=np.unique(V.reshape(-1,3),axis=0,return_inverse=True);F=fi.reshape(-1,3);face=np.cross(V[:,1]-V[:,0],V[:,2]-V[:,0]);face/=np.linalg.norm(face,axis=1)[:,None];acc=np.zeros_like(points,dtype=np.float64)
for j in range(3):
 a=V[:,(j+1)%3]-V[:,j];b=V[:,(j+2)%3]-V[:,j];a/=np.linalg.norm(a,axis=1)[:,None];b/=np.linalg.norm(b,axis=1)[:,None];angle=np.arccos(np.clip((a*b).sum(1),-1,1));np.add.at(acc,F[:,j],face*angle[:,None])
acc/=np.linalg.norm(acc,axis=1)[:,None];N=D[name+'_n'];N[:nf]=acc[F];N[nf:2*nf]=acc[F][:,::-1]*[1,1,-1]
wall=N[2*nf:];length=np.linalg.norm(wall[...,:2],axis=2);good=length>1e-8;wall[...,:2][good]/=length[good,None];wall[...,2]=0
np.savez_compressed(C/'parts.npz',**D)
(C/'frame_finish.json').write_text(json.dumps(dict(reason='Reference broad gold band is an inward rising bezel chamfer. A parallel flat plate gives one flat reflection; smoothed normals across that plate make a false tube. This version changes actual geometry to a continuous inward rise.',outer_halfheight=.26,inner_halfheight=.40,frame_center_z=.43,gem_unchanged=True,all_uvs_unchanged=True,blender_review_pending=True),indent=2)+'\n')
print('Shaped real gold chamfer. Mesh topology, outline and gem unchanged.')
