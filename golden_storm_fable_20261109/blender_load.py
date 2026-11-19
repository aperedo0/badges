"""Load the built Golden Storm into the owner's open Blender (run through the bridge).

Objects are updated in place and never deleted. The scene is saved as one file for this badge.
"""
import json, math, os
import numpy as np
import bpy

ROOT = '/Users/antonioperedo/Desktop/badges/golden_storm_fable_20261109'
CAND = open(os.path.join(ROOT, 'candidate.txt')).read().strip()
C = os.path.join(ROOT, CAND)
D = np.load(os.path.join(C, 'geometry.npz')); META = json.load(open(os.path.join(C, 'parts.json')))
MATS = json.load(open(os.path.join(C, 'materials.json'))); ART = json.load(open(os.path.join(C, 'textures/art.json')))
SCENE = 'Golden Storm'
scene = bpy.data.scenes.get(SCENE) or bpy.data.scenes.new(SCENE)
bpy.context.window.scene = scene


def material(role):
    name = 'GoldenStorm_' + role
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF'); spec = MATS[role]
    bs.inputs['Base Color'].default_value = (*spec['color'], 1)
    bs.inputs['Metallic'].default_value = spec['metallic']; bs.inputs['Roughness'].default_value = spec['roughness']
    if role in ('art', 'art_bolt'):
        nodes = m.node_tree.nodes
        tex = next((n for n in nodes if n.type == 'TEX_IMAGE'), None) or nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(os.path.join(C, 'textures', 'bolt_emission.png' if role == 'art_bolt' else 'art_emission.png'), check_existing=True); tex.image.reload()
        tex.interpolation = 'Cubic'          # smooth when zoomed far past the picture's own pixels
        if role == 'art_bolt':
            tex.image.colorspace_settings.name = 'Non-Color'
        m.node_tree.links.new(tex.outputs['Color'], bs.inputs['Emission Color'])
        bs.inputs['Emission Strength'].default_value = ART['bolt_scale'] if role == 'art_bolt' else ART['emission_scale']
    return m


total = 0
for i, part in enumerate(META['parts']):
    v = D[f'{i}_v']; n = D[f'{i}_n']; uv = D[f'{i}_uv']; t = D[f'{i}_t']
    name = SCENE + ' ' + part['name']
    ob = bpy.data.objects.get(name); me = ob.data if ob else bpy.data.meshes.new(name)
    me.clear_geometry(); me.from_pydata(v.tolist(), [], t.tolist()); me.update()
    me.materials.clear(); me.materials.append(material(part['role']))
    if not me.uv_layers:
        me.uv_layers.new(name='StormUV')
    me.uv_layers[0].data.foreach_set('uv', uv[t.ravel()].ravel().astype(np.float32))
    me.polygons.foreach_set('use_smooth', np.ones(len(t), bool))
    me.normals_split_custom_set_from_vertices([tuple(x) for x in n])
    me.update()
    if ob is None:
        ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    elif ob.name not in scene.objects:
        scene.collection.objects.link(ob)
    ob.rotation_euler = (math.pi / 2, 0, 0)      # stands upright in Blender; the data stays Y up
    ob.hide_viewport = False; ob.hide_render = False
    total += len(t)
# Objects from an earlier version that this one no longer has are hidden, never deleted (deleting objects closed
# Blender twice in an earlier chat).
current = {SCENE + ' ' + part['name'] for part in META['parts']} | {SCENE + ' mockup'}
stale = [o for o in scene.objects if o.name.startswith(SCENE + ' ') and o.name not in current]
for o in stale:
    o.hide_viewport = True; o.hide_render = True
    if not o.hide_get():
        o.hide_set(True)
if stale:
    print('hidden earlier objects:', len(stale))
ref = bpy.data.objects.get(SCENE + ' mockup')
if ref is None:
    ref = bpy.data.objects.new(SCENE + ' mockup', None); ref.empty_display_type = 'IMAGE'
    ref.data = bpy.data.images.load(os.path.join(ROOT, 'reference/mockup.png'), check_existing=True); scene.collection.objects.link(ref)
ref.empty_display_size = META['mockup_size'][0] * META['units_per_pixel']; ref.location = (-6.4, 0, .28); ref.rotation_euler = (math.pi / 2, 0, 0)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, 'golden_storm.blend'))
print('loaded', len(META['parts']), 'pieces,', total, 'triangles from', CAND)
