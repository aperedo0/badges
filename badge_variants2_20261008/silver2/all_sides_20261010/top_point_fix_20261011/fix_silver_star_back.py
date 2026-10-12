"""Stop the Silver star's back faces poking through its front while it turns.

The star's front faces run from the front apex to the star's BACK outline,
and the 2026-10-10 back was mirrored from them, so its faces run from the back
apex to a FRONT outline. Near the edges the two sets cross, and once the badge
turns past about 60 degrees slivers of the back faces show through the front.

This keeps every front face exactly as it is and makes the back faces end on
the same outline the front faces end on (same points), so the two never cross.
The side walls between the two outlines are then left with no outline to join
and are deleted. Flat normals are recomputed for the back faces. Run it on the
model whose top point is already fixed (fix_silver_top_point.py).

Usage: python -I fix_silver_star_back.py <compacted.usdc> <out.usdc>
"""
import sys
import numpy as np
from pxr import Usd, UsdGeom, Vt, Gf

src, out = sys.argv[1], sys.argv[2]
stage = Usd.Stage.Open(src)
prim = stage.GetPrimAtPath('/Silver2/Silver2_Star_Satin')
mesh = UsdGeom.Mesh(prim)
points = np.array(mesh.GetPointsAttr().Get(), dtype=np.float64)
indices = np.array(mesh.GetFaceVertexIndicesAttr().Get()).reshape(-1, 3)
normals = np.array(mesh.GetNormalsAttr().Get(), dtype=np.float64).reshape(-1, 3, 3)
uv_primvar = UsdGeom.PrimvarsAPI(prim).GetPrimvar('USDZ_UV')
uvs = np.array(uv_primvar.Get(), dtype=np.float64).reshape(-1, 3, 2)

def face_normal(face):
    c = points[indices[face]]
    n = np.cross(c[1] - c[0], c[2] - c[0])
    return n / np.linalg.norm(n)

face_normals = np.array([face_normal(f) for f in range(len(indices))])
front = face_normals[:, 2] > 0.4
back = face_normals[:, 2] < -0.4
wall = ~front & ~back
assert front.sum() == 10 and back.sum() == 10 and wall.sum() == 18, (front.sum(), back.sum(), wall.sum())

front_apex = max(set(indices[front].ravel()), key=lambda i: points[i, 2])
back_apex = min(set(indices[back].ravel()), key=lambda i: points[i, 2])
front_outline = {i for i in indices[front].ravel() if i != front_apex}

def same_xy(i, j):
    return np.allclose(points[i, :2], points[j, :2], atol=1e-4)

# Each back-face outline point moves to the front faces' outline point above it.
remap = {}
for i in set(indices[back].ravel()) - {back_apex}:
    matches = [j for j in front_outline if same_xy(i, j)]
    assert len(matches) == 1, (i, matches)
    remap[i] = matches[0]
for face in np.where(back)[0]:
    indices[face] = [remap.get(i, i) for i in indices[face]]
    assert face_normal(face)[2] < 0, f'back face {face} would face forward'
    normals[face] = face_normal(face)

keep = ~wall
old_to_new = -np.ones(len(indices), dtype=int)
old_to_new[keep] = np.arange(keep.sum())
mesh.GetFaceVertexCountsAttr().Set(Vt.IntArray([3] * int(keep.sum())))
mesh.GetFaceVertexIndicesAttr().Set(Vt.IntArray(indices[keep].ravel().tolist()))
mesh.GetNormalsAttr().Set(Vt.Vec3fArray([Gf.Vec3f(*v) for v in normals[keep].reshape(-1, 3)]))
uv_primvar.Set(Vt.Vec2fArray([Gf.Vec2f(*v) for v in uvs[keep].reshape(-1, 2)]))
for subset in UsdGeom.Subset.GetAllGeomSubsets(mesh):
    kept = [int(old_to_new[i]) for i in subset.GetIndicesAttr().Get() if keep[i]]
    if kept:
        subset.GetIndicesAttr().Set(Vt.IntArray(kept))
    else:
        stage.RemovePrim(subset.GetPath())
stage.GetRootLayer().Export(out)
print('front faces kept', int(front.sum()), 'back faces moved', int(back.sum()), 'walls deleted', int(wall.sum()))
