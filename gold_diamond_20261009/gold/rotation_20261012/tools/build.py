"""Make the approved round crown repeat one complete section eight times."""
from pathlib import Path
import json
import shutil
import sys
import hashlib
import tempfile
import zipfile

import numpy as np
from pxr import Sdf, Usd, UsdGeom, UsdUtils

WORK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORK.parents[2] / "all_sides_20261010/tools"))
from model_common import read_mesh, write_mesh, normals, shader_material


def rotate(points, angle):
    return (points @ axis)[:, None] * axis + (
        np.cos(angle) * (points - (points @ axis)[:, None] * axis)
        + np.sin(angle) * np.cross(axis, points)
    )


baseline = WORK.parent / "all_sides_20261010/mobile/gold_badge_mobile.usdz"
assert hashlib.sha256(baseline.read_bytes()).hexdigest() == "70ea3bcab53cb3f1fb024cd9b1a46fed56cf43268a1a70e6e1d23ab037a24530"
scratch = tempfile.TemporaryDirectory(prefix="gold-pattern-", dir="/tmp")
extracted = Path(scratch.name) / "source"
with zipfile.ZipFile(baseline) as package:
    package.extractall(extracted)
source = next(extracted.glob("*.usd*"))
out = Path(scratch.name) / "model"
out.mkdir()
for folder in extracted.iterdir():
    if folder.is_dir():
        shutil.copytree(folder, out / folder.name, dirs_exist_ok=True)
stage = Usd.Stage.Open(str(source))
layer = Sdf.Layer.CreateAnonymous()
layer.TransferContent(stage.GetRootLayer())
stage = Usd.Stage.Open(layer)
axis = np.array([0, .9553869282796957, -.2953571012728279])
radial_z = np.cross([1, 0, 0], axis)
center = np.array([0, -2.0006320204744803, .7454742431640625]) * .995
band_height = .6300864902666727 * .995
band_radius = 2.644996483626511 * .995
peak = 2.5885693469707665
valley = 1.21
flare = .17614380033279456
thickness = .10
count, rows = 512, 12
angles = np.arange(count) * (2 * np.pi / count)
phase = ((angles + np.pi / 8) % (np.pi / 4) - np.pi / 8) / (np.pi / 8)
top = valley + (peak - valley) * (1 - np.abs(phase)) ** 3
front = "/GoldCrown/Materials/GoldCrown_Front"
inside = shader_material(stage, "RoundCrown_InnerGold", [.32, .16, .016], .55)
edge = shader_material(stage, "RoundCrown_RolledGold", [.18, .085, .008], .65)

# Retain the original gold surface atlas. One centered point's complete
# texture section repeats with the shape, with matching samples at valleys.
p, f, n, m, uv = read_mesh(stage.GetPrimAtPath("/GoldCrown/GoldCrown_ScallopedShell"))
original_uv = np.zeros((len(p), 2))
weights = np.zeros(len(p))
chart = uv["BadgeUV"]
for corner in range(3):
    np.add.at(original_uv, f[:, corner], chart[:, corner])
    np.add.at(weights, f[:, corner], 1)
original_uv /= np.maximum(weights[:, None], 1)
source_angles = []
for row in range(6):
    local = p[row * 281 : (row + 1) * 281] - center
    source_angles.append(np.arctan2(local[:, 0], local @ radial_z))

# Eight identical round finials and collars keep their existing detailed
# meshes and finish, rather than the unequal projected front/rear copies.
details = {}
for name in ["Finial3", "Collar3"]:
    details[name] = read_mesh(stage.GetPrimAtPath("/GoldCrown/GoldCrown_" + name))
# Preserve the exact detailed cap's envelope and atlas while using every
# other vertex on its regular latitude/longitude grid. A 32-segment cap is
# already smooth at the badge's phone size.
p, f, n, m, uv = details["Finial3"]
assert len(p) == 2 + 29 * 64
selected = np.array([0] + [1 + (j - 1) * 64 + k for j in range(2, 30, 2) for k in range(0, 64, 2)] + [len(p) - 1])
vertex_uv = {}
for key, chart in uv.items():
    values, hits = np.zeros((len(p), 2)), np.zeros(len(p))
    for c in range(3):
        np.add.at(values, f[:, c], chart[:, c])
        np.add.at(hits, f[:, c], 1)
    vertex_uv[key] = (values / np.maximum(hits[:, None], 1))[selected]
