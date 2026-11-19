"""Load a badge built by badge3d.py into the open Blender (run through the MCP bridge).

Reads the candidate's parts.npz, parts.json and palette.json named in a job file, updates each part's mesh in place
(objects are never deleted: that closed Blender twice), sets per corner normals, materials and UVs, stands the badge
upright beside the mockup, and saves the badge's own .blend (the job's "blend").

Job file: the path in a BADGE_JOB variable at the top of the code sent through the bridge
(`BADGE_JOB = '/tmp/badge_live_job_<badge>.json'` followed by this file's text), else the newest
/tmp/badge_live_job*.json. Keys: parts, meta, palette, root, blend, scene, prefix, mockup, mockup_width_px, and
optionally allow_unsaved and allow_other_file (both only after the owner says so).
"""
import json, math, os
import numpy as np
import bpy
import glob
JOB_PATH = globals().get('BADGE_JOB') or os.environ.get('BADGE_JOB') or max(glob.glob('/tmp/badge_live_job*.json'), key=os.path.getmtime)   # the newest job
JOB = json.load(open(JOB_PATH)); print('job', JOB_PATH, 'scene', JOB['scene'], 'blend', JOB['blend'])
# Owner rule, November 14, 2026: never overwrite the owner's unsaved changes in the open Blender. Every load
# ends with a save, so unsaved changes here mean someone worked in the window by hand. Stop and ask the owner;
# only after they answer, rerun with "allow_unsaved": true in the job.
if bpy.data.is_dirty and not JOB.get('allow_unsaved'):
    raise RuntimeError('The open Blender file %s has unsaved changes (possibly the owner\'s). Nothing was loaded. '
                       'Ask the owner whether to save or drop them first.' % (bpy.data.filepath or '(never saved)'))
# One file per badge (badge-quality): loading into another badge's file would save that badge's scenes into this
# badge's .blend. Open the badge's own file first (reopen Blender with it), or start an empty Blender for a new badge.
here, target = os.path.abspath(bpy.data.filepath) if bpy.data.filepath else '', os.path.abspath(JOB['blend'])
if here and here != target and not JOB.get('allow_other_file'):
    raise RuntimeError('The open Blender file is %s, not this badge\'s %s. Nothing was loaded. Save it, then reopen '
                       'Blender with this badge\'s file (or an empty one for a new badge) and load again.' % (here, target))
D = np.load(JOB['parts']); META = json.load(open(JOB['meta'])); PAL = json.load(open(JOB['palette']))
SCENE = JOB['scene']
scene = bpy.data.scenes.get(SCENE) or bpy.data.scenes.new(SCENE)
bpy.context.window.scene = scene


def material(name):
    full = JOB['prefix'] + '_' + name if name != 'Gem' else 'CrestGem_FoilSapphire'
    m = bpy.data.materials.get(full) or bpy.data.materials.new(full)
    m.use_nodes = True; bs = m.node_tree.nodes.get('Principled BSDF'); p = PAL.get(name, {})
    if name == 'Gem':
        bs.inputs['Base Color'].default_value = (0.05, 0.45, 0.9, 1); bs.inputs['Roughness'].default_value = 0.05
    elif 'emission_texture' in p:                                 # enamel: near black metal plus the mockup's color as emission
        nodes = m.node_tree.nodes
        texs = {n.label: n for n in nodes if n.type == 'TEX_IMAGE'}
        for key, label in (('color_texture', 'color'), ('emission_texture', 'emission')):
            t = texs.get(label) or nodes.new('ShaderNodeTexImage'); t.label = label
            t.image = bpy.data.images.load(os.path.join(JOB['root'], p[key]), check_existing=True); t.image.reload()
            m.node_tree.links.new(t.outputs['Color'], bs.inputs['Base Color' if label == 'color' else 'Emission Color'])
        bs.inputs['Emission Strength'].default_value = p.get('emission_scale', 8.0)
        bs.inputs['Metallic'].default_value = 1.0; bs.inputs['Roughness'].default_value = p['roughness']
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
    ob.hide_viewport = False; ob.hide_render = False
# pieces of this badge that the new build no longer has: hidden, never deleted (the owner may want to look back)
current = {f'{SCENE} {p["name"]}' for p in META['parts']} | {f'{SCENE} mockup'}
stale = [o for o in scene.objects if o.name.startswith(SCENE + ' ') and o.name not in current]
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
