"""build_gem.py <out_dir> [turn_degrees=22.5] : builds the Diamond's round brilliant gem as an intersection of facet planes and checks it.

Run with Blender's Python (it has pxr and numpy):
  /Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 -I build_gem.py <out_dir> [turn_degrees]

turn_degrees (default 22.5, the installed gem) turns the whole gem about Y before it is written: every plane's azimuth gets
that added, so the file keeps identity transforms. With 22.5 the seam between two bezels (the star facet) faces +Z instead
of a bezel; pass 0 for the unturned gem (a bezel faces +Z).

Writes <out_dir>/diamond_badge_mobile.usdz (one mesh, one material named DiamondGem, flat facets with per-face
normals), <out_dir>/gem_planes.npz (every facet plane and the triangles, for the measuring scripts) and prints every
check; any miss exits with an error.

The gem (Y up, front +Z, 8 fold symmetric, so the back matches the front; with the default turn a star facet faces +Z at rest):
  table (1), 8 bezels at azimuth 45k, 8 stars at 22.5 + 45k, 16 upper girdle facets at 11.25 + 22.5k,
  32 vertical girdle facets at 11.25k, 8 pavilion mains at 45k, 16 lower girdle facets at 11.25 + 22.5k = 89 facets.
Azimuth 0 is +Z and grows toward +X. Each plane is "normal . x = offset", with the normal pointing out of the gem.
"""
import itertools
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

# ---- Dimensions, in the app's scene units (the size of Codex's round gem, so the framing does not change) ----
GIRDLE_APOTHEM = 3.12        # distance from the axis to a vertical girdle facet: the gem is 6.24 wide on the axes
GIRDLE_TOP_Y = 0.88          # where the crown meets the girdle wall
GIRDLE_BOTTOM_Y = 0.78       # where the pavilion meets the girdle wall
TABLE_Y = 2.349
TABLE_CIRCUMRADIUS = 1.40    # the table is an octagon; its corners sit under the bezel facets (Codex's round table: 1.38)
CULET_Y = -2.455
# ---- Facet shape choices ----
STAR_TIP_Y = 1.60            # how low the star facets reach: about half way down the crown
LOWER_GIRDLE_EXTRA_DEGREES = 3.0   # the lower girdle facets are this much steeper than the pavilion mains
EXPECTED_FACET_COUNT = 89
PLANE_TOLERANCE = 1e-4

TURN_DEGREES = 22.5          # the whole gem turned about Y, baked into the planes (command line can override)
TABLE_APOTHEM = TABLE_CIRCUMRADIUS * math.cos(math.radians(22.5))
HALF_STEP = math.radians(22.5)


def make_plane(azimuth_degrees, normal_elevation_degrees, through_distance, through_y):
    """The plane whose normal points at `azimuth` and `normal_elevation` above the horizon, through the profile point
    (distance from the axis along that azimuth, height)."""
    azimuth = math.radians(azimuth_degrees + TURN_DEGREES)
    elevation = math.radians(normal_elevation_degrees)
    normal = np.array([math.cos(elevation) * math.sin(azimuth), math.sin(elevation), math.cos(elevation) * math.cos(azimuth)])
    offset = math.cos(elevation) * through_distance + math.sin(elevation) * through_y
    return normal, offset


def elevation_through(profile_a, profile_b):
    """Normal elevation (degrees) of the profile line through two (distance, height) points, with the normal pointing
    away from the axis."""
    (distance_a, y_a), (distance_b, y_b) = profile_a, profile_b
    slope_y, slope_distance = y_b - y_a, distance_b - distance_a
    # The line direction is (slope_distance, slope_y); its outward normal is (slope_y, -slope_distance) up to sign.
    normal_distance, normal_y = slope_y, -slope_distance
    if normal_distance < 0:
        normal_distance, normal_y = -normal_distance, -normal_y
    return math.degrees(math.atan2(normal_y, normal_distance))


