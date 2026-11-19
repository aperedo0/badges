import bpy,numpy as np,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
C=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase01/candidate36');source=np.load(C/'source_fields.npz');attrs=json.loads((C/'source_field_attrs.json').read_text());report={}
for name,key in [('Chest Body Upper Rim','body'),('Chest Upper Lid Rim','lid')]:
 oldv=source[name+' v'];oldt=source[name+' t'];oldtri=oldv[oldt];G=np.cross(oldtri[:,1]-oldtri[:,0],oldtri[:,2]-oldtri[:,0]);G/=np.linalg.norm(G,axis=1)[:,None];tree=BVHTree.FromPolygons(oldv.tolist(),oldt.tolist(),all_triangles=True);new=np.load(C/f'manifold64_{key}.npz');v=new['v'].astype(np.float32).astype(float);t=new['t'];points=np.vstack([v,v[t].mean(1)]);dist=np.array([tree.find_nearest(Vector(p))[3] for p in points]);gn=np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]);gn/=np.linalg.norm(gn,axis=1)[:,None];missing=[]
 for i,face in enumerate(t):
  for vid in face:
   near=tree.find_nearest_range(Vector(v[vid]),.0008)
   if not any(G[h[2]]@gn[i]>(.8 if attrs[name][h[2]]['smooth'] else .9) for h in near):missing.append(dict(face=i,position=v[vid].tolist(),best_dot=max((float(G[h[2]]@gn[i]) for h in near),default=-1)))
 report[name]=dict(maximum_surface_error=float(dist.max()),samples_over_original_gate=int((dist>.0008).sum()),unmapped_old_normals=len(missing),missing=missing);(C/'manifold64_measurement.json').write_text(json.dumps(report,indent=2));print(json.dumps({name:{k:val for k,val in report[name].items() if k!='missing'}}))
print('Read only array measurement. No chest geometry or scene object changed.')
