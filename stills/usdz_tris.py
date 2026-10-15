"""usdz_tris.py <in.usdz> <out.npz> : every mesh triangle in world space as ALLP (N,3,3), for still_cut.py's alpha."""
import sys, numpy as np
from pxr import Usd, UsdGeom
stage = Usd.Stage.Open(sys.argv[1])
print('upAxis', UsdGeom.GetStageUpAxis(stage), 'metersPerUnit', UsdGeom.GetStageMetersPerUnit(stage))
tris = []
for prim in stage.Traverse():
    if not prim.IsA(UsdGeom.Mesh):
        continue
    m = UsdGeom.Mesh(prim)
    pts = np.array(m.GetPointsAttr().Get(), float)
    xf = np.array(UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(Usd.TimeCode.Default()), float)
    pts = np.c_[pts, np.ones(len(pts))] @ xf
    pts = pts[:, :3]
    counts = m.GetFaceVertexCountsAttr().Get(); idx = np.array(m.GetFaceVertexIndicesAttr().Get())
    o = 0
    for c in counts:
        f = idx[o:o + c]
        for k in range(1, c - 1):
            tris.append(pts[[f[0], f[k], f[k + 1]]])
        o += c
ALLP = np.array(tris)
print(len(ALLP), 'triangles; bounds', ALLP.reshape(-1, 3).min(0).round(3), ALLP.reshape(-1, 3).max(0).round(3))
np.savez_compressed(sys.argv[2], ALLP=ALLP)