def facet_planes():
    """Returns [(family, normal, offset), ...] for all 89 facets."""
    planes = [('table', np.array([0.0, 1.0, 0.0]), TABLE_Y)]

    # Bezels: through the table corner and the girdle wall's top edge.
    bezel_elevation = elevation_through((TABLE_CIRCUMRADIUS, TABLE_Y), (GIRDLE_APOTHEM, GIRDLE_TOP_Y))
    for k in range(8):
        planes.append(('bezel', *make_plane(45 * k, bezel_elevation, GIRDLE_APOTHEM, GIRDLE_TOP_Y)))

    # The star tip is a point on the ridge where two neighbouring bezels meet (azimuth 22.5), at STAR_TIP_Y.
    bezel_distance_at_tip = TABLE_CIRCUMRADIUS + (GIRDLE_APOTHEM - TABLE_CIRCUMRADIUS) * (TABLE_Y - STAR_TIP_Y) / (TABLE_Y - GIRDLE_TOP_Y)
    tip_radius = bezel_distance_at_tip / math.cos(HALF_STEP)
    star_elevation = elevation_through((TABLE_APOTHEM, TABLE_Y), (tip_radius, STAR_TIP_Y))
    for k in range(8):
        planes.append(('star', *make_plane(22.5 + 45 * k, star_elevation, TABLE_APOTHEM, TABLE_Y)))

    # Upper girdle facets: through the star tip and the girdle wall's top edge, so five planes meet at each star tip.
    tip_distance_on_upper = tip_radius * math.cos(math.radians(11.25))
    upper_elevation = elevation_through((GIRDLE_APOTHEM, GIRDLE_TOP_Y), (tip_distance_on_upper, STAR_TIP_Y))
    for k in range(16):
        planes.append(('upper', *make_plane(11.25 + 22.5 * k, upper_elevation, GIRDLE_APOTHEM, GIRDLE_TOP_Y)))

    for m in range(32):
        planes.append(('wall', *make_plane(11.25 * m, 0.0, GIRDLE_APOTHEM, 0.0)))

    # Pavilion mains meet at the culet: the line from the girdle wall's bottom edge to the culet.
    main_elevation = elevation_through((GIRDLE_APOTHEM, GIRDLE_BOTTOM_Y), (0.0, CULET_Y))
    for k in range(8):
        planes.append(('main', *make_plane(45 * k, main_elevation, GIRDLE_APOTHEM, GIRDLE_BOTTOM_Y)))

    # Lower girdle facets: a little steeper than the mains.
    main_angle_from_horizontal = 90 + main_elevation  # main_elevation is negative
    lower_elevation = -(90 - (main_angle_from_horizontal + LOWER_GIRDLE_EXTRA_DEGREES))
    for k in range(16):
        planes.append(('lower', *make_plane(11.25 + 22.5 * k, lower_elevation, GIRDLE_APOTHEM, GIRDLE_BOTTOM_Y)))
    return planes


def intersect_planes(planes):
    """Vertices of the convex gem: every triple intersection that lies inside all planes, merged within 1e-5."""
    normals = np.array([p[1] for p in planes])
    offsets = np.array([p[2] for p in planes])
    found = []
    for i, j, k in itertools.combinations(range(len(planes)), 3):
        matrix = normals[[i, j, k]]
        if abs(np.linalg.det(matrix)) < 1e-9:
            continue
        point = np.linalg.solve(matrix, offsets[[i, j, k]])
        if np.all(normals @ point - offsets < 1e-6):
            found.append(point)
    merged = []
    for point in found:
        if not any(np.linalg.norm(point - other) < 1e-5 for other in merged):
            merged.append(point)
    return np.array(merged)


