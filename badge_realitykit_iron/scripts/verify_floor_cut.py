"""Checks a floor-cut export against the uncut export, triangle by triangle.

  Blender --background --factory-startup --python verify_floor_cut.py -- UNCUT.usdz CUT.usdz HEIGHT [report.json]

For every mesh: min and max height (USD Y), triangle counts, and a SHA-1 of every
geometry array (so untouched meshes can be shown byte-identical). For a cut mesh:
  - every uncut triangle entirely above the floor must reappear in the cut file with
    bit-identical corner positions, normals, UVs (every UV set) and material;
  - every other triangle in the cut file must lie on or above the floor, inside one of
    the uncut triangles that crossed the floor, with corner normals and UVs equal to
    that triangle's own corner values interpolated at the corner (the edge
    interpolation the rule asks for), normals compared after normalizing.
"""
import hashlib
import json
import math
import sys

import numpy as np
from pxr import Usd, UsdGeom, UsdShade

args = sys.argv[sys.argv.index('--') + 1:]
uncut_path, cut_path, height = args[0], args[1], float(args[2])
out_path = args[3] if len(args) > 3 else None
EPS = 1e-5


def load(path):
    stage = Usd.Stage.Open(path)
    meshes = {}
    for prim in stage.Traverse():
        if not prim.IsA(UsdGeom.Mesh):
            continue
        mesh = UsdGeom.Mesh(prim)
        counts = np.array(mesh.GetFaceVertexCountsAttr().Get())
        assert (counts == 3).all()
        idx = np.array(mesh.GetFaceVertexIndicesAttr().Get()).reshape(-1, 3)
        pts = np.array(mesh.GetPointsAttr().Get(), dtype=np.float32)
        normals = np.array(mesh.GetNormalsAttr().Get(), dtype=np.float32).reshape(-1, 3, 3)
        uvs = {}
        for pv in UsdGeom.PrimvarsAPI(prim).GetPrimvars():
            if str(pv.GetTypeName()) == 'texCoord2f[]':
                assert pv.GetInterpolation() == 'faceVarying'
                uvs[str(pv.GetPrimvarName())] = np.array(pv.ComputeFlattened(), dtype=np.float32).reshape(-1, 3, 2)
        material = np.full(len(idx), '', dtype=object)
        bound = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0]
        material[:] = bound.GetPath().name if bound else ''
        for subset in UsdGeom.Subset.GetAllGeomSubsets(UsdGeom.Imageable(prim)):
            m = UsdShade.MaterialBindingAPI(subset.GetPrim()).ComputeBoundMaterial()[0]
            material[np.array(subset.GetIndicesAttr().Get(), dtype=int)] = m.GetPath().name
        digest = hashlib.sha1()
        for arr in [pts, idx, normals] + [uvs[k] for k in sorted(uvs)]:
            digest.update(np.ascontiguousarray(arr).tobytes())
        digest.update('|'.join(material).encode())
        meshes[prim.GetName()] = dict(pts=pts, idx=idx, normals=normals, uvs=uvs, material=material,
                                      sha1=digest.hexdigest())
    return meshes


def canonical(corners):
    """Cyclic rotation starting at the smallest corner, so the key ignores the start corner."""
    keys = [tuple(float(x) for x in c) for c in corners]
    start = min(range(3), key=lambda i: keys[i])
    order = [(start + k) % 3 for k in range(3)]
    return tuple(keys[i] for i in order), order


def barycentric(p, a, b, c):
    v0, v1, v2 = b - a, c - a, p - a
    d00, d01, d11, d20, d21 = v0 @ v0, v0 @ v1, v1 @ v1, v2 @ v0, v2 @ v1
    den = d00 * d11 - d01 * d01
    w1 = (d11 * d20 - d01 * d21) / den
    w2 = (d00 * d21 - d01 * d20) / den
    return np.array([1 - w1 - w2, w1, w2])


def angle(a, b):
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    return math.degrees(math.acos(max(-1.0, min(1.0, float(a @ b)))))


