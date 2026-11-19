"""Load the rebuilt Radiant Mountain Sunburst into the open Blender (run through the MCP bridge).

Reads rebuild/candNN/parts.npz, parts.json and palette.json (paths from rebuild/live_job.json), updates each
part's mesh in place (objects are never deleted: that closed Blender twice), sets per corner normals, materials
and UVs, stands the badge upright beside the mockup, and saves rebuild/mountain_sunburst_rebuild.blend.
"""
import json, math, os
import numpy as np
import bpy
JOB = json.load(open('/Users/antonioperedo/Desktop/badges/mountain_sunburst_claude_20261108/rebuild/live_job.json'))
D = np.load(JOB['parts']); META = json.load(open(JOB['meta'])); PAL = json.load(open(JOB['palette']))
SCENE = 'Mountain Sunburst Rebuild'
scene = bpy.data.scenes.get(SCENE) or bpy.data.scenes.new(SCENE)
bpy.context.window.scene = scene


def material(name):
    full = 'MountainSunburst_' + name if name != 'Gem' else 'CrestGem_FoilSapphire'
    m = bpy.data.materials.get(full) or bpy.data.materials.new(full)
    m.use_nodes = True; bs = m.node_tree.nodes.get('Principled BSDF'); p = PAL.get(name, {})
    if name == 'Gem':
        bs.inputs['Base Color'].default_value = (0.05, 0.45, 0.9, 1); bs.inputs['Roughness'].default_value = 0.05
    elif 'texture' in p:
        nodes = m.node_tree.nodes
        tex = next((n for n in nodes if n.type == 'TEX_IMAGE'), None) or nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(os.path.join(JOB['root'], p['texture']), check_existing=True); tex.image.reload()
        m.node_tree.links.new(tex.outputs['Color'], bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = p['roughness']
    else:
        a = p.get('albedo', [0.8, 0.8, 0.8]); bs.inputs['Base Color'].default_value = (*a, 1)
        bs.inputs['Metallic'].default_value = p.get('metallic', 0.0); bs.inputs['Roughness'].default_value = p.get('roughness', 0.3)
    return m


for part in META['parts']:
    name = part['name']; V = D[name + '_v'].reshape(-1, 3); N = D[name + '_n'].reshape(-1, 3); UV = D[name + '_uv'].reshape(-1, 2)
    M = D[name + '_m']
    key = np.round(V, 6); uniq, inv = np.unique(key, axis=0, return_inverse=True)
    faces = inv.reshape(-1, 3)
    obj_name = f'{SCENE} {name}'
    ob = bpy.data.objects.get(obj_name); me = ob.data if ob else bpy.data.meshes.new(obj_name)
    me.clear_geometry(); me.from_pydata(uniq.tolist(), [], faces.tolist()); me.update()
    me.materials.clear()
    for mname in part['materials']:
        me.materials.append(material(mname))
    me.polygons.foreach_set('material_index', M.astype(np.int32))
    if not me.uv_layers:
        me.uv_layers.new(name='st')
    me.uv_layers[0].data.foreach_set('uv', UV.ravel().astype(np.float32))
    me.normals_split_custom_set([tuple(n) for n in N])
    me.update()
    if ob is None:
        ob = bpy.data.objects.new(obj_name, me); scene.collection.objects.link(ob)
    elif ob.name not in scene.objects:
        scene.collection.objects.link(ob)
    ob.rotation_euler = (math.pi / 2, 0, 0)          # upright in Blender; the data stays Y up
ref = bpy.data.objects.get(f'{SCENE} mockup')
if ref is None:
    ref = bpy.data.objects.new(f'{SCENE} mockup', None); ref.empty_display_type = 'IMAGE'
    ref.data = bpy.data.images.load(JOB['mockup'], check_existing=True); scene.collection.objects.link(ref)
ref.empty_display_size = 1312 * 5.45 / 1161; ref.location = (-6.8, 0, 0.27); ref.rotation_euler = (math.pi / 2, 0, 0)
bpy.ops.wm.save_as_mainfile(filepath=JOB['blend'])
print('loaded', len(META['parts']), 'parts,', sum(p['triangles'] for p in META['parts']), 'triangles; saved', JOB['blend'])