def facet_polygons(planes, vertices):
    """Per plane, the indices of its vertices sorted counter clockwise as seen from outside."""
    polygons = []
    for family, normal, offset in planes:
        on_plane = np.where(np.abs(vertices @ normal - offset) < 1e-5)[0]
        if len(on_plane) < 3:
            polygons.append(None)
            continue
        points = vertices[on_plane]
        center = points.mean(axis=0)
        axis_a = np.cross(normal, [0.0, 1.0, 0.0]) if abs(normal[1]) < 0.99 else np.array([1.0, 0.0, 0.0])
        axis_a /= np.linalg.norm(axis_a)
        axis_b = np.cross(normal, axis_a)
        angles = np.arctan2((points - center) @ axis_b, (points - center) @ axis_a)
        order = on_plane[np.argsort(angles)]
        # Counter clockwise about the outward normal = right hand rule gives the outward normal.
        first, second, third = vertices[order[0]], vertices[order[1]], vertices[order[2]]
        if np.dot(np.cross(second - first, third - first), normal) < 0:
            order = order[::-1]
        polygons.append(order)
    return polygons


def triangulate(polygons):
    """Fan triangulation of every polygon: list of (plane index, a, b, c) over merged vertex ids."""
    triangles = []
    for plane_index, polygon in enumerate(polygons):
        for position in range(1, len(polygon) - 1):
            triangles.append((plane_index, polygon[0], polygon[position], polygon[position + 1]))
    return triangles


def check(condition, message):
    print(('PASS  ' if condition else 'FAIL  ') + message)
    if not condition:
        raise SystemExit(f'check failed: {message}')


def run_checks(planes, vertices, polygons, triangles):
    normals = np.array([p[1] for p in planes])
    offsets = np.array([p[2] for p in planes])
    facet_count = sum(polygon is not None for polygon in polygons)
    check(facet_count == EXPECTED_FACET_COUNT == len(planes), f'facet count {facet_count} (every one of {len(planes)} planes is a facet)')
    edge_use = {}
    for _, a, b, c in triangles:
        for edge in ((a, b), (b, c), (c, a)):
            key = tuple(sorted(edge))
            edge_use[key] = edge_use.get(key, 0) + 1
    # Fan diagonals inside a facet are shared by its two triangles, polygon edges by the neighbouring facet's triangle.
    check(all(count == 2 for count in edge_use.values()), f'closed: all {len(edge_use)} edges shared by exactly two triangles')
    outside = (vertices @ normals.T - offsets).max()
    check(outside < PLANE_TOLERANCE, f'convex: no vertex more than {outside:.2e} outside any facet plane (limit {PLANE_TOLERANCE})')
    worst_planarity = max(np.abs(vertices[polygon] @ normals[i] - offsets[i]).max() for i, polygon in enumerate(polygons))
    check(worst_planarity < 1e-6, f'every facet planar (worst {worst_planarity:.2e})')
    low, high = vertices.min(axis=0), vertices.max(axis=0)
    check(abs(low[0]) <= 3.13 and high[0] <= 3.13 and abs(low[2]) <= 3.13 and high[2] <= 3.13, f'bounds x {low[0]:.4f}..{high[0]:.4f}, z {low[2]:.4f}..{high[2]:.4f} within +-3.13')
    check(abs(low[1] - CULET_Y) <= 0.005 and abs(high[1] - TABLE_Y) <= 0.005, f'y from {low[1]:.4f} to {high[1]:.4f} (culet {CULET_Y}, table {TABLE_Y}, +-0.005)')
    # Winding: every triangle's cross product points along its plane's outward normal.
    for plane_index, a, b, c in triangles:
        cross = np.cross(vertices[b] - vertices[a], vertices[c] - vertices[a])
        assert np.dot(cross, normals[plane_index]) > 0, 'a triangle is wound inward'
    print(f'PASS  winding: all {len(triangles)} triangles face outward')


