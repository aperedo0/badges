"""Open the physical setting beneath the gem; retain the actual convex gemstone."""
from pathlib import Path
import json,numpy as np,shutil,shapely
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
R=Path(__file__).resolve().parent;A=R/'sapphire_teardrop/candidate11';C=A.parent/'candidate12';assert not C.exists();C.mkdir()
D=dict(np.load(A/'parts.npz'));M=json.loads((A/'parts.json').read_text());U=M['units'];S=U['S'];name='recessed_blue_gem_seat';old=np.unique(D[name+'_v'].reshape(-1,3),axis=0);outer=Polygon(old[ConvexHull(old[:,:2]).vertices,:2]);gem=np.unique(D['gem_v'].reshape(-1,3),axis=0);inner=Polygon(gem[ConvexHull(gem[:,:2]).vertices,:2]).buffer(.008,quad_segs=2);region=orient(outer.difference(inner),sign=1);assert region.geom_type=='Polygon' and len(region.interiors)==1
tri=shapely.constrained_delaunay_triangles(region);xy=np.array([np.asarray(t.exterior.coords)[:3] for t in tri.geoms]);V=np.concatenate([xy,np.full((*xy.shape[:2],1),.105)],2);bad=np.cross(V[:,1]-V[:,0],V[:,2]-V[:,0])[:,2]<0;V[bad]=V[bad][:,::-1];N=np.broadcast_to([0,0,1.],V.shape).copy();back=(V*[1,1,-1])[:,::-1];Bn=(N*[1,1,-1])[:,::-1];walls=[];wn=[]
for ring in [region.exterior,*region.interiors]:
 a=np.asarray(ring.coords)
 for p,q in zip(a[:-1],a[1:]):
  A0=np.r_[p,.105];A1=np.r_[q,.105];B0=np.r_[p,-.105];B1=np.r_[q,-.105];out=np.r_[q[1]-p[1],p[0]-q[0],0];out/=np.linalg.norm(out)
  walls.extend([[A0,B0,A1],[A1,B0,B1]]);wn.extend([[out,out,out],[out,out,out]])
allv=np.concatenate([V,back,np.array(walls)]).astype(np.float32);alln=np.concatenate([N,Bn,np.array(wn)]).astype(np.float32);D[name+'_v']=allv;D[name+'_n']=alln
px=allv[...,0]/S+U['axis'];py=U['top']+(2.995-allv[...,1])/S;D[name+'_uv']=np.stack([px/U['width_px'],1-py/U['height_px']],-1).astype(np.float32);D[name+'_m']=np.r_[np.zeros(2*len(V),np.int16),np.ones(len(walls),np.int16)]
for p in M['parts']:
 if p['name']==name:p.update(triangles=len(allv),front=len(V))
 # Restore actual bevel shape normals on the gold, instead of a shallow fixed blend.
 if p['name']=='solid_gold_teardrop_setting':
  n=p['name'];nf=p['front'];v=D[n+'_v'][:nf];pts,inv=np.unique(v.reshape(-1,3),axis=0,return_inverse=True);F=inv.reshape(-1,3);face=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);face/=np.linalg.norm(face,axis=1)[:,None];accum=np.zeros_like(pts,dtype=np.float64)
  for j in range(3):
   a=v[:,(j+1)%3]-v[:,j];b=v[:,(j+2)%3]-v[:,j];a/=np.linalg.norm(a,axis=1)[:,None];b/=np.linalg.norm(b,axis=1)[:,None];ang=np.arccos(np.clip((a*b).sum(1),-1,1));np.add.at(accum,F[:,j],face*ang[:,None])
  accum/=np.linalg.norm(accum,axis=1)[:,None];D[n+'_n'][:nf]=accum[F];D[n+'_n'][nf:2*nf]=accum[F][:,::-1]*[1,1,-1]
np.savez_compressed(C/'parts.npz',**D);(C/'parts.json').write_text(json.dumps(M,indent=1)+'\n')
over=json.loads((A/'palette_overrides.json').read_text());over['Gold']=dict(albedo=[.83,.43,.045],metallic=1,roughness=.26);(C/'palette_overrides.json').write_text(json.dumps(over,indent=2)+'\n')
for f in ['cut_design.json','optical_profile.json']:shutil.copy2(A/f,C/f)
(C/'setting_fix.json').write_text(json.dumps(dict(change='Full opaque plate passing through gem replaced with a closed annular support outside the actual gemstone outline. Physical internal light path is clear.',gem_geometry_normals_and_uvs_unchanged=True,frame_geometry_unchanged=True,frame_normals='Angle weighted actual geometric bevel normals',runtime_unchanged=True,blender_review_pending=True),indent=2)+'\n')
print('Open gem support created. Gem itself unchanged. Complete',sum(p['triangles'] for p in M['parts']),'triangles')
