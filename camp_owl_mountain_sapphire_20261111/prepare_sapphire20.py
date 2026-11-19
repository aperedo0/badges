"""Isolate the nested reflection cause with a physically closed flat backed sapphire cut."""
from pathlib import Path
import numpy as np,json,shutil
from scipy.spatial import HalfspaceIntersection,ConvexHull
R=Path(__file__).resolve().parent;A=R/'sapphire_teardrop/candidate18';C=A.parent/'candidate20';assert not C.exists();C.mkdir();D=dict(np.load(A/'parts.npz'));M=json.loads((A/'parts.json').read_text());v=D['gem_v'].astype(float);n=D['gem_n'][:,0].astype(float);w=(n*v[:,0]).sum(1);p=np.unique(np.round(np.c_[n,w],6),axis=0);hs=np.c_[p[p[:,2]>=-.001,:3],-p[p[:,2]>=-.001,3]];hs=np.r_[hs,[[0,0,-1,-.15]]];inside=np.r_[v.reshape(-1,3).mean(0)[:2],0.];assert (hs[:,:3]@inside+hs[:,3]<0).all();P=HalfspaceIntersection(hs,inside).intersections;h=ConvexHull(P);F=h.simplices.copy();V=P[F];N=np.cross(V[:,1]-V[:,0],V[:,2]-V[:,0]);bad=(N*h.equations[:,:3]).sum(1)<0;F[bad]=F[bad,::-1];V=P[F];N=np.cross(V[:,1]-V[:,0],V[:,2]-V[:,0]);N/=np.linalg.norm(N,axis=1)[:,None];D['gem_v']=V.astype(np.float32);D['gem_n']=np.repeat(N[:,None],3,axis=1).astype(np.float32);D['gem_uv']=np.zeros((len(V),3,2),np.float32);D['gem_m']=np.zeros(len(V),np.int16)
for part in M['parts']:
 if part['name']=='gem':part.update(front=0,triangles=len(V),flat_backed_physical_cut=True)
allv=np.concatenate([D[p['name']+'_v'].reshape(-1,3) for p in M['parts']]);shift=-(allv[:,2].min()+allv[:,2].max())/2
for part in M['parts']:D[part['name']+'_v'][...,2]+=shift
np.savez_compressed(C/'parts.npz',**D);(C/'parts.json').write_text(json.dumps(M,indent=1)+'\n')
for file in ['palette_overrides.json','optical_profile.json']:shutil.copy2(A/file,C/file)
(C/'cut_design.json').write_text(json.dumps(dict(change='Physical flat backed cut isolates reflections of the second crown through the front. Front crown planes and XY silhouette unchanged.',closed_convex=True,no_app_changes=True,no_appearance_texture=True,centering_shift=float(shift),back_review_pending=True),indent=2)+'\n');print('Prepared flat backed test20',len(V),'gem triangles',len(hs),'planes')
