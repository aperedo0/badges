"""Renders a badge USDZ (use an UNCUT export, whose coin is a full circle) alone on a transparent background,
inside a COPY of a badge master stage scene for its camera and studio lights. The scene's own badge meshes,
floor, haze and backdrop shaft are hidden; the USDZ is placed in raw scene coordinates under the turntable at
rest. Same render settings as render_still.py. Usage:
  Blender --background <stage copy .blend> --python render_still_usdz.py -- <badge.usdz> <out.png>"""
import sys
import bpy
usdz, out = sys.argv[sys.argv.index('--') + 1:][:2]
assert '/badges/stills/work/' in bpy.data.filepath, 'open a copy only'
s = bpy.context.scene
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'; prefs.get_devices()
for d in prefs.devices: d.use = d.type == 'METAL'
s.cycles.device = 'GPU'
s.frame_set(360)
rig = bpy.data.objects['Turntable | one slow 360 degree spin']
rig.animation_data_clear(); rig.location, rig.rotation_euler, rig.scale = (0, 0, 0), (0, 0, 0), (1, 1, 1)
for o in rig.children_recursive:
    o.hide_render = True
for name in ('Floor | polished black with softened reflections', 'Atmosphere | subtle illuminated haze', 'Overhead | soft visible shaft'):
    bpy.data.objects[name].hide_render = True
before = set(bpy.data.objects)
bpy.ops.wm.usd_import(filepath=usdz, import_materials=True, import_usd_preview=True, import_cameras=False,
                      import_lights=False, create_world_material=False, import_textures_mode='IMPORT_PACK')
for root in [o for o in bpy.data.objects if o not in before and o.parent is None]:
    root.matrix_world.identity()          # the file holds raw scene coordinates (Y up)
    root.parent = rig
    root.matrix_parent_inverse.identity()
s.render.film_transparent = True
s.render.use_compositing = False
s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = 1080, 1440, 200
s.cycles.samples = 256
s.cycles.use_denoising = True
st = s.render.image_settings
st.media_type = 'IMAGE'
st.file_format, st.color_mode, st.color_depth = 'PNG', 'RGBA', '16'
s.render.filepath = out
bpy.ops.render.render(write_still=True)
print('WROTE', out)
