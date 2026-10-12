"""Blender python: export_all.py <usdc> <out.npz> : ALLP = every triangle of every mesh (for the silhouette); plus per textured
material its triangles (P, UV) and the map files it reads, as JSON in 'info'."""
import sys, json, numpy as np
from pxr import Usd, UsdGeom, UsdShade
st = Usd.Stage.Open(sys.argv[1]); ALLP = []; P = []; UV = []; MAT = []; info = {}
def mat_info(mat):
    if mat in info: return info[mat]
    varname, files = None, {}
    for p in Usd.PrimRange(UsdShade.Material.Get(st, mat).GetPrim()):
        if not p.IsA(UsdShade.Shader): continue
        sh = UsdShade.Shader(p); sid = sh.GetIdAttr().Get()
        if sid == 'UsdPrimvarReader_float2': varname = sh.GetInput('varname').Get()
        if sid == 'UsdPreviewSurface':
            for n in ['diffuseColor', 'emissiveColor', 'roughness']:
                i = sh.GetInput(n)
                if i and i.HasConnectedSource():
                    f = UsdShade.Shader(i.GetConnectedSources()[0][0].source.GetPrim()).GetInput('file').Get()
                    if f: files[n] = f.path
    info[mat] = {'varname': varname, 'files': files}; return info[mat]
for prim in st.Traverse():
    if not prim.IsA(UsdGeom.Mesh): continue
    m = UsdGeom.Mesh(prim); pts = np.array(m.GetPointsAttr().Get()); idx = np.array(m.GetFaceVertexIndicesAttr().Get()).reshape(-1, 3)
    ALLP.append(pts[idx])
    names = np.array([''] * len(idx), dtype=object)
    for s in UsdGeom.Subset.GetAllGeomSubsets(m):
        t = UsdShade.MaterialBindingAPI(s.GetPrim()).GetDirectBindingRel().GetTargets()
        names[np.array(s.GetIndicesAttr().Get())] = str(t[0]) if t else ''
    if not UsdGeom.Subset.GetAllGeomSubsets(m):
        t = UsdShade.MaterialBindingAPI(prim).GetDirectBindingRel().GetTargets(); names[:] = str(t[0]) if t else ''
    pv = UsdGeom.PrimvarsAPI(prim)
    for mat in set(names):
        if not mat: continue
        mi = mat_info(mat)
        if not mi['varname'] or not mi['files']: continue
        sel = names == mat; pvv = pv.GetPrimvar(mi['varname']); uv = np.array(pvv.Get()); ind = pvv.GetIndices()
        if ind: uv = uv[np.array(ind)]
        uvt = uv.reshape(-1, 3, 2) if pvv.GetInterpolation() == 'faceVarying' else uv[idx]
        P.append(pts[idx[sel]]); UV.append(uvt[sel]); MAT += [mat.split('/')[-1]] * int(sel.sum())
np.savez(sys.argv[2], ALLP=np.concatenate(ALLP), P=np.concatenate(P), UV=np.concatenate(UV), MAT=np.array(MAT, dtype=str),
         info=json.dumps({k.split('/')[-1]: v for k, v in info.items()}))
print('ok', sum(len(a) for a in ALLP), 'triangles,', len(MAT), 'textured')
