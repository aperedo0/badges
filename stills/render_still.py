"""Renders a badge's coin alone (no floor, haze or backdrop light) on a transparent background, from a COPY
of its master scene, at rest, with the scene's own studio lights and AgX Medium High Contrast (the look the
app's lighting was tuned to). Compositing (glare) off. Usage:
  Blender --background <copy.blend> --python render_still.py -- <out.png>"""
import sys
import bpy
out = sys.argv[sys.argv.index('--') + 1]
assert '/badges/stills/work/' in bpy.data.filepath, 'open a copy only'
s = bpy.context.scene
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'; prefs.get_devices()
for d in prefs.devices: d.use = d.type == 'METAL'
s.cycles.device = 'GPU'
s.frame_set(360)
rig = bpy.data.objects['Turntable | one slow 360 degree spin']
rig.animation_data_clear(); rig.location, rig.rotation_euler, rig.scale = (0, 0, 0), (0, 0, 0), (1, 1, 1)
for name in ('Floor | polished black with softened reflections', 'Atmosphere | subtle illuminated haze', 'Overhead | soft visible shaft'):
    bpy.data.objects[name].hide_render = True
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
