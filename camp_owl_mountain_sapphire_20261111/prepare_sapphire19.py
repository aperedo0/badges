"""Test a real sloping rear table, retaining the measured front and intrinsic sapphire optics."""
from pathlib import Path
import numpy as np,json,shutil
from scipy.spatial import HalfspaceIntersection,ConvexHull
R=Path(__file__).resolve().parent;A=R/'sapphire_teardrop/candidate18';C=A.parent/'candidate19';assert not C.exists();C.mkdir()
D=dict(np.load(A/'parts.npz'));M=json.loads((A/'parts.json').read_text());V=D['gem_v'].astype(float);N=D['gem_n'][:,0].astype(float);w=(N*V[:,0]).sum(1);raw=np.unique(np.round(np.c_[N,w],6),axis=0);ymin=V[...,1].min();k=.30
# Move only the rear planes farther from the crown toward the top.
# This is real absorption path variation through solid sapphire, not a color ramp.
p=raw.copy();rear=p[:,2]<-.001;p[rear,1]+=p[rear,2]*k;p[rear,3]+=p[rear,2]*k*ymin;hs=np.c_[p[:,:3],-p[:,3]];inside=V.reshape(-1,3).mean(0);inside[2]-=.3;assert (hs[:,:3]@inside+hs[:,3]<0).all();P=HalfspaceIntersection(hs,inside).intersections;h=ConvexHull(P);F=h.simplices.copy();v=P[F];n=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);flip=(n*h.equations[:,:3]).sum(1)<0;F[flip]=F[flip,::-1];v=P[F];n=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
D['gem_v']=v.astype(np.float32);D['gem_n']=np.repeat(n[:,None],3,axis=1).astype(np.float32);D['gem_uv']=np.zeros((len(v),3,2),np.float32);D['gem_m']=np.zeros(len(v),np.int16)
shift=-(P[:,2].min()+P[:,2].max())/2
for part in M['parts']:
 D[part['name']+'_v'][...,2]+=shift
 if part['name']=='gem':part.update(triangles=len(v),front=0,asymmetric_rear_cut=True)
np.savez_compressed(C/'parts.npz',**D);(C/'parts.json').write_text(json.dumps(M,indent=1)+'\n')
for f in ['palette_overrides.json','optical_profile.json']:shutil.copy2(A/f,C/f)
(C/'cut_design.json').write_text(json.dumps(dict(change='Rear sapphire planes slope toward a deeper top, giving real variation in optical path lengths across the broad front table. Measured front planes and XY outline retained.',rear_shear=k,centering_shift=shift,depth=float(np.ptp(P[:,2])),no_reference_appearance_texture=True,no_app_changes=True,blender_review_pending=True),indent=2)+'\n');print('Prepared rear cut19',len(v),'triangles, center shift',shift)