new_faces = []
for k in range(32):
    new_faces.append([0, 1 + k, 1 + (k + 1) % 32])
for j in range(13):
    for k in range(32):
        a, b = 1 + j * 32 + k, 1 + j * 32 + (k + 1) % 32
        c, d = b + 32, a + 32
        new_faces.extend([[a, d, c], [a, c, b]])
for k in range(32):
    new_faces.append([len(selected) - 1, 1 + 13 * 32 + (k + 1) % 32, 1 + 13 * 32 + k])
new_p, new_faces = p[selected], np.array(new_faces)
volume = np.einsum('ij,ij->i', new_p[new_faces[:, 0]], np.cross(new_p[new_faces[:, 1]], new_p[new_faces[:, 2]])).sum() / 6
if volume < 0:
    new_faces = new_faces[:, ::-1]
assert len(set(m)) == 1
details["Finial3"] = (new_p, new_faces, normals(new_p, new_faces, True),
                     np.array([m[0]] * len(new_faces)), {key: a[new_faces] for key, a in vertex_uv.items()})
for prim in [q for q in stage.Traverse() if q.IsA(UsdGeom.Mesh)]:
    if not any(
        token in prim.GetName() for token in ["TrueCircularBand", "CircularUpperLip", "CircularLowerLip"]
    ):
        stage.RemovePrim(prim.GetPath())
for i in range(8):
    for name, (p, f, n, m, uv) in details.items():
        write_mesh(stage, "/GoldCrown/Repeat_%02d_%s" % (i, name),
                   center + rotate(p - center, i * np.pi / 4), f,
                   rotate(n.reshape(-1, 3), i * np.pi / 4).reshape(n.shape), m, uv)

