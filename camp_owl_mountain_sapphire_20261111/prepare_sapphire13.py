"""Use a true pavilion behind the measured front cut so it returns light rather than acting as parallel windows."""
from pathlib import Path
import numpy as np,json,shutil
from scipy.spatial import ConvexHull,HalfspaceIntersection
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
R=Path(__file__).resolve().parent;A=R/'sapphire_teardrop/candidate12';C=A.parent/'candidate13';assert not C.exists();C.mkdir()
D=dict(np.load(A/'parts.npz'));M=json.loads((A/'parts.json').read_text());V=np.unique(D['gem_v'].reshape(-1,3),axis=0);hxy=ConvexHull(V[:,:2]);ring=V[hxy.vertices,:2];ring=np.asarray(orient(Polygon(ring),sign=1).exterior.coords)[:-1];table=V[np.isclose(V[:,2],.64),:2];table=table[ConvexHull(table).vertices];table=np.asarray(orient(Polygon(table),sign=1).exterior.coords)[:-1];apex=np.array(Polygon(table).centroid.coords[0]);planes=[]
for p,q in zip(ring,np.roll(ring,-1,axis=0)):
 n=np.array([q[1]-p[1],p[0]-q[0]]);n/=np.linalg.norm(n);planes.append([*n,0,-float(n@p)])
for p,q in zip(table,np.roll(table,-1,axis=0)):
 n=np.array([q[1]-p[1],p[0]-q[0]]);n/=np.linalg.norm(n);edge=float(n@p);support=float(np.max(ring@n));slope=(support-edge)/(.64-.16);planes.append([*n,slope,-(support+slope*.16)])
 # All pavilion planes meet at the actual rear point, not another broad parallel table.
 rear_slope=(support-float(n@apex))/(1.5-.16);planes.append([*n,-rear_slope,-(support+rear_slope*.16)])
planes.append([0,0,1,-.64]);hs=np.array(planes);inside=np.r_[Polygon(table).centroid.coords[0],0.];assert (hs[:,:3]@inside+hs[:,3]<0).all();points=HalfspaceIntersection(hs,inside).intersections;h=ConvexHull(points);f=h.simplices.copy();v=points[f];n=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);bad=(n*h.equations[:,:3]).sum(1)<0;f[bad]=f[bad,::-1];v=points[f];n=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
D['gem_v']=v.astype(np.float32);D['gem_n']=np.repeat(n[:,None],3,axis=1).astype(np.float32);D['gem_uv']=np.zeros((len(v),3,2),np.float32);D['gem_m']=np.zeros(len(v),np.int16)
shift=.43
for p in M['parts']:
 D[p['name']+'_v'][...,2]+=shift
 if p['name']=='gem':p.update(triangles=len(v),front=0,physical_pavilion=True)
np.savez_compressed(C/'parts.npz',**D);(C/'parts.json').write_text(json.dumps(M,indent=1)+'\n');shutil.copy2(A/'palette_overrides.json',C/'palette_overrides.json');shutil.copy2(A/'optical_profile.json',C/'optical_profile.json')
(C/'cut_design.json').write_text(json.dumps(dict(source='candidate12 open physical setting',front='Same measured six broad crown planes and six sided table',back='Six pavilion planes meeting at one real point',reason='Parallel front and rear tables transmit the dark environment instead of returning light through the crown. Pavilion angles now redirect rays.',apex_before_centering=[*apex,-1.5],whole_model_centering_z=shift,gem_geometry_real_closed_convex=True,no_appearance_texture=True,blender_and_native_review_pending=True),indent=2)+'\n')
print('Prepared true pavilion,',len(v),'gem triangles. Model centered Z',-1.5+shift,.64+shift)
