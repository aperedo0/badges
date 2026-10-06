"""Mobile export rules for RealityKit badge exports (v3: v2 rules plus the floor cut).

Applies the export rules from EXPORT_RULES.md to a reduced mobile badge scene (the
scene export_mobile.py saves before it writes USD), then exports the USDZ with
exactly the v1 exporter settings and post-processing.

Headless use (never run it on an original file; it only reads the input .blend):
  Blender --background --factory-startup --python badge_mobile_rules.py -- \
      --input  <reduced mobile .blend> \
      --output <folder>/silver_badge_mobile.usdz \
      [--save-blend <folder>/silver_badge_mobile_v2.blend] [--report <file>.json] \
      [--inset-strength 0.4] [--skip-v2-rules] [--no-rules]

  --skip-v2-rules  the input already carries rules 1 to 4 (for example v2's saved
                   scenes/silver_badge_mobile.blend); only the floor cut runs.
  --no-rules       no rule at all: a plain re-export, for baseline checks.

The rules, in short:
  1. Bevel strips on faceted polished meshes take the shading normal of the
     broad facet they belong to (continuing that facet's own normals), never
     rounded normals of their own.
  2. Those strips use exactly the material of that facet.
  3. Polished metal (the emblem and the casing/ring) exports without baked
     normal maps; facet detail lives in geometry and custom normals.
  4. A normal map that stays is baked at the strength Blender renders it at,
     because UsdPreviewSurface has no normal-strength input.
  5. Floor cut: every mesh is cut at the stage floor and the part below it is
     removed, without a cap. Kept faces keep their exact data; new corners on
     cut edges interpolate normals and UVs along the edge.
"""
import json
import math
import struct
import sys
import zlib
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.geometry import closest_point_on_tri
from pxr import Sdf, Tf, Usd, UsdGeom, UsdUtils

# The USD export writes Blender world coordinates unchanged (convert_orientation=False)
# and only labels the stage Y up. The badge scenes are authored Y up, so USD +Y is
# Blender world +Y. Both the exporter call and the floor cut read this one constant.
CONVERT_ORIENTATION = False

# Per-badge settings. Mesh keys are the short object names, the text before ' | '.
SILVER_CONFIG = dict(
    # Rule 3: meshes whose materials lose their baked normal maps.
    no_normal_map_meshes=['Emblem', 'Casing'],
    # Rules 1 and 2: meshes whose thin bevel strips fold into their facets. The
    # strips are the faces the master's Bevel modifier gave its bevel material;
    # the geometric width check only cross-checks that selection.
    bevel_meshes={'Emblem': dict(bevel_material_prefix='Silver | polished cut edges', max_strip_width=0.02)},
    # Rule 4: normal maps that stay, and the strength to bake into their pixels.
    # The inset bake already matches Blender (Cycles renders it at the master's
    # grain), but RealityKit shows that fine grain about 2.5x stronger than
    # Blender's final render (app 2.48 / 2.91 vs Blender 1.15 / 0.93 luma levels,
    # left / right patch). 0.4 brings the app back to Blender's look; use 1.0 for
    # a Blender-exact file. See proof/NUMBERS.md.
    normal_map_strength={'Inset': 0.4},
    # Broad triangles within this angle of each other and sharing a vertex form one facet.
    facet_merge_degrees=1.0,
    # Rule 5: the stage floor in the exported (USD, Y up) model space, with the badge
    # at its final resting pose. The Blender stage floor sits at Y = -2.8950002 (one
    # float32 step below -2.895); the app cuts at -2.895, so the file does too.
    floor_cut=dict(usd_up_height=-2.895),
    # Sibling order of the exported prims. Blender's USD exporter orders them
    # differently on every run, so the order is fixed after export: here the
    # shipped v1 file's order; names not listed follow alphabetically.
    prim_order={
        '/Badge': ['Inset___charcoal_textured_disk', '_materials', 'Inner_edge___fine_silver_reveal',
                   'Casing___smooth_rounded_outer_edge', 'Emblem___faceted_compass_spear',
                   'Inner_channel___shadowed_bevel', 'Rim_inner_lip___narrow_highlight'],
        '/Badge/_materials': ['Inset___finely_textured_charcoal_Mobile_Inset',
                              'Silver___polished_cut_edges_Mobile_Inner_edge',
                              'Silver___circumferential_brushed_steel_Mobile_Casing',
                              'Outer_edge___smooth_satin_silver_Mobile_Casing',
                              'Back_and_edge___gunmetal_Mobile_Casing',
                              'Emblem___satin_silver_facets_Mobile_Emblem',
                              'Emblem___shaded_outer_facets_Mobile_Emblem',
                              'Recess___smoked_nickel_Mobile_Inner_channel',
                              'Silver___polished_cut_edges_Mobile_Rim_inner_lip'],
    },
)


