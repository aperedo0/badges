import bpy,numpy as np,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
C=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase01/candidate36');old=np.load(C/'source_fields.npz');report={}
for name,key in [('Chest Body Upper Rim','body'),('Chest Upper Lid Rim','lid')]:
 v=old[name+' v'];t=old[name+' t'];tri=v[t];tree=BVHTree.FromPolygons(v.tolist(),t.tolist(),all_triangles=True);d=np.load(C/f'manifold64_{key}.npz');nv=d['v'].astype(np.float32).astype(float);nt=d['t'];pts=np.vstack([nv,nv[nt].mean(1)]);dist=np.array([tree.find_nearest(Vector(p))[3] for p in pts]);p=pts[dist.argmax()];a=tri[:,0];b=tri[:,1];c=tri[:,2];n=np.cross(b-a,c-a);nn=np.einsum('ij,ij->i',n,n);q=p-n*(np.einsum('ij,ij->i',p-a,n)/nn)[:,None];inside=np.ones(len(tri),dtype=bool)
 for A,B in ((a,b),(b,c),(c,a)):inside &= np.einsum('ij,ij->i',np.cross(B-A,q-A),n)>=-1e-24
 distances=np.full(len(tri),np.inf);distances[inside]=np.linalg.norm(q[inside]-p,axis=1)
 for A,B in ((a,b),(b,c),(c,a)):
  e=B-A;u=np.clip(np.einsum('ij,ij->i',p-A,e)/np.einsum('ij,ij->i',e,e),0,1);near=A+e*u[:,None];distances=np.minimum(distances,np.linalg.norm(near-p,axis=1))
 k=int(distances.argmin());report[name]=dict(point=p.tolist(),bvh_distance=float(dist.max()),brute_force_distance=float(distances[k]),old_triangle=k,old_vertices=tri[k].tolist(),bvh_old_triangle=int(tree.find_nearest(Vector(p))[2]));print(json.dumps({name:report[name]}))
(C/'bvh_precision_diagnosis.json').write_text(json.dumps(report,indent=2))
