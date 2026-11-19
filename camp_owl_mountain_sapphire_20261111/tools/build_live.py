"""Load a badge built by badge3d.py into the open Blender (run through the MCP bridge).

Reads rebuild/candNN/parts.npz, parts.json and palette.json (paths from rebuild/live_job.json), updates each
part's mesh in place (objects are never deleted: that closed Blender twice), sets per corner normals, materials
and UVs, stands the badge upright beside the mockup, and saves rebuild/mountain_sunburst_rebuild.blend.
"""
import json, math, os
import numpy as np
import bpy
import glob
JOB_PATH = os.environ.get('BADGE_JOB') or max(glob.glob('/tmp/badge_live_job*.json'), key=os.path.getmtime)   # the newest job
JOB = json.load(open(JOB_PATH)); print('job', JOB_PATH, 'scene', JOB['scene'], 'blend', JOB['blend'])
D = np.load(JOB['parts']); META = json.load(open(JOB['meta'])); PAL = json.load(open(JOB['palette']))
SCENE = JOB['scene']
scene = bpy.data.scenes.get(SCENE) or bpy.data.scenes.new(SCENE)
bpy.context.window.scene = scene


def material(name):
    full = JOB['prefix'] + '_' + name if name != 'Gem' else PAL.get(name, {}).get('material_name', 'CrestGem_SapphireClear')
    m = bpy.data.materials.get(full) or bpy.data.materials.new(full)
    m.use_nodes = True; bs = m.node_tree.nodes.get('Principled BSDF'); p = PAL.get(name, {})
    if name == 'Gem':
        bs.inputs['Base Color'].default_value = (0.05, 0.45, 0.9, 1); bs.inputs['Roughness'].default_value = 0.05; bs.inputs['Transmission Weight'].default_value = 1; bs.inputs['IOR'].default_value = 1.77
    elif 'emission_texture' in p:                                 # enamel: near black metal plus the mockup's color as emission
        nodes = m.node_tree.nodes
        texs = {n.label: n for n in nodes if n.type == 'TEX_IMAGE'}
        for key, label in (('color_texture', 'color'), ('emission_texture', 'emission')):
            t = texs.get(label) or nodes.new('ShaderNodeTexImage'); t.label = label
            t.image = bpy.data.images.load(os.path.join(JOB['root'], p[key]), check_existing=True); t.image.reload()
            m.node_tree.links.new(t.outputs['Color'], bs.inputs['Base Color' if label == 'color' else 'Emission Color'])
        bs.inputs['Emission Strength'].default_value = p.get('emission_scale', 8.0)
        bs.inputs['Metallic'].default_value = p.get('enamel_metallic', 1.0); bs.inputs['Roughness'].default_value = p['roughness']
    elif 'texture' in p:
        nodes = m.node_tree.nodes
        tex = next((n for n in nodes if n.type == 'TEX_IMAGE'), None) or nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(os.path.join(JOB['root'], p['texture']), check_existing=True); tex.image.reload()
        m.node_tree.links.new(tex.outputs['Color'], bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = p['roughness']
    else:
        a = p.get('albedo', [0.8, 0.8, 0.8]); bs.inputs['Base Color'].default_value = (*a, 1)
        bs.inputs['Metallic'].default_value = p.get('metallic', 0.0); bs.inputs['Roughness'].default_value = p.get('roughness', 0.3)
    if 'roughness_texture' in p:
        nodes=m.node_tree.nodes
        tex=next((n for n in nodes if n.label=='brushed roughness'),None) or nodes.new('ShaderNodeTexImage')
        tex.label='brushed roughness'
        tex.image=bpy.data.images.load(os.path.join(JOB['root'],p['roughness_texture']),check_existing=True)
        tex.image.colorspace_settings.name='Non-Color'
        tex.extension='REPEAT'
        if 'roughness_texture_scale' in p:
            scale=next((n for n in nodes if n.label=='brushed roughness contrast'),None) or nodes.new('ShaderNodeMath')
            scale.label='brushed roughness contrast';scale.operation='MULTIPLY_ADD'
            scale.inputs[1].default_value=p['roughness_texture_scale'];scale.inputs[2].default_value=p.get('roughness_texture_bias',0.0)
            m.node_tree.links.new(tex.outputs['Color'],scale.inputs[0]);m.node_tree.links.new(scale.outputs[0],bs.inputs['Roughness'])
        else:
            m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Roughness'])
    else:
        for link in list(bs.inputs['Roughness'].links):m.node_tree.links.remove(link)
    return m


for part in META['parts']:
    name = part['name']; V = D[name + '_v'].reshape(-1, 3); N = D[name + '_n'].reshape(-1, 3); UV = D[name + '_uv'].reshape(-1, 2)
    M = D[name + '_m']
    key = V.astype(np.float32); uniq, inv = np.unique(key, axis=0, return_inverse=True)
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
    ob.hide_viewport = False; ob.hide_render = False
# pieces of this badge that the new build no longer has: hidden, never deleted (the owner may want to look back)
current = {f'{SCENE} {p["name"]}' for p in META['parts']} | {f'{SCENE} mockup'}
stale = [o for o in scene.objects if o.type == 'MESH' and o.name.startswith(SCENE + ' ') and o.name not in current]
for o in stale:
    o.hide_viewport = True; o.hide_render = True
if stale:
    print('hidden old pieces:', ', '.join(o.name for o in stale))
ref = bpy.data.objects.get(f'{SCENE} mockup')
if ref is None:
    ref = bpy.data.objects.new(f'{SCENE} mockup', None); ref.empty_display_type = 'IMAGE'
    ref.data = bpy.data.images.load(JOB['mockup'], check_existing=True); scene.collection.objects.link(ref)
ref.empty_display_size = JOB['mockup_width_px'] * META['units']['S']; ref.location = (-6.8, 0, 0.27); ref.rotation_euler = (math.pi / 2, 0, 0)
bpy.ops.wm.save_as_mainfile(filepath=JOB['blend'])
print('loaded', len(META['parts']), 'parts,', sum(p['triangles'] for p in META['parts']), 'triangles; saved', JOB['blend'])
