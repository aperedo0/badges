"""Check every physical solid from the inspected Blender checkpoint."""
from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parent;C=R/(R/'candidate.txt').read_text().strip()
D=np.load(C/'blender_geometry.npz');groups=json.loads((C/'groups.json').read_text());reports=[]
solids=[[0,1],[8,9],[10,11]]+[[i] for i in range(len(groups)) if i not in [0,1,8,9,10,11]]
for ids in solids:
 points=[];triangles=[];offset=0
 for i in ids:
  p=D[str(i)+'_points'];t=D[str(i)+'_triangles'];points.append(p);triangles.append(t+offset);offset+=len(p)
 p=np.vstack(points);t=np.vstack(triangles)
 area=np.linalg.norm(np.cross(p[t[:,1]]-p[t[:,0]],p[t[:,2]]-p[t[:,0]]),axis=1)
 assert area.min()>1e-11,groups[ids[0]]['name']
 _,welded=np.unique(np.round(p,6),axis=0,return_inverse=True);q=welded[t]
 edges=np.vstack([q[:,[0,1]],q[:,[1,2]],q[:,[2,0]]]);_,inverse,count=np.unique(np.sort(edges,axis=1),axis=0,return_inverse=True,return_counts=True)
 winding=np.bincount(inverse,weights=np.where(edges[:,0]<edges[:,1],1,-1))
 assert (count==2).all() and (winding==0).all(),groups[ids[0]]['name']
 reports.append(dict(name=groups[ids[0]]['name'],closed=True,consistent_winding=True,no_degenerate_triangles=True))
(C/'closed_solids_validation.json').write_text(json.dumps(reports,indent=2)+'\n')
print('All',len(reports),'physical solids pass.')
