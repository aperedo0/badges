"""Blender python: scale_usd.py <usdc> <s> : scales every mesh's points by s about (0, -2.455, 0), so the float gap stays."""
import sys, numpy as np
from pxr import Usd, UsdGeom, Vt, Gf
st = Usd.Stage.Open(sys.argv[1]); s = float(sys.argv[2]); pivot = np.array([0, -2.455, 0])
for prim in st.Traverse():
    if not prim.IsA(UsdGeom.Mesh): continue
    m = UsdGeom.Mesh(prim); pts = np.array(m.GetPointsAttr().Get(), dtype=np.float64)
    new = pivot + s * (pts - pivot)
    m.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(new.astype(np.float32)))
    m.GetExtentAttr().Set(Vt.Vec3fArray([Gf.Vec3f(*new.min(0)), Gf.Vec3f(*new.max(0))]))
st.GetRootLayer().Save()
b = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ['default', 'render']).ComputeWorldBound(st.GetPseudoRoot()).ComputeAlignedRange()
print('scaled', s, 'bounds', b.GetMin(), b.GetMax())