def short_name(obj):
    return obj.name.split(' | ')[0]


# ---------------------------------------------------------------- rules 1 and 2

def use_free_normals(mesh):
    """Stores the mesh's current corner normals as a float3 'custom_normal' attribute.

    Blender's default custom normals are 16-bit encoded, so writing them back
    through normals_split_custom_set would nudge every corner slightly. With the
    float attribute the untouched corners keep their exact values.
    """
    normals = np.empty(len(mesh.loops) * 3, dtype=np.float32)
    mesh.corner_normals.foreach_get('vector', normals)
    if 'custom_normal' in mesh.attributes:
        mesh.attributes.remove(mesh.attributes['custom_normal'])
    attr = mesh.attributes.new('custom_normal', 'FLOAT_VECTOR', 'CORNER')
    attr.data.foreach_set('vector', normals)
    mesh.update()
    check = np.empty_like(normals)
    mesh.corner_normals.foreach_get('vector', check)
    assert mesh.normals_domain == 'CORNER', mesh.normals_domain
    assert np.array_equal(check, normals), 'free normals did not round-trip exactly'
    return normals.reshape(-1, 3)


def strip_width(mesh, poly):
    """Smallest altitude of a triangle (or of a polygon's triangles): how thin the face is."""
    pts = [mesh.vertices[v].co for v in poly.vertices]
    if len(pts) != 3:
        return min(strip_width_tri(pts[0], pts[i], pts[i + 1]) for i in range(1, len(pts) - 1))
    return strip_width_tri(*pts)


def strip_width_tri(a, b, c):
    area2 = (b - a).cross(c - a).length
    longest = max((b - a).length, (c - b).length, (a - c).length)
    return area2 / longest if longest > 0 else 0.0


