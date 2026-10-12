"""Re-imports a badge USDZ into an empty Blender scene and lists what came in.

  Blender --background --factory-startup --python reimport_check.py -- <file.usdz>
"""
import sys
import bpy
import numpy as np

path = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
result = bpy.ops.wm.usd_import(filepath=path, import_materials=True, import_usd_preview=True,
                               import_textures_mode='IMPORT_PACK', validate_meshes=True)
print('import result', result)
tris = 0
for obj in sorted(bpy.context.scene.objects, key=lambda o: o.name):
    if obj.type != 'MESH':
        print(f'OBJECT {obj.name} ({obj.type})')
        continue
    mesh = obj.data
    mesh.calc_loop_triangles()
    tris += len(mesh.loop_triangles)
    co = np.empty(len(mesh.vertices) * 3)
    mesh.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    counts = {}
    for p in mesh.polygons:
        name = mesh.materials[p.material_index].name if mesh.materials else None
        counts[name] = counts.get(name, 0) + 1
    print(f'MESH {obj.name}: {len(mesh.vertices)} verts, {len(mesh.loop_triangles)} tris, custom normals {mesh.has_custom_normals}, '
          f'UVs {[u.name for u in mesh.uv_layers]}, local bounds min {np.round(co.min(0), 5).tolist()} max {np.round(co.max(0), 5).tolist()}')
    for name, n in counts.items():
        print(f'    material {name}: {n} faces')
print('TOTAL TRIANGLES', tris)
for mat in bpy.data.materials:
    if not mat.users:
        continue
    bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    links = {s.name: s.links[0].from_node.type for s in bsdf.inputs if s.is_linked} if bsdf else {}
    values = {k: round(bsdf.inputs[k].default_value, 4) for k in ('Metallic', 'Roughness') if not bsdf.inputs[k].is_linked}
    color = tuple(round(c, 4) for c in bsdf.inputs['Base Color'].default_value[:3]) if not bsdf.inputs['Base Color'].is_linked else 'texture'
    images = [n.image.name for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
    print(f'MATERIAL {mat.name}: base color {color}, {values}, linked inputs {links}, images {images}')
for img in bpy.data.images:
    if img.users:
        print(f'IMAGE {img.name}: {img.size[0]}x{img.size[1]}, {img.colorspace_settings.name}, packed {bool(img.packed_file)}')
