import bpy,numpy as np,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
C=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase01/candidate36');d=np.load(C/'source_fields.npz');attrs=json.loads((C/'source_field_attrs.json').read_text())['Chest Upper Lid Rim'];v=d['Chest Upper Lid Rim v'];t=d['Chest Upper Lid Rim t'];tri=v[t];G=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);G/=np.linalg.norm(G,axis=1)[:,None];tree=BVHTree.FromPolygons(v.tolist(),t.tolist(),all_triangles=True);ob=bpy.data.objects['Chest Upper Lid Rim'];rows=[]
for f in ob.data.polygons:
 normal=np.array(f.normal)
 for i in f.vertices:
  p=ob.data.vertices[i].co;hits=tree.find_nearest_range(p,.02)
  eligible=[h for h in hits if G[h[2]]@normal>.8]; closest=min((h[3] for h in eligible),default=100)
  if closest>.0008:rows.append(dict(face=f.index,position=list(p),area=f.area,closest_compatible=closest,near=[dict(distance=h[3],dot=float(G[h[2]]@normal),smooth=attrs[h[2]]['smooth'],source=attrs[h[2]]['source']) for h in hits]))
(C/'lid_unmatched_all.json').write_text(json.dumps(rows,indent=2));print(json.dumps(dict(unmatched=len(rows),minimum_best_dot=min((max((h['dot'] for h in r['near']),default=-1) for r in rows),default=1),maximum_nearest_distance=max((min((h['distance'] for h in r['near']),default=100) for r in rows),default=0),faces=sorted({r['face'] for r in rows})[:30])))
