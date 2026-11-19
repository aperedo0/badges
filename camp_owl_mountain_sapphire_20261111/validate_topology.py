"""Check closed topology and real triangle areas in the actual exported USDZ."""
from pathlib import Path
import json,sys,numpy as np
from pxr import Usd,UsdGeom
R=Path(__file__).resolve().parent;C=R/sys.argv[1]/sys.argv[2];stage=Usd.Stage.Open(str(C/'model.usdz'));rows=[]
for p in stage.Traverse():
 if not p.IsA(UsdGeom.Mesh):continue
 m=UsdGeom.Mesh(p);v=np.asarray(m.GetPointsAttr().Get(),dtype=float);f=np.asarray(m.GetFaceVertexIndicesAttr().Get()).reshape(-1,3);t=v[f];cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);e=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);_,counts=np.unique(e,axis=0,return_counts=True);rows.append(dict(mesh=str(p.GetPath()),triangles=len(f),nonmanifold_edges=int(np.count_nonzero(counts!=2)),zero_area_faces=int(np.count_nonzero(np.sum(cross*cross,axis=1)==0)),volume=float(np.sum(t[:,0]*np.cross(t[:,1],t[:,2]))/6)))
fail=[p for p in rows if p['nonmanifold_edges'] or p['zero_area_faces'] or p['volume']<=0];report=dict(actual_usdz=True,passed=not fail,meshes=len(rows),failures=fail);(C/'topology_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert not fail