points, texcoords = [], []
for inner in range(2):
    for row in range(rows + 1):
        fraction = row / rows
        height = band_height - .012 + fraction * (top - band_height + .012)
        radius = band_radius - .012 + flare * (height - band_height) - inner * thickness
        points.extend(center + height[:, None] * axis + radius[:, None] * (
            np.sin(angles)[:, None] * [1, 0, 0] + np.cos(angles)[:, None] * radial_z))
        source_row = fraction * 5
        lower = int(source_row)
        upper = min(5, lower + 1)
        blend = source_row - lower
        # The old central scallop's valleys sit roughly eighteen degrees
        # away from its peak; expand that same curved section evenly.
        old_angle = phase * np.radians(18)
        value = np.empty((count, 2))
        for channel in range(2):
            lo = np.interp(old_angle, source_angles[lower], original_uv[lower * 281:(lower + 1) * 281, channel])
            hi = np.interp(old_angle, source_angles[upper], original_uv[upper * 281:(upper + 1) * 281, channel])
            value[:, channel] = lo * (1 - blend) + hi * blend
        # Both valley endpoints meet on the same texel. Fade the U chart
        # smoothly into the average endpoint only in the lowest valley.
        seam = np.clip((np.abs(phase) - .90) / .10, 0, 1)
        seam = seam * seam * (3 - 2 * seam)
        endpoint = np.mean(value[[count // 16, count - count // 16]], axis=0)
        value = value * (1 - seam[:, None]) + endpoint * seam[:, None]
        texcoords.extend(value)
points, texcoords = np.array(points), np.array(texcoords)
half = (rows + 1) * count
faces, materials = [], []
for inner in range(2):
    offset = inner * half
    for row in range(rows):
        for k in range(count):
            nxt = (k + 1) % count
            a, b = offset + row * count + k, offset + row * count + nxt
            c, d = b + count, a + count
            pair = [[a, b, c], [a, c, d]]
            if not inner:
                pair = [t[::-1] for t in pair]
            faces.extend(pair)
            materials.extend([inside if inner else front] * 2)
for k in range(count):
    nxt = (k + 1) % count
    for row in [0, rows]:
        a, b = row * count + k, row * count + nxt
        pair = [[a, a + half, b + half], [a, b + half, b]]
        if row == 0:
            pair = [t[::-1] for t in pair]
        faces.extend(pair)
        materials.extend([edge] * 2)
faces = np.array(faces)
faces = faces[:, ::-1]
write_mesh(stage, "/GoldCrown/ContinuousEightPointWall", points, faces,
           normals(points, faces, True), np.array(materials), {"BadgeUV": texcoords[faces]})

# A single closed rolled lip follows all eight scallops without front/side
# joins or overlapped tubes. Its thickness stays below the finial collars.
ring = points[rows * count:(rows + 1) * count]
rolled, roll_faces = [], []
for k, c in enumerate(ring):
    tangent = ring[(k + 1) % count] - ring[(k - 1) % count]
    tangent /= np.linalg.norm(tangent)
    outward = np.sin(angles[k]) * np.array([1, 0, 0]) + np.cos(angles[k]) * radial_z
    u = outward - tangent * np.dot(outward, tangent)
    u /= np.linalg.norm(u)
    v = np.cross(tangent, u)
    for a in np.arange(8) * 2 * np.pi / 8:
        rolled.append(c + .024 * (np.cos(a) * u + np.sin(a) * v))
for k in range(count):
    for j in range(8):
        a, b = k * 8 + j, k * 8 + (j + 1) % 8
        c, d = ((k + 1) % count) * 8 + (j + 1) % 8, ((k + 1) % count) * 8 + j
        roll_faces.extend([[a, b, c], [a, c, d]])
rolled, roll_faces = np.array(rolled), np.array(roll_faces)
write_mesh(stage, "/GoldCrown/ContinuousScallopLip", rolled, roll_faces,
           normals(rolled, roll_faces, True), np.array([edge] * len(roll_faces)))

allpoints = np.concatenate([read_mesh(q)[0] for q in stage.Traverse() if q.IsA(UsdGeom.Mesh)])
# The circular band and original tilt remain. Center thickness after the
# replicated points replace the asymmetric rear geometry.
shift = np.array([-(allpoints[:, 0].min() + allpoints[:, 0].max()) / 2,
                  0, -(allpoints[:, 2].min() + allpoints[:, 2].max()) / 2])
for prim in [q for q in stage.Traverse() if q.IsA(UsdGeom.Mesh)]:
    p, f, n, m, uv = read_mesh(prim)
    write_mesh(stage, prim.GetPath(), p + shift, f, n, m, uv)
allpoints += shift
low, high = allpoints.min(0), allpoints.max(0)
assert low[1] >= -2.895 and high[1] <= 3.015 and np.max(np.abs(allpoints[:, 0])) <= 3.35
UsdGeom.SetStageUpAxis(stage, "Y")
UsdGeom.SetStageMetersPerUnit(stage, 1)
path = out / "badge.usdc"
stage.GetRootLayer().Export(str(path))
package = WORK / "mobile/gold_badge_mobile.usdz"
package.parent.mkdir(exist_ok=True)
package.unlink(missing_ok=True)
assert UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(str(path)), str(package))
checker = UsdUtils.ComplianceChecker(arkit=True)
checker.CheckCompliance(str(package))
assert not checker.GetErrors() and not checker.GetFailedChecks(), (checker.GetErrors(), checker.GetFailedChecks())
report = {"equal_points": 8, "angular_spacing_degrees": 45, "peak_axis_height": peak,
          "bounds": [low.tolist(), high.tolist()], "bytes": package.stat().st_size,
          "triangles": sum(len(UsdGeom.Mesh(q).GetFaceVertexCountsAttr().Get()) for q in stage.Traverse() if q.IsA(UsdGeom.Mesh)),
          "arkit_errors": checker.GetErrors(), "arkit_failed_checks": checker.GetFailedChecks()}
(WORK / "geometry.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
scratch.cleanup()
