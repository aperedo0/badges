import json,numpy as np
from pathlib import Path
P=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase01');C=P/'candidate36'
exec(compile((P/'tools/frame36_geometry.py').read_text(),'helpers36','exec'))
old=np.load(C/'source_fields.npz');known=json.loads((C/'bvh_precision_diagnosis.json').read_text());report={}
for name,row in known.items():
 v=old[name+' v'];t=old[name+' t'];tri=v[t];G=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);G/=np.linalg.norm(G,axis=1)[:,None];f=dict(tri=tri,geom=G,index=index36(tri));hits=near36(f,np.array(row['point']),.0008);assert hits;distance=min(h[3] for h in hits);assert abs(distance-row['brute_force_distance'])<1e-10;report[name]=dict(recovered_distance=distance,old_wrong_bvh_distance=row['bvh_distance'])
tri=np.array([[[0.,0,0],[1.,0,0],[0,1.,0]]]);f=dict(tri=tri,geom=np.array([[0.,0,1.]]),index=index36(tri));assert near36(f,[.2,.2,0],.0008);assert not near36(f,[.2,.2,.001],.0008);assert not near36(f,[.8,.8,0],.0008)
report['negative_controls']=dict(real_normal_displacement_rejected=True,point_outside_triangle_but_inside_bounds_rejected=True);(C/'precision_checker_proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
