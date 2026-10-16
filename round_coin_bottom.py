"""Restore the complete circular shell for the five hovering coin previews.

Use Blender's bundled Python (pxr/numpy): SOURCE.usdz OUTPUT.usdz.
Profile, materials and emblem are preserved. Only the former floor cut is
removed. These models require preview lift 0.56 so their low point floats at
Y -2.455; they must not be installed with the old floor-standing placement.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import math
import os
import sys
import tempfile
import zipfile
import subprocess

import numpy as np
from pxr import Gf, Usd, UsdGeom, Vt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coin_rim import SHELL_PATH, brush_uv


def full_shell():
    profile = np.array([[2.420,.190], [2.485,.300], [2.945,.300],
                        [3.015,.230], [3.015,-.560], [2.945,-.630],
                        [2.485,-.630], [2.420,-.520]])
    profile_roles = ['inner', 'face', 'bevel', 'side', 'bevel', 'face', 'inner', 'inner']
    points, normals, roles = [], [], []
    for j, (p1, p2) in enumerate(zip(profile, np.roll(profile, -1, axis=0))):
        dr, dz = p2 - p1
        for k in range(256):
            a, b = k * math.tau / 256, (k + 1) * math.tau / 256
            quad = [np.array([p1[0]*math.cos(a), p1[0]*math.sin(a), p1[1]]),
                    np.array([p2[0]*math.cos(a), p2[0]*math.sin(a), p2[1]]),
                    np.array([p2[0]*math.cos(b), p2[0]*math.sin(b), p2[1]]),
                    np.array([p1[0]*math.cos(b), p1[0]*math.sin(b), p1[1]])]
            for indices in [(0, 1, 2), (0, 2, 3)]:
                tri = np.array([quad[i] for i in indices])
                angle = np.arctan2(tri[:,1], tri[:,0])
                normal = np.c_[-dz*np.cos(angle), -dz*np.sin(angle), np.full(3, dr)]
                normal /= np.linalg.norm(normal, axis=1, keepdims=True)
                points.extend(tri)
                normals.extend(normal)
                roles.append(profile_roles[j])
    points, normals = np.array(points), np.array(normals)
    triangles = np.arange(len(points)).reshape(-1, 3)
    planar = (points[:,:2] + 3.015) / 6.03
    rear = normals.reshape(-1,3,3).mean(1)[:,2] < -.1
    planar[triangles[rear].ravel(),0] = 1 - planar[triangles[rear].ravel(),0]
    brushed, _ = brush_uv(points, triangles, planar[triangles])
    return points, triangles, normals, np.array(roles), planar, brushed


def build(source, output):
    source, output = Path(source), Path(output)
    with tempfile.TemporaryDirectory(prefix='round_coin_') as tmp:
        pkg = Path(tmp)
        with zipfile.ZipFile(source) as archive:
            names = archive.namelist()
            archive.extractall(pkg)
        usd = next(n for n in names if n.endswith('.usdc'))
        stage = Usd.Stage.Open(str(pkg / usd))
        before = {str(a.GetPath()): a.Get() for p in stage.Traverse()
                  if not str(p.GetPath()).startswith(SHELL_PATH) for a in p.GetAttributes()}
        mesh = UsdGeom.Mesh(stage.GetPrimAtPath(SHELL_PATH))
        assert mesh
        points, triangles, normals, roles, planar, brushed = full_shell()
        mesh.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(points.astype(np.float32)))
        mesh.GetFaceVertexCountsAttr().Set(Vt.IntArray.FromNumpy(np.full(len(triangles), 3, dtype=np.int32)))
        mesh.GetFaceVertexIndicesAttr().Set(Vt.IntArray.FromNumpy(triangles.astype(np.int32).ravel()))
        mesh.GetNormalsAttr().Set(Vt.Vec3fArray.FromNumpy(normals.astype(np.float32)))
        mesh.SetNormalsInterpolation('faceVarying')
        mesh.GetExtentAttr().Set([Gf.Vec3f(*points.min(0)), Gf.Vec3f(*points.max(0))])
        api = UsdGeom.PrimvarsAPI(mesh)
        for name in ['USDZ_UV', 'Machining_UV']:
            pv = api.GetPrimvar(name)
            assert pv and not pv.IsIndexed()
            pv.SetInterpolation('vertex')
            pv.Set(Vt.Vec2fArray.FromNumpy(planar.astype(np.float32)))
        api.GetPrimvar('RimBrushUV').Set(Vt.Vec2fArray.FromNumpy(brushed.reshape(-1,2).astype(np.float32)))
        side_uv = api.GetPrimvar('RimSideUV')
        if side_uv:
            uv = np.c_[np.arctan2(points[:,1], points[:,0]) / math.tau + .00390625,
                       (points[:,2] + .630) / .930]
            side_uv.SetInterpolation('faceVarying')
            side_uv.Set(Vt.Vec2fArray.FromNumpy(uv.astype(np.float32)))
        for subset in UsdGeom.Subset.GetGeomSubsets(mesh, 'face', 'materialBind'):
            role = subset.GetPrim().GetName()
            subset.GetIndicesAttr().Set(np.flatnonzero(roles == role).tolist())
        # Every welded edge now has two faces, including the restored bottom.
        _, welded = np.unique(np.round(points / 1e-5).astype(np.int64), axis=0, return_inverse=True)
        counts = Counter(tuple(sorted(e)) for f in welded[triangles]
                         for e in [(f[0], f[1]), (f[1], f[2]), (f[2], f[0])])
        assert all(n == 2 for n in counts.values())
        after = {str(a.GetPath()): a.Get() for p in stage.Traverse()
                 if not str(p.GetPath()).startswith(SHELL_PATH) for a in p.GetAttributes()}
        assert before == after, 'A material or emblem changed.'
        assert abs(points[:,1].min() + 3.015) < 1e-6
        assert abs(points[:,1].max() - 3.015) < 1e-6
        compact_layer = pkg / 'closed_shell.usdc'
        assert stage.GetRootLayer().Export(str(compact_layer))
        compact_layer.replace(pkg / usd)
        for n in names:
            os.utime(pkg / n, (946684800, 946684800))
        candidate = pkg / 'round.usdz'
        subprocess.run(['/usr/bin/usdzip', str(candidate)] + names, cwd=pkg, check=True, capture_output=True)
        gate = subprocess.run(['/usr/bin/usdchecker', '--arkit', str(candidate)], capture_output=True, text=True)
        assert gate.returncode == 0, gate.stdout + gate.stderr
        with zipfile.ZipFile(source) as a, zipfile.ZipFile(candidate) as b:
            assert all(a.read(n) == b.read(n) for n in names if n != usd)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(candidate.read_bytes())
    return {'file': str(output), 'bytes': output.stat().st_size,
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'closed_round_shell': True, 'shell_triangles': len(triangles),
            'materials_emblem_textures': 'unchanged', 'USD_validation': 'passed',
            'required_preview_lift': .56, 'float_lowest_y': -2.455}


if __name__ == '__main__':
    print(json.dumps(build(*sys.argv[1:])))
