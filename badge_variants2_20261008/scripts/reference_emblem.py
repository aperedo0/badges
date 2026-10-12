import json
from pathlib import Path
from pxr import Usd,UsdGeom
import numpy as np
r=Path(__file__).resolve().parents[1];s=Usd.Stage.Open(str(r/'source/silver_base.usdz'))
for prim in s.Traverse():
    if prim.IsA(UsdGeom.Mesh) and 'Emblem' in str(prim.GetPath()):
        m=UsdGeom.Mesh(prim);points=[list(p) for p in m.GetPointsAttr().Get()];indices=m.GetFaceVertexIndicesAttr().Get();counts=m.GetFaceVertexCountsAttr().Get();faces=[];offset=0
        for c in counts:faces.append(list(indices[offset:offset+c]));offset+=c
        n=np.array(m.GetNormalsAttr().Get()).reshape(-1,3,3)
        for i,f in enumerate(faces):
            xyz=np.array(points)[f]
            if np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0])@n[i].mean(0)<0:faces[i]=[f[0],f[2],f[1]]
        (r/'proof/original_silver_emblem.json').write_text(json.dumps({'points':points,'indices':faces,'subsets':{'all':list(range(len(faces)))}}))