def fold_bevels_into_facets(obj, settings, merge_degrees):
    mesh = obj.data
    mesh.calc_loop_triangles()
    mats = list(mesh.materials)
    prefix = settings['bevel_material_prefix']
    bevel_slots = {i for i, m in enumerate(mats) if m and m.name.startswith(prefix)}
    assert bevel_slots, f'{obj.name}: no material starting with {prefix!r}'
    bevel = [p.index for p in mesh.polygons if p.material_index in bevel_slots]
    broad = [p.index for p in mesh.polygons if p.material_index not in bevel_slots]
    widths = {i: strip_width(mesh, mesh.polygons[i]) for i in bevel}
    too_wide = [i for i, w in widths.items() if w > settings['max_strip_width']]
    assert not too_wide, (f'{obj.name}: faces {too_wide[:10]} use the bevel material but are wider than '
                          f'max_strip_width; a bevel that wide is visible geometry, so raise max_strip_width '
                          f'only if it should still be folded into its facets')

    normals = use_free_normals(mesh)
    before = normals.copy()

    # Broad triangles, grouped into planar facets.
    tris = [t for t in mesh.loop_triangles if t.polygon_index in set(broad)]
    face_n = {t.index: Vector(t.normal) for t in tris}
    parent = {t.index: t.index for t in tris}

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    cos_limit = math.cos(math.radians(merge_degrees))
    for i, a in enumerate(tris):
        for b in tris[i + 1:]:
            if set(a.vertices) & set(b.vertices) and face_n[a.index].dot(face_n[b.index]) > cos_limit:
                parent[find(a.index)] = find(b.index)
    facets = {}
    for t in tris:
        facets.setdefault(find(t.index), []).append(t)

    def tri_points(t):
        return [mesh.vertices[v].co for v in t.vertices]

    def closest_on(tri_list, p):
        best = None
        for t in tri_list:
            a, b, c = tri_points(t)
            q = closest_point_on_tri(p, a, b, c)
            d = (q - p).length
            if best is None or d < best[0]:
                best = (d, t, q)
        return best

    def interpolated_normal(t, q):
        a, b, c = tri_points(t)
        v0, v1, v2 = b - a, c - a, q - a
        d00, d01, d11 = v0.dot(v0), v0.dot(v1), v1.dot(v1)
        d20, d21 = v2.dot(v0), v2.dot(v1)
        den = d00 * d11 - d01 * d01
        w1 = (d11 * d20 - d01 * d21) / den
        w2 = (d00 * d21 - d01 * d20) / den
        w0 = 1 - w1 - w2
        n = w0 * normals[t.loops[0]] + w1 * normals[t.loops[1]] + w2 * normals[t.loops[2]]
        return n / np.linalg.norm(n)

    group_of = {t.index: key for key, members in facets.items() for t in members}
    new_material = {}
    stats = []
    for pi in bevel:
        poly = mesh.polygons[pi]
        centre = Vector(poly.center)
        _, nearest, _ = closest_on(tris, centre)
        facet = facets[group_of[nearest.index]]
        new_material[pi] = mesh.polygons[nearest.polygon_index].material_index
        facet_normal = face_n[nearest.index]
        for li in poly.loop_indices:
            p = mesh.vertices[mesh.loops[li].vertex_index].co
            _, t, q = closest_on(facet, p)
            n = interpolated_normal(t, q)
            old = before[li] / np.linalg.norm(before[li])
            stats.append(dict(
                old_vs_facet=math.degrees(math.acos(max(-1, min(1, float(np.dot(old, facet_normal)))))),
                new_vs_facet=math.degrees(math.acos(max(-1, min(1, float(np.dot(n, facet_normal))))))))
            normals[li] = n

    mesh.attributes['custom_normal'].data.foreach_set('vector', normals.astype(np.float32).ravel())
    for pi, mi in new_material.items():
        mesh.polygons[pi].material_index = mi
    mesh.update()

    # Drop the now unused bevel material slot(s), keeping every face on its material.
    used = sorted({p.material_index for p in mesh.polygons})
    keep = [mats[i] for i in used]
    remap = {old: new for new, old in enumerate(used)}
    indices = [remap[p.material_index] for p in mesh.polygons]
    mesh.materials.clear()
    for m in keep:
        mesh.materials.append(m)
    mesh.polygons.foreach_set('material_index', indices)
    mesh.update()

    after = np.empty(len(mesh.loops) * 3, dtype=np.float32)
    mesh.corner_normals.foreach_get('vector', after)
    after = after.reshape(-1, 3)
    broad_loops = [li for pi in broad for li in mesh.polygons[pi].loop_indices]
    old_vs = np.array([s['old_vs_facet'] for s in stats])
    new_vs = np.array([s['new_vs_facet'] for s in stats])
    return dict(
        mesh=obj.name, bevel_faces=len(bevel), broad_faces=len(broad), facets=len(facets),
        max_bevel_strip_width=max(widths.values()),
        min_broad_face_width=min(strip_width(mesh, mesh.polygons[i]) for i in broad),
        bevel_material_removed=[mats[i].name for i in sorted(bevel_slots)],
        bevel_faces_per_material={m.name: sum(1 for pi in bevel if keep[remap[new_material[pi]]] is m) for m in keep},
        bevel_corner_normal_vs_owner_facet_degrees_before=dict(
            median=float(np.median(old_vs)), p95=float(np.percentile(old_vs, 95)), max=float(old_vs.max())),
        bevel_corner_normal_vs_owner_facet_degrees_after=dict(
            median=float(np.median(new_vs)), p95=float(np.percentile(new_vs, 95)), max=float(new_vs.max())),
        broad_facet_corner_normals_max_change=float(np.abs(after[broad_loops] - before[broad_loops]).max()),
        materials_after=[m.name for m in keep])


# ---------------------------------------------------------------- rule 5

def usd_up_axis_in_blender():
    """The Blender world axis that becomes USD +Y in the exported file."""
    return Vector((0.0, 0.0, 1.0)) if CONVERT_ORIENTATION else Vector((0.0, 1.0, 0.0))


