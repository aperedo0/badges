"""usd_info.py <model.usdz> : meshes, triangle counts, bounds, materials and their inputs/textures."""
import sys, numpy as np
from pxr import Usd, UsdGeom, UsdShade
st = Usd.Stage.Open(sys.argv[1])
for p in st.Traverse():
    if p.IsA(UsdGeom.Mesh):
        m = UsdGeom.Mesh(p); pts = np.array(m.GetPointsAttr().Get()); n = len(m.GetFaceVertexCountsAttr().Get())
        mat = UsdShade.MaterialBindingAPI(p).ComputeBoundMaterial()[0]
        print('MESH', p.GetPath(), n, 'faces', pts.min(0).round(3), pts.max(0).round(3), '->', mat.GetPath() if mat else None,
              [pv.GetName() for pv in UsdGeom.PrimvarsAPI(p).GetPrimvars()])
    if p.IsA(UsdShade.Shader):
        s = UsdShade.Shader(p); ins = {}
        for i in s.GetInputs():
            v = i.Get()
            if i.HasConnectedSource():
                v = '<-' + str(i.GetConnectedSources()[0][0].source.GetPath().name)
            ins[i.GetBaseName()] = v
        print('  SHADER', p.GetPath(), s.GetIdAttr().Get(), ins)