def write_usd(out_dir, planes, vertices, triangles):
    from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade, UsdUtils, Vt

    usdc_path = out_dir / 'badge.usdc'
    usdz_path = out_dir / 'diamond_badge_mobile.usdz'
    stage = Usd.Stage.CreateNew(str(usdc_path))
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    root = UsdGeom.Xform.Define(stage, '/DiamondGem')
    stage.SetDefaultPrim(root.GetPrim())

    material = UsdShade.Material.Define(stage, '/DiamondGem/Materials/DiamondGem')
    surface = UsdShade.Shader.Define(stage, '/DiamondGem/Materials/DiamondGem/Surface')
    surface.CreateIdAttr('UsdPreviewSurface')
    surface.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0.06, 0.24, 0.53))
    surface.CreateInput('metallic', Sdf.ValueTypeNames.Float).Set(0.6)
    surface.CreateInput('roughness', Sdf.ValueTypeNames.Float).Set(0.25)
    material.CreateSurfaceOutput().ConnectToSource(surface.ConnectableAPI(), 'surface')

    points, indices, normals = [], [], []
    for plane_index, a, b, c in triangles:
        for corner in (a, b, c):
            indices.append(len(points))
            points.append(Gf.Vec3f(*[float(x) for x in vertices[corner]]))
            normals.append(Gf.Vec3f(*[float(x) for x in planes[plane_index][1]]))
    mesh = UsdGeom.Mesh.Define(stage, '/DiamondGem/DiamondGem_Facets')
    mesh.CreatePointsAttr(Vt.Vec3fArray(points))
    mesh.CreateFaceVertexCountsAttr(Vt.IntArray([3] * len(triangles)))
    mesh.CreateFaceVertexIndicesAttr(Vt.IntArray(indices))
    mesh.CreateNormalsAttr(Vt.Vec3fArray(normals))
    mesh.SetNormalsInterpolation(UsdGeom.Tokens.vertex)
    mesh.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)
    mesh.CreateDoubleSidedAttr(False)
    low, high = vertices.min(axis=0), vertices.max(axis=0)
    mesh.CreateExtentAttr(Vt.Vec3fArray([Gf.Vec3f(*[float(x) for x in low]), Gf.Vec3f(*[float(x) for x in high])]))
    UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(material)
    stage.GetRootLayer().Save()
    # The zip stores the file's modification time, so it is pinned (to when the installed gem was packaged): a plain
    # re-run then writes a byte for byte identical file.
    pinned_time = time.mktime((2026, 10, 11, 8, 49, 14, 0, 0, -1))
    os.utime(usdc_path, (pinned_time, pinned_time))

    if usdz_path.exists():
        usdz_path.unlink()
    ok = UsdUtils.CreateNewARKitUsdzPackage(Sdf.AssetPath(str(usdc_path)), str(usdz_path))
    check(bool(ok) and usdz_path.exists(), f'packaged {usdz_path} ({usdz_path.stat().st_size} bytes)')
    result = subprocess.run(['/usr/bin/usdchecker', '--arkit', str(usdz_path)], capture_output=True, text=True)
    print(result.stdout.strip()[-400:], result.stderr.strip()[-400:])
    check(result.returncode == 0, 'usdchecker --arkit passes')
    return usdz_path


def main():
    global TURN_DEGREES
    out_dir = Path(sys.argv[1])
    if len(sys.argv) > 2:
        TURN_DEGREES = float(sys.argv[2])
    print(f'gem turned {TURN_DEGREES} degrees about Y')
    out_dir.mkdir(parents=True, exist_ok=True)
    planes = facet_planes()
    vertices = intersect_planes(planes)
    polygons = facet_polygons(planes, vertices)
    check(all(polygon is not None for polygon in polygons), 'every plane has at least 3 vertices')
    triangles = triangulate(polygons)
    print(f'{len(vertices)} vertices, {len(triangles)} triangles, {len(planes)} planes')
    run_checks(planes, vertices, polygons, triangles)
    np.savez(out_dir / 'gem_planes.npz',
             normals=np.array([p[1] for p in planes]), offsets=np.array([p[2] for p in planes]),
             families=np.array([p[0] for p in planes]),
             ALLP=np.array([[vertices[a], vertices[b], vertices[c]] for _, a, b, c in triangles]))
    write_usd(out_dir, planes, vertices, triangles)


if __name__ == '__main__':
    main()