def cut_at_floor(obj, usd_height, eps=1e-6):
    """Bisects the mesh at the floor and deletes everything below it, with no cap.

    Faces entirely above the floor are not touched. bmesh's bisect interpolates each
    face's corner data (UVs and the float custom normals) along every cut edge; the
    new corners' normals are then renormalized. Cut faces that become quads are split
    into triangles, keeping the mesh all triangles as the v1 pipeline left it.
    """
    mesh = obj.data
    up_world = usd_up_axis_in_blender()
    world = np.array(obj.matrix_world)
    co = np.empty(len(mesh.vertices) * 3)
    mesh.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    heights = (co @ world[:3, :3].T + world[:3, 3]) @ np.array(up_world)
    mesh.calc_loop_triangles()
    info = dict(mesh=obj.name, blender_world_axis=list(up_world), blender_height=usd_height,
                min_height_before=float(heights.min()), triangles_before=len(mesh.loop_triangles))
    if heights.min() >= usd_height - eps:
        info.update(cut=False, min_height_after=info['min_height_before'], triangles_after=info['triangles_before'])
        return info

    use_free_normals(mesh)  # exact float corner normals, so kept corners cannot drift
    inverse = obj.matrix_world.inverted()
    plane_co = inverse @ (up_world * usd_height)
    plane_no = (obj.matrix_world.to_3x3().transposed() @ up_world).normalized()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    normal_layer = bm.loops.layers.float_vector.get('custom_normal')
    assert normal_layer is not None, 'free normals missing'
    original = {tuple(v.co) for v in bm.verts}
    result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=eps,
                                    plane_co=plane_co, plane_no=plane_no, clear_inner=True)
    new_verts = [v for v in bm.verts if tuple(v.co) not in original]
    cut_edges = sum(1 for e in result['geom_cut'] if isinstance(e, bmesh.types.BMEdge))
    for vert in new_verts:
        for loop in vert.link_loops:
            loop[normal_layer] = loop[normal_layer].normalized()
    polygons = [f for f in bm.faces if len(f.verts) > 3]
    bmesh.ops.triangulate(bm, faces=polygons, quad_method='BEAUTY', ngon_method='BEAUTY')
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    co = np.empty(len(mesh.vertices) * 3)
    mesh.vertices.foreach_get('co', co)
    heights = (co.reshape(-1, 3) @ world[:3, :3].T + world[:3, 3]) @ np.array(up_world)
    mesh.calc_loop_triangles()
    assert mesh.normals_domain == 'CORNER'
    info.update(cut=True, new_vertices=len(new_verts), open_boundary_edges_on_floor=cut_edges,
                faces_split_into_polygons=len(polygons), triangles_after=len(mesh.loop_triangles),
                min_height_after=float(heights.min()), max_height_after=float(heights.max()))
    return info


# ---------------------------------------------------------------- rules 3 and 4

def normal_map_chain(mat):
    """The Principled BSDF and the Normal Map node feeding its Normal input, if any."""
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    links = bsdf.inputs['Normal'].links
    if not links or links[0].from_node.type != 'NORMAL_MAP':
        return bsdf, None
    return bsdf, links[0].from_node


def upstream(node):
    found = []
    for socket in node.inputs:
        for link in socket.links:
            found.append(link.from_node)
            found.extend(upstream(link.from_node))
    return found


def remove_normal_map(mat):
    bsdf, nmap = normal_map_chain(mat)
    if nmap is None:
        return None
    image = next((n.image.name for n in upstream(nmap) if n.type == 'TEX_IMAGE' and n.image), None)
    tree = mat.node_tree
    for link in list(bsdf.inputs['Normal'].links):
        tree.links.remove(link)
    for node in [nmap] + upstream(nmap):
        if all(not out.links for out in node.outputs) or node is nmap:
            if node.name in tree.nodes:
                tree.nodes.remove(node)
    # UV Map nodes feeding only the removed texture are gone with it; sweep leftovers.
    for node in list(tree.nodes):
        if node.type in ('UVMAP', 'TEX_IMAGE') and all(not out.links for out in node.outputs):
            tree.nodes.remove(node)
    return image


def with_strength(pixels, strength):
    """Blender's Normal Map Strength baked into tangent-space pixels (RGB 0..1).

    Blender mixes toward the unperturbed normal and renormalizes:
    n' = normalize((0, 0, 1) + strength * (n - (0, 0, 1))).
    """
    n = pixels * 2.0 - 1.0
    flat = np.array([0.0, 0.0, 1.0])
    n = flat + strength * (n - flat)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return (n + 1.0) * 0.5


# ---------------------------------------------------------------- textures and export

def png_bytes(rgb8):
    """8-bit RGB PNG, rows top to bottom."""
    h, w, _ = rgb8.shape
    raw = b''.join(b'\x00' + rgb8[y].tobytes() for y in range(h))

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


