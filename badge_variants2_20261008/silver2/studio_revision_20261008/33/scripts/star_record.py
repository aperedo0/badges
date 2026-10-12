from pathlib import Path
import json,numpy as np
from geometry import silver_geometry,MESH_IDS
r=Path(__file__).resolve().parents[1];b=r/'silver2';meshes,meta=silver_geometry(json.loads((b/'settings.json').read_text()));allpoints=np.concatenate([m.points for m in meshes.values()]);lo=allpoints.min(0);hi=allpoints.max(0);xy=min(6.03/(hi[0]-lo[0]),5.3/(hi[1]-lo[1]));sc=np.array([xy,xy,.65/(hi[2]-lo[2])]);offset=np.array([-(hi[0]+lo[0])/2,-lo[1],-(hi[2]+lo[2])/2]);m=meshes[MESH_IDS[3]];points=((np.array(m.points)+offset)*sc+[0,-2.455,0]).astype(np.float32).tolist();(b/'reports/Star_geometry.json').write_text(json.dumps({'points':points,'indices':m.faces,'regions':m.regions,'subsets':{'front':[i for i,t in enumerate(m.regions) if t.startswith('star plane')]}}))
