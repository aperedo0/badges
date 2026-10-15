"""uvdump.py <in.usdz> <out.npz> : per triangle world points (P), UVs (UV, for the texture-reading primvar), material path (MAT),
mesh name (MESH), face index. Handles GeomSubset material bindings. Also ALLP for still_cut alpha."""
import sys, numpy as np
from pxr import Usd, UsdGeom, UsdShade
st = Usd.Stage.Open(sys.argv[1]); P=[]; UV=[]; MAT=[]; MESH=[]; FI=[]
for prim in st.Traverse():
    if not prim.IsA(UsdGeom.Mesh): continue
    m = UsdGeom.Mesh(prim); pts = np.array(m.GetPointsAttr().Get(), float)
    xf = np.array(UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(Usd.TimeCode.Default()), float)
    pts = (np.c_[pts, np.ones(len(pts))] @ xf)[:, :3]
    counts = np.array(m.GetFaceVertexCountsAttr().Get()); idx = np.array(m.GetFaceVertexIndicesAttr().Get())
    base = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0]
    fmat = [str(base.GetPath()) if base else ''] * len(counts)
    for sub in UsdGeom.Subset.GetAllGeomSubsets(m):
        mt = UsdShade.MaterialBindingAPI(sub.GetPrim()).ComputeBoundMaterial()[0]
        if mt:
            for f in sub.GetIndicesAttr().Get(): fmat[f] = str(mt.GetPath())
    pvs = UsdGeom.PrimvarsAPI(prim); uvpv = [p for p in pvs.GetPrimvars() if p.GetTypeName().role == 'TextureCoordinate' or p.GetTypeName() == 'texCoord2f[]' or p.GetTypeName() == 'float2[]']
    uvpv = [p for p in uvpv if p.GetName() != 'primvars:displayColor']
    uv = None
    if uvpv:
        pv = uvpv[0]; vals = np.array(pv.Get(), float); interp = pv.GetInterpolation(); ind = pv.GetIndices()
        if ind and len(ind): vals = vals[np.array(ind)]
    o = 0
    for fi, c in enumerate(counts):
        f = idx[o:o + c]
        for k in range(1, c - 1):
            tri = [0, k, k + 1]; P.append(pts[f[tri]]); MAT.append(fmat[fi]); MESH.append(prim.GetName()); FI.append(fi)
            if uvpv:
                if interp == 'faceVarying': UV.append(vals[o + np.array(tri)])
                elif interp == 'vertex': UV.append(vals[f[tri]])
                else: UV.append(np.zeros((3, 2)))
            else: UV.append(np.zeros((3, 2)))
        o += c
    print(prim.GetName(), len(counts), 'faces', 'uv', uvpv[0].GetName() if uvpv else None, uvpv[0].GetInterpolation() if uvpv else '', sorted(set(fmat)))
P = np.array(P); np.savez_compressed(sys.argv[2], P=P, ALLP=P, UV=np.array(UV), MAT=np.array(MAT), MESH=np.array(MESH), FI=np.array(FI))
print(len(P), 'triangles')
