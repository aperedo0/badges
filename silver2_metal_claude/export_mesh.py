"""Blender python: export_mesh.py <usdc> <out.npz> : every triangle's points, uvs, mesh name and material name."""
import sys, numpy as np
from pxr import Usd, UsdGeom, UsdShade
st = Usd.Stage.Open(sys.argv[1]); P, UV, MAT, MESH = [], [], [], []
for prim in st.Traverse():
    if not prim.IsA(UsdGeom.Mesh): continue
    m = UsdGeom.Mesh(prim); pts = np.array(m.GetPointsAttr().Get()); idx = np.array(m.GetFaceVertexIndicesAttr().Get()).reshape(-1, 3)
    uv = np.array(UsdGeom.PrimvarsAPI(prim).GetPrimvar('USDZ_UV').Get()).reshape(-1, 3, 2)
    mat = np.array([''] * len(idx), dtype=object)
    for s in UsdGeom.Subset.GetAllGeomSubsets(m):
        t = UsdShade.MaterialBindingAPI(s.GetPrim()).GetDirectBindingRel().GetTargets()
        mat[np.array(s.GetIndicesAttr().Get())] = t[0].name if t else ''
    P.append(pts[idx]); UV.append(uv); MAT += list(mat); MESH += [prim.GetName()] * len(idx)
np.savez(sys.argv[2], P=np.concatenate(P), UV=np.concatenate(UV), MAT=np.array(MAT, dtype=str), MESH=np.array(MESH, dtype=str))
print('triangles', len(MAT))
