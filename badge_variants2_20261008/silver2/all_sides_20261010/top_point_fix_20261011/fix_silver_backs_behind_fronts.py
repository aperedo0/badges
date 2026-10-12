"""Keep every back surface of the Silver laurel behind its own front surface.

The 2026-10-10 Silver backs were mirrored from the fronts. Where a leaf's or
stem's front dips below the middle of its thickness (near the tips), the
mirrored back comes out IN FRONT of the front there, so slivers of the back
show through while the badge turns. This moves only those back points: each
point used by back-facing faces (and by no front-facing face) that sits in
front of, or within `GAP` of, its own leaf's front surface is pushed back to
`GAP` behind that surface. Front faces, walls, textures, UVs and normals are
untouched; points that are already behind do not move.

"Its own" front: faces are grouped into connected pieces (one leaf, one stem
branch), so a back point is only ever compared with the front of its own piece.

Usage: python -I fix_silver_backs_behind_fronts.py <compacted.usdc> <out.usdc>
"""
import sys
import numpy as np
from pxr import Usd, UsdGeom, Vt, Gf

GAP = 0.004
MESHES = ['Silver2_LeafBlades_Satin', 'Silver2_LeafEdges_Satin', 'Silver2_InnerLeaves_Satin',
          'Silver2_UpperLeaves_Satin', 'Silver2_Stems_Satin']

src, out = sys.argv[1], sys.argv[2]
stage = Usd.Stage.Open(src)
report = []
for name in MESHES:
    mesh = UsdGeom.Mesh(stage.GetPrimAtPath('/Silver2/' + name))
    points = np.array(mesh.GetPointsAttr().Get(), dtype=np.float64)
    tris = np.array(mesh.GetFaceVertexIndicesAttr().Get()).reshape(-1, 3)
    assert (np.array(mesh.GetFaceVertexCountsAttr().Get()) == 3).all()

    # Weld by position so UV-split copies of one corner move together.
    keys = {}
    weld = np.array([keys.setdefault(tuple(p), len(keys)) for p in np.round(points, 6)])
    welded = np.zeros((len(keys), 3))
    welded[weld] = points
    wtris = weld[tris]

    corners = welded[wtris]
    normal = np.cross(corners[:, 1] - corners[:, 0], corners[:, 2] - corners[:, 0])
    normal /= np.linalg.norm(normal, axis=1, keepdims=True) + 1e-15
    front = normal[:, 2] > 0.05
    back = normal[:, 2] < -0.05

    # Connected pieces over welded points (union-find).
    parent = np.arange(len(welded))
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for a, b, c in wtris:
        ra, rb, rc = root(a), root(b), root(c)
        parent[rb] = ra
        parent[rc] = ra
    piece_of_point = np.array([root(i) for i in range(len(welded))])
    piece_of_tri = piece_of_point[wtris[:, 0]]

    on_front = np.zeros(len(welded), bool)
    on_front[wtris[front].ravel()] = True
    on_back = np.zeros(len(welded), bool)
    on_back[wtris[back].ravel()] = True
    movable = on_back & ~on_front

    new_welded = welded.copy()
    moved = 0
    largest = 0.0
    for piece in np.unique(piece_of_tri):
        ftris = corners[front & (piece_of_tri == piece)]
        if len(ftris) == 0:
            continue
        a, b, c = ftris[:, 0], ftris[:, 1], ftris[:, 2]
        lo = ftris[:, :, :2].min(1)
        hi = ftris[:, :, :2].max(1)
        for i in np.where(movable & (piece_of_point == piece))[0]:
            x, y = welded[i, 0], welded[i, 1]
            cand = np.where((lo[:, 0] <= x) & (x <= hi[:, 0]) & (lo[:, 1] <= y) & (y <= hi[:, 1]))[0]
            best = None
            for t in cand:
                v0 = b[t, :2] - a[t, :2]; v1 = c[t, :2] - a[t, :2]; v2 = np.array([x, y]) - a[t, :2]
                den = v0[0] * v1[1] - v1[0] * v0[1]
                if abs(den) < 1e-14:
                    continue
                s = (v2[0] * v1[1] - v1[0] * v2[1]) / den
                u = (v0[0] * v2[1] - v2[0] * v0[1]) / den
                if s < -1e-9 or u < -1e-9 or s + u > 1 + 1e-9:
                    continue
                z = a[t, 2] + s * (b[t, 2] - a[t, 2]) + u * (c[t, 2] - a[t, 2])
                best = z if best is None else max(best, z)
            if best is not None and welded[i, 2] > best - GAP:
                largest = max(largest, welded[i, 2] - (best - GAP))
                new_welded[i, 2] = best - GAP
                moved += 1

    mesh.GetPointsAttr().Set(Vt.Vec3fArray([Gf.Vec3f(*p) for p in new_welded[weld]]))
    report.append(f'{name}: moved {moved} of {int(movable.sum())} back points, largest move {largest:.4f}')
stage.GetRootLayer().Export(out)
print('\n'.join(report))
