import json,numpy as np
from pathlib import Path
from pxr import Usd,UsdGeom
r=Path(__file__).resolve().parents[1];stage=Usd.Stage.Open(str(r/'work/iron_baked.usdz'));data={}
for prim in stage.Traverse():
 if not prim.IsA(UsdGeom.Mesh):continue
 mesh=UsdGeom.Mesh(prim);pv=UsdGeom.PrimvarsAPI(prim).GetPrimvar('USDZ_UV')
 if not pv:continue
 data[prim.GetParent().GetName()]={'points':np.array(mesh.GetPointsAttr().Get()).tolist(),'indices':np.array(mesh.GetFaceVertexIndicesAttr().Get()).reshape(-1,3).tolist(),'uv':np.array(pv.ComputeFlattened()).reshape(-1,3,2).tolist(),'normals':np.array(mesh.GetNormalsAttr().Get()).reshape(-1,3,3).tolist()}
(r/'work/normal_bake_geometry.json').write_text(json.dumps(data));print('Extracted actual shipped UVs and corner normals for seam-safe normal baking.')
