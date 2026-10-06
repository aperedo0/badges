"""Renders the badge for the v2 proof images, always from a COPY of the master stage scene.

  Blender --background <copy of silver_medallion_stage_refined.blend> --python render_proof.py -- \
      --variant master|<file.usdz> --rig stage|harsh --pose DEGREES --out <file.png> \
      [--samples N] [--no-denoise] [--seed N] [--border x0,x1,y0,y1] [--inset-strength K] [--harsh-scale F] [--flat-casing-maps] [--master-bevel WIDTH,SEGMENTS]

variant master  renders the artist's procedural badge (Blender's own look).
variant <usdz>  hides the master badge and renders that export in its place, at the
                same transform (the USD is Y up with raw scene coordinates).
rig stage       the scene's own six lights, world, Cycles, AgX Medium High Contrast, Glare.
rig harsh       the scene's lights off; the app's eight point lights instead (same
                positions, colors and relative intensities as TestBadge3DStudioLight.all),
                zero radius, which exposes blotches and glints the softboxes hide.
--inset-strength  scales the imported inset normal map (Normal Map node Strength), used
                only to calibrate rule 4.
"""
import math
import sys

import bpy

args = sys.argv[sys.argv.index('--') + 1:]


def opt(name, default=None):
    return args[args.index(name) + 1] if name in args else default


variant, rig_name = opt('--variant'), opt('--rig', 'stage')
pose, out = float(opt('--pose', '0')), opt('--out')
scene = bpy.context.scene
assert bpy.data.filepath.startswith('/Users/antonioperedo/Downloads/badge_realitykit_iron/scenes/'), 'open a copy only'
bpy.context.preferences.filepaths.save_version = 0

# GPU for speed; every variant uses the same device and settings.
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'
prefs.get_devices()
for device in prefs.devices:
    device.use = device.type == 'METAL'
scene.cycles.device = 'GPU'
if opt('--samples'):
    scene.cycles.samples = int(opt('--samples'))
if '--no-denoise' in args:
    scene.cycles.use_denoising = False
    scene.cycles.use_adaptive_sampling = False
if opt('--seed'):
    scene.cycles.seed = int(opt('--seed'))

scene.frame_set(360)
rig = bpy.data.objects['Turntable | one slow 360 degree spin']
rig.animation_data_clear()
rig.location, rig.rotation_euler, rig.scale = (0, 0, 0), (0, math.radians(pose), 0), (1, 1, 1)

if opt('--master-bevel'):
    # Question D preview only (never saved): the master emblem's edge bevel, width and segments.
    width, segments = opt('--master-bevel').split(',')
    bevel = next(m for m in bpy.data.objects['Emblem | faceted compass spear'].modifiers if m.type == 'BEVEL')
    bevel.width, bevel.segments = float(width), int(segments)

if variant != 'master':
    for obj in rig.children_recursive:
        if obj.type == 'MESH':
            obj.hide_render = True
    before = set(bpy.data.objects)
    bpy.ops.wm.usd_import(filepath=variant, import_materials=True, import_usd_preview=True,
                          import_cameras=False, import_lights=False, create_world_material=False,
                          import_textures_mode='IMPORT_PACK', mtl_name_collision_mode='MAKE_UNIQUE')
    new = [o for o in bpy.data.objects if o not in before]
    roots = [o for o in new if o.parent is None]
    for root in roots:
        # Undo the importer's Y-up to Z-up turn: the file holds raw scene coordinates.
        root.matrix_world.identity()
        root.parent = rig
        root.matrix_parent_inverse.identity()
    strength = opt('--inset-strength')
    for obj in new:
        if obj.type != 'MESH':
            continue
        for mat in obj.data.materials:
            for node in mat.node_tree.nodes:
                if node.type == 'NORMAL_MAP' and strength and 'Inset' in mat.name:
                    node.inputs['Strength'].default_value = float(strength)
    if '--flat-casing-maps' in args:
        # Diagnostic only: the brushed steel's baked color and roughness maps replaced by constants.
        for obj in new:
            if obj.type == 'MESH' and obj.name.startswith('Casing'):
                for mat in obj.data.materials:
                    if not mat.name.startswith('Silver___circumferential'):
                        continue
                    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
                    for name, value in (('Base Color', (0.345, 0.335, 0.318, 1)), ('Roughness', 0.325)):
                        for link in list(bsdf.inputs[name].links):
                            mat.node_tree.links.remove(link)
                        bsdf.inputs[name].default_value = value
    print('IMPORTED', sorted(o.name for o in new if o.type == 'MESH'))

if rig_name == 'harsh':
    for obj in scene.objects:
        if obj.type == 'LIGHT':
            obj.hide_render = True
    # position, linear RGB, RealityKit lumens (BadgeHeroCard.swift TestBadge3DStudioLight.all)
    app_lights = [
        ((-5.4, 3.5, 2.8), (1, 0.98, 0.95), 1_156_500),
        ((5.393, 2.023, 3.426), (0.98, 0.99, 1), 226_633),
        ((4.8, 1.8, 4.2), (0.98, 0.99, 1), 226_633),
        ((4.207, 1.577, 4.974), (0.98, 0.99, 1), 226_633),
        ((-0.3, 5.1, 3.5), (1, 0.99, 0.98), 958_800),
        ((-2.075, -2.375, 4.375), (1, 0.985, 0.96), 300_000),
        ((-1.525, -1.825, 4.825), (1, 0.985, 0.96), 300_000),
        ((0, 0.6, 7.5), (1, 1, 1), 83_800),
    ]
    scale = float(opt('--harsh-scale', '1.0'))
    for i, (position, color, lumens) in enumerate(app_lights):
        data = bpy.data.lights.new(f'Harsh point {i}', 'POINT')
        data.energy = lumens / 683.0 * scale
        data.color = color
        data.shadow_soft_size = 0.0
        light = bpy.data.objects.new(f'Harsh point {i}', data)
        light.location = position
        scene.collection.objects.link(light)

if '--realtime' in args:
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.use_raytracing = False

# Render only the badge region (full-size frame, black outside) to save time.
scene.render.use_border, scene.render.use_crop_to_border = True, False
x0, x1, y0, y1 = (float(v) for v in opt('--border', '0.19,0.81,0.30,0.77').split(','))
scene.render.border_min_x, scene.render.border_max_x = x0, x1
scene.render.border_min_y, scene.render.border_max_y = y0, y1
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1080, 1440, 100
scene.render.use_compositing, scene.render.use_sequencer = True, False
settings = scene.render.image_settings
settings.media_type = 'IMAGE'
settings.file_format, settings.color_mode, settings.color_depth, settings.compression = 'PNG', 'RGB', '8', 90
scene.render.dither_intensity = 0
scene.render.filepath = out
result = bpy.ops.render.render(write_still=True)
assert 'FINISHED' in result, result
print('RENDERED', out)
