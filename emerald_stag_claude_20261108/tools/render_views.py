# Blender -b FILE.blend --python render_views.py -- OUT_PREFIX "yaw,pitch;..." : workbench renders of the saved scene
import sys, math, bpy, mathutils
argv = sys.argv[sys.argv.index('--') + 1:]
out, views = argv[0], [tuple(float(x) for x in v.split(',')) for v in argv[1].split(';')]
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'MATERIAL'
sc.display.shading.show_specular_highlight = True
sc.render.resolution_x = 700; sc.render.resolution_y = 800; sc.render.film_transparent = False
cam_data = bpy.data.cameras.new('cam'); cam_data.lens = 85
cam = bpy.data.objects.new('cam', cam_data); sc.collection.objects.link(cam); sc.camera = cam
target = mathutils.Vector((0, 0, 0.25))
for i, (yaw, pitch) in enumerate(views):
    d = 22.0
    y, p = math.radians(yaw), math.radians(pitch)
    pos = mathutils.Vector((d * math.sin(y) * math.cos(p), -d * math.cos(y) * math.cos(p), d * math.sin(p))) + target
    cam.location = pos
    cam.rotation_euler = (target - pos).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = f'{out}_{i}.png'
    bpy.ops.render.render(write_still=True)
print('rendered', len(views))
