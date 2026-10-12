"""Blender python: export_tris.py <usdc> <out.npz> : every triangle's points, uv (from each material's own UV reader), material, and that material's texture files."""
import sys, numpy as np, json
from pxr import Usd, UsdGeom, UsdShade
st = Usd.Stage.Open(sys.argv[1]); P, UV, MAT = [], [], []; info = {}
def mat_info(mat):
    if mat in info: return info[mat]
    varname, files = None, {}
    m = UsdShade.Material.Get(st, mat)
    for p in Usd.PrimRange(m.GetPrim()):
        if not p.IsA(UsdShade.Shader): continue
        sh = UsdShade.Shader(p); sid = sh.GetIdAttr().Get()
        if sid == 'UsdPrimvarReader_float2':
            varname = sh.GetInput('varname').Get()
        if sid == 'UsdPreviewSurface':
            for n in ['diffuseColor', 'emissiveColor', 'roughness', 'metallic']:
                i = sh.GetInput(n)
                if i and i.HasConnectedSource():
                    src = i.GetConnectedSources()[0][0].source
                    f = UsdShade.Shader(src.GetPrim()).GetInput('file').Get()
                    files[n] = f.path if f else None
    info[mat] = {'varname': varname, 'files': files}
    return info[mat]
for prim in st.Traverse():
    if not prim.IsA(UsdGeom.Mesh): continue
    m = UsdGeom.Mesh(prim); pts = np.array(m.GetPointsAttr().Get()); cnt = np.array(m.GetFaceVertexCountsAttr().Get())
    if (cnt != 3).any(): print('non triangle faces in', prim.GetPath()); continue
    idx = np.array(m.GetFaceVertexIndicesAttr().Get()).reshape(-1, 3)
    names = np.array([''] * len(idx), dtype=object)
    for s in UsdGeom.Subset.GetAllGeomSubsets(m):
        t = UsdShade.MaterialBindingAPI(s.GetPrim()).GetDirectBindingRel().GetTargets()
        names[np.array(s.GetIndicesAttr().Get())] = str(t[0]) if t else ''
    if not UsdGeom.Subset.GetAllGeomSubsets(m):
        t = UsdShade.MaterialBindingAPI(prim).GetDirectBindingRel().GetTargets(); names[:] = str(t[0]) if t else ''
    pv = UsdGeom.PrimvarsAPI(prim)
    for mat in set(names):
        if not mat: continue
        mi = mat_info(mat); sel = names == mat
        if not mi['varname']: continue
        pvv = pv.GetPrimvar(mi['varname']); uv = np.array(pvv.Get()); interp = pvv.GetInterpolation()
        ind = pvv.GetIndices()
        if ind: uv = uv[np.array(ind)]
        if interp == 'faceVarying': uvt = uv.reshape(-1, 3, 2)
        else: uvt = uv[idx]
        P.append(pts[idx[sel]]); UV.append(uvt[sel]); MAT += [mat.split('/')[-1]] * int(sel.sum())
np.savez(sys.argv[2], P=np.concatenate(P), UV=np.concatenate(UV), MAT=np.array(MAT, dtype=str))
print(json.dumps({k.split('/')[-1]: v for k, v in info.items()}))
