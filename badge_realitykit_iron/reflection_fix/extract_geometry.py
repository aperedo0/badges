"""Run with Blender's Python (has pxr). Writes, for every textured casing material, its triangles' model-space
positions and UVs plus the texture files it reads (by PreviewSurface input), to geometry.npz + materials.json."""
import json, sys
import numpy as np
from pxr import Usd, UsdGeom, UsdShade
src, out = sys.argv[1], sys.argv[2]
stage = Usd.Stage.Open(src)
tex_by_mat = {}
for prim in stage.Traverse():
    if prim.IsA(UsdShade.Material):
        files = {}
        for shader_prim in Usd.PrimRange(prim):
            sh = UsdShade.Shader(shader_prim)
            if not sh or sh.GetIdAttr().Get() != 'UsdPreviewSurface':
                continue
            for name in ('diffuseColor', 'roughness', 'normal', 'metallic'):
                inp = sh.GetInput(name)
                if not inp or not inp.HasConnectedSource():
                    continue
                for s in inp.GetConnectedSources()[0]:
                    tex = UsdShade.Shader(s.source.GetPrim())
                    f = tex.GetInput('file')
                    if f and f.Get():
                        files[name] = f.Get().path
        tex_by_mat[str(prim.GetPath())] = files
result = {}
arrays = {}
for prim in stage.Traverse():
    if not prim.IsA(UsdGeom.Mesh):
        continue
    mesh = UsdGeom.Mesh(prim)
    pts = np.array(mesh.GetPointsAttr().Get(), dtype=np.float64)
    counts = np.array(mesh.GetFaceVertexCountsAttr().Get())
    idx = np.array(mesh.GetFaceVertexIndicesAttr().Get())
    pv = UsdGeom.PrimvarsAPI(prim)
    # the textures read the primvar named by their UsdPrimvarReader (here USDZ_UV); the mesh also carries
    # Machining_UV for the brushed direction, which must NOT be used for texture lookups
    st = pv.GetPrimvar('USDZ_UV') if pv.HasPrimvar('USDZ_UV') else None
    if st is None:
        continue
    uv = np.array(st.ComputeFlattened(), dtype=np.float64)   # flattened to the primvar's interpolation
    interp = st.GetInterpolation()
    assert (counts == 3).all(), 'expected triangles'
    tri = idx.reshape(-1, 3)
    if interp == 'faceVarying':
        uvt = uv.reshape(-1, 3, 2)
    else:
        uvt = uv[tri]
    pos = pts[tri]
    subsets = UsdGeom.Subset.GetAllGeomSubsets(mesh)
    for sub in subsets:
        mat, _ = UsdShade.MaterialBindingAPI(sub.GetPrim()).ComputeBoundMaterial()
        if not mat:
            continue
        mpath = str(mat.GetPath())
        files = tex_by_mat.get(mpath, {})
        if not files:
            continue
        faces = np.array(sub.GetIndicesAttr().Get())
        key = f"{prim.GetName()}|{mat.GetPrim().GetName()}"
        arrays[key + '|pos'] = pos[faces]
        arrays[key + '|uv'] = uvt[faces]
        result[key] = {'mesh': str(prim.GetPath()), 'material': mpath, 'files': files, 'triangles': int(len(faces)), 'uv_interp': interp}
np.savez(out + '/geometry.npz', **arrays)
json.dump(result, open(out + '/materials.json', 'w'), indent=1)
for k, v in result.items():
    print(k, v['triangles'], v['files'])
