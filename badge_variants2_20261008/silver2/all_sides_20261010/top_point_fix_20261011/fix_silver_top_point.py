"""Fix the Silver star's top point (flicker while the badge turns).

The star's front face ends at the top point's FRONT tip and its back face at a
separate BACK tip, so the two edges cross half way along each top side wall and
the wall cannot be covered without a fold: one half faces out, one faces in,
and they swap in and out of view as the badge turns. This moves the back tip
onto the front tip (the front is untouched), so each top side wall becomes one
triangle built like the walls of the other four points, and deletes the two
triangles that collapse to nothing. Normals of the touched faces are
recomputed (the star's normals are flat per face).

Usage: python -I fix_silver_top_point.py <extracted compacted.usdc> <out.usdc>
"""
import sys
import numpy as np
from pxr import Usd, UsdGeom, Vt, Gf

src, out = sys.argv[1], sys.argv[2]
stage = Usd.Stage.Open(src)
prim = stage.GetPrimAtPath('/Silver2/Silver2_Star_Satin')
mesh = UsdGeom.Mesh(prim)
points = np.array(mesh.GetPointsAttr().Get(), dtype=np.float64)
counts = np.array(mesh.GetFaceVertexCountsAttr().Get())
indices = np.array(mesh.GetFaceVertexIndicesAttr().Get()).reshape(-1, 3)
normals = np.array(mesh.GetNormalsAttr().Get(), dtype=np.float64).reshape(-1, 3, 3)
uv_primvar = UsdGeom.PrimvarsAPI(prim).GetPrimvar('USDZ_UV')
uvs = np.array(uv_primvar.Get(), dtype=np.float64).reshape(-1, 3, 2)
assert (counts == 3).all() and len(indices) == 40

def find(target):
    hits = [i for i in range(len(points)) if np.allclose(points[i], target, atol=2e-3)]
    assert len(hits) == 1, (target, hits)
    return hits[0]

front_tip = find([-0.006, 2.657, 0.084])
back_tip = find([-0.006, 2.657, -0.074])
assert (front_tip, back_tip) == (2, 24), (front_tip, back_tip)

# Every face that used the back tip now uses the front tip.
indices[indices == back_tip] = front_tip

# Faces with a repeated corner have collapsed to nothing: delete them.
keep = np.array([len(set(face)) == 3 for face in indices])
removed = np.where(~keep)[0].tolist()
assert removed == [21, 38], removed

# Flat normals for the faces that moved (their corners changed).
for face in range(len(indices)):
    corners = points[indices[face]]
    n = np.cross(corners[1] - corners[0], corners[2] - corners[0])
    n /= np.linalg.norm(n)
    if not np.allclose(normals[face], n, atol=1e-6):
        normals[face] = n

old_to_new = -np.ones(len(indices), dtype=int)
old_to_new[keep] = np.arange(keep.sum())

mesh.GetFaceVertexCountsAttr().Set(Vt.IntArray([3] * int(keep.sum())))
mesh.GetFaceVertexIndicesAttr().Set(Vt.IntArray(indices[keep].ravel().tolist()))
mesh.GetNormalsAttr().Set(Vt.Vec3fArray([Gf.Vec3f(*v) for v in normals[keep].reshape(-1, 3)]))
uv_primvar.Set(Vt.Vec2fArray([Gf.Vec2f(*v) for v in uvs[keep].reshape(-1, 2)]))
for subset in UsdGeom.Subset.GetAllGeomSubsets(mesh):
    attr = subset.GetIndicesAttr()
    remapped = [int(old_to_new[i]) for i in attr.Get() if keep[i]]
    attr.Set(Vt.IntArray(remapped))

stage.GetRootLayer().Export(out)
print('removed faces', removed, 'faces now', int(keep.sum()))