def image_rgb(img):
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    return px.reshape(h, w, 4)[::-1, :, :3]  # Blender rows run bottom to top


def write_textures(materials, textures_dir, strengths):
    """Writes every image the export still uses into textures_dir and points the images there.

    Untouched images are written from their packed bytes, byte for byte. A normal
    map with a strength other than 1 is re-encoded with that strength baked in.
    """
    textures_dir.mkdir(parents=True, exist_ok=True)
    written = {}
    for mat in materials:
        for node in mat.node_tree.nodes:
            if node.type != 'TEX_IMAGE' or not node.image or node.image.name in written:
                continue
            img = node.image
            target = textures_dir / img.name
            strength = strengths.get(img.name, 1.0)
            if strength != 1.0:
                rgb = with_strength(image_rgb(img).astype(np.float64), strength)
                target.write_bytes(png_bytes(np.clip(np.rint(rgb * 255), 0, 255).astype(np.uint8)))
            elif img.packed_file:
                target.write_bytes(img.packed_file.data)
            else:
                target.write_bytes(Path(bpy.path.abspath(img.filepath)).read_bytes())
            # Repoint first, then refresh the packed copy from the new file, so nothing is ever
            # written to the old path. Packed images export as ./textures/<name>, exactly as in v1.
            img.filepath_raw = str(target)
            img.filepath = str(target)
            if img.packed_file:
                img.unpack(method='REMOVE')
                img.filepath = str(target)
            img.reload()
            img.pack()
            assert img.packed_file.data == target.read_bytes(), img.name
            written[img.name] = dict(file=str(target), strength_baked=strength,
                                     width=img.size[0], height=img.size[1])
    return written


def fix_prim_order(layer, prim_order):
    """Reorders sibling prims: listed names first, in list order, the rest alphabetically.

    Sdf has no in-place reorder here, so each child moves to a holding prim and back;
    a move appends at the end, so moving back in the wanted order sets the order.
    Paths end up exactly where they were, so bindings and connections stay valid.
    """
    for parent, wanted in prim_order.items():
        spec = layer.GetPrimAtPath(parent)
        if spec is None:
            continue
        present = [child.name for child in spec.nameChildren]
        order = [n for n in wanted if n in present] + sorted(n for n in present if n not in wanted)
        if order == present:
            continue
        hold = Sdf.Path('/__reorder__')
        Sdf.CreatePrimInLayer(layer, hold)
        for step in ((parent, hold), (hold, parent)):
            edit = Sdf.BatchNamespaceEdit()
            for name in order:
                edit.Add(Sdf.NamespaceEdit.ReparentAndRename(
                    Sdf.Path(step[0]).AppendChild(name), Sdf.Path(step[1]), name, -1))
            assert layer.Apply(edit), (parent, step)
        del layer.rootPrims[hold.name]
        assert [child.name for child in layer.GetPrimAtPath(parent).nameChildren] == order, parent


def export_usdz(objects, out_usdz, prim_order=None):
    """The v1 exporter call and post-processing, plus a fixed sibling order."""
    usdc = out_usdz.with_suffix('.usdc')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.wm.usd_export(filepath=str(usdc), check_existing=False, selected_objects_only=True,
        export_animation=False, export_materials=True, export_normals=True, export_uvmaps=True, rename_uvmaps=False,
        generate_preview_surface=True, generate_materialx_network=False, export_textures_mode='KEEP',
        relative_paths=True, export_lights=False, export_cameras=False, export_volumes=False,
        export_curves=False, export_points=False, export_armatures=False, export_shapekeys=False,
        convert_world_material=False, convert_orientation=CONVERT_ORIENTATION, root_prim_path='/Badge',
        export_custom_properties=True, author_blender_name=True, triangulate_meshes=True, evaluation_mode='RENDER')
    stage = Usd.Stage.Open(str(usdc))
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    stage.SetDefaultPrim(stage.GetPrimAtPath('/Badge'))
    names = {Tf.MakeValidIdentifier(o.name): o.name for o in objects}
    meshes = [p for p in stage.Traverse() if p.IsA(UsdGeom.Mesh)]
    assert len(meshes) == len(objects), (len(meshes), len(objects))
    for prim in meshes:
        name = names[prim.GetParent().GetName()]
        prim.SetDisplayName(name)
        prim.GetParent().SetDisplayName(name)
        prim.SetCustomDataByKey('sourceObjectName', name)
    # Restore frozen enclosure specifications to preserve even indexed UV representation.
    silver = Usd.Stage.Open('/Users/antonioperedo/Downloads/badge_realitykit_iron/source/silver_v3/silver_badge_mobile.usdz')
    for source in silver.GetPrimAtPath('/Badge').GetChildren():
        if source.GetName() in ('_materials', 'Emblem___faceted_compass_spear'):
            continue
        assert Sdf.CopySpec(silver.GetRootLayer(), source.GetPath(), stage.GetRootLayer(), source.GetPath())
    fix_prim_order(stage.GetRootLayer(), prim_order or {'/Badge': [], '/Badge/_materials': []})
    stage.GetRootLayer().Save()
    assert UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(str(usdc)), str(out_usdz))
    return usdc