old, new = load(uncut_path), load(cut_path)
report = dict(uncut=uncut_path, cut=cut_path, height=height, meshes={})
for name in old:
    a, b = old[name], new[name]
    row = dict(min_y_uncut=float(a['pts'][:, 1].min()), min_y_cut=float(b['pts'][:, 1].min()),
               max_uncut=a['pts'].max(0).tolist(), max_cut=b['pts'].max(0).tolist(),
               triangles_uncut=len(a['idx']), triangles_cut=len(b['idx']),
               byte_identical=a['sha1'] == b['sha1'], sha1_uncut=a['sha1'], sha1_cut=b['sha1'])
    report['meshes'][name] = row
    if row['byte_identical']:
        continue
    corner_y = a['pts'][a['idx']][:, :, 1]
    above = (corner_y > height + EPS).all(1)
    below = (corner_y <= height + EPS).all(1)
    crossing = ~above & ~below
    index = {}
    for t in range(len(b['idx'])):
        key, order = canonical(b['pts'][b['idx'][t]])
        index[key] = (t, order)
    kept_identical, kept_missing, kept_changed, matched = 0, 0, 0, set()
    for t in np.nonzero(above)[0]:
        key, order = canonical(a['pts'][a['idx'][t]])
        if key not in index:
            kept_missing += 1
            continue
        u, order_b = index[key]
        matched.add(u)
        same = (np.array_equal(a['normals'][t][order], b['normals'][u][order_b])
                and all(np.array_equal(a['uvs'][k][t][order], b['uvs'][k][u][order_b]) for k in a['uvs'])
                and a['material'][t] == b['material'][u])
        kept_identical += same
        kept_changed += not same
    # New triangles: inside a crossing source triangle, corner data = source data interpolated.
    sources = np.nonzero(crossing)[0]
    src_pts = a['pts'][a['idx'][sources]]
    worst = dict(normal_deg=0.0, uv=0.0, below_floor=0.0, plane_distance=0.0)
    new_tris, material_mismatch = 0, 0
    for u in range(len(b['idx'])):
        if u in matched:
            continue
        new_tris += 1
        tri = b['pts'][b['idx'][u]].astype(np.float64)
        worst['below_floor'] = max(worst['below_floor'], float(height - tri[:, 1].min()))
        centre = tri.mean(0)
        best = None
        for s, (p0, p1, p2) in zip(sources, src_pts.astype(np.float64)):
            n = np.cross(p1 - p0, p2 - p0)
            n /= np.linalg.norm(n)
            dist = abs((centre - p0) @ n)
            w = barycentric(centre, p0, p1, p2)
            if w.min() > -1e-4 and (best is None or dist < best[0]):
                best = (dist, s)
        assert best is not None, f'triangle {u} lies in no crossing source triangle'
        worst['plane_distance'] = max(worst['plane_distance'], best[0])
        s = best[1]
        p0, p1, p2 = a['pts'][a['idx'][s]].astype(np.float64)
        material_mismatch += a['material'][s] != b['material'][u]
        for c in range(3):
            w = barycentric(tri[c], p0, p1, p2)
            normal = w @ (a['normals'][s] / np.linalg.norm(a['normals'][s], axis=1, keepdims=True))
            worst['normal_deg'] = max(worst['normal_deg'], angle(normal, b['normals'][u][c].astype(np.float64)))
            for k in a['uvs']:
                uv = w @ a['uvs'][k][s].astype(np.float64)
                worst['uv'] = max(worst['uv'], float(np.abs(uv - b['uvs'][k][u][c]).max()))
    row.update(uncut_triangles_above=int(above.sum()), uncut_triangles_below=int(below.sum()),
               uncut_triangles_crossing=int(crossing.sum()), kept_bit_identical=int(kept_identical),
               kept_changed=int(kept_changed), kept_missing=int(kept_missing), new_cut_triangles=new_tris,
               new_triangle_material_mismatches=int(material_mismatch),
               new_corner_normal_max_deg_from_edge_interpolation=worst['normal_deg'],
               new_corner_uv_max_abs_from_edge_interpolation=worst['uv'],
               new_triangle_max_distance_from_source_plane=worst['plane_distance'],
               max_depth_below_floor=worst['below_floor'])
print(json.dumps(report, indent=1))
if out_path:
    json.dump(report, open(out_path, 'w'), indent=1)