def run(input_blend, out_usdz, textures_dir, apply=True, config=SILVER_CONFIG, save_blend=None,
        convert_free_normals=False, floor_cut=True):
    if input_blend:
        bpy.ops.wm.open_mainfile(filepath=str(input_blend))
    bpy.context.preferences.filepaths.save_version = 0
    out_usdz, textures_dir = Path(out_usdz), Path(textures_dir)
    out_usdz.parent.mkdir(parents=True, exist_ok=True)
    objects = sorted((o for o in bpy.context.scene.objects if o.type == 'MESH'), key=lambda o: o.name)
    scene = bpy.context.scene
    done = list(scene.get('mobile_rules_applied', []))
    assert not (apply and 'rules 1-4' in done), 'rules 1-4 are already applied to this scene; use --skip-v2-rules'
    report = dict(input_blend=bpy.data.filepath, rules_applied=apply, floor_cut_applied=floor_cut,
                  meshes={}, materials={})
    strengths = {}
    if convert_free_normals:
        for obj in objects:
            use_free_normals(obj.data)
    if apply:
        for obj in objects:
            short = short_name(obj)
            if short in config['bevel_meshes']:
                report['meshes'][obj.name] = fold_bevels_into_facets(
                    obj, config['bevel_meshes'][short], config['facet_merge_degrees'])
            for mat in obj.data.materials:
                entry = report['materials'].setdefault(mat.name, dict(meshes=[]))
                entry['meshes'].append(obj.name)
                if short in config['no_normal_map_meshes']:
                    removed = remove_normal_map(mat)
                    if removed:
                        entry['normal_map_removed'] = removed
                elif short in config['normal_map_strength']:
                    _, nmap = normal_map_chain(mat)
                    if nmap is not None:
                        image = next(n.image.name for n in upstream(nmap) if n.type == 'TEX_IMAGE')
                        strength = nmap.inputs['Strength'].default_value * config['normal_map_strength'][short]
                        strengths[image] = strength
                        nmap.inputs['Strength'].default_value = 1.0  # now baked into the pixels
                        entry['normal_map_strength_baked'] = dict(image=image, strength=strength)
    if apply:
        done.append('rules 1-4')
    if floor_cut:
        report['floor_cut'] = {obj.name: cut_at_floor(obj, config['floor_cut']['usd_up_height'])
                               for obj in objects}
        done.append('floor cut')
    scene['mobile_rules_applied'] = done
    used = [m for o in objects for m in o.data.materials if m]
    report['textures'] = write_textures(list(dict.fromkeys(used)), textures_dir, strengths)
    if save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=str(save_blend), check_existing=False)
    usdc = export_usdz(objects, out_usdz, config.get('prim_order'))
    report.update(file=str(out_usdz), file_bytes=out_usdz.stat().st_size, usdc=str(usdc))
    return report


if __name__ == '__main__' and '--input' in sys.argv:
    args = sys.argv[sys.argv.index('--') + 1:]

    def opt(name, default=None):
        return args[args.index(name) + 1] if name in args else default
    config = dict(SILVER_CONFIG)
    if opt('--inset-strength'):
        config['normal_map_strength'] = {'Inset': float(opt('--inset-strength'))}
    out = Path(opt('--output'))
    result = run(opt('--input'), out, out.parent / 'textures',
                 apply='--no-rules' not in args and '--skip-v2-rules' not in args,
                 floor_cut='--no-rules' not in args, config=config, save_blend=opt('--save-blend'))
    text = json.dumps(result, indent=2)
    print(text)
    if opt('--report'):
        Path(opt('--report')).write_text(text)
