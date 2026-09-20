"""Create a 12-second, single-turn video setup from the saved medallion."""
import bpy
import math
import os
import sys
import time

OUT = os.path.dirname(os.path.abspath(__file__))
FRAMES = '/private/tmp/medallion-spin-frames'
PREVIEW = '--preview' in sys.argv
os.makedirs(FRAMES, exist_ok=True)
scene = bpy.context.scene
model = bpy.data.collections['01 | Medallion']
parts = [obj for obj in model.objects if obj.type == 'MESH']
assert len(parts) == 8, 'Expected the eight original medallion parts.'

turntable = bpy.data.objects.new('Turntable | one slow 360 degree spin', None)
model.objects.link(turntable)
turntable.empty_display_type = 'PLAIN_AXES'
turntable.empty_display_size = .6
for obj in parts:
    transform = obj.matrix_world.copy()
    obj.parent = turntable
    obj.matrix_world = transform

scene.frame_start = 1
scene.frame_end = 360
scene.render.fps = 30
scene.render.fps_base = 1
turntable.rotation_mode = 'XYZ'
turntable.rotation_euler = (0, 0, 0)
turntable.keyframe_insert(data_path='rotation_euler', index=1, frame=1)
turntable.rotation_euler.y = math.tau
turntable.keyframe_insert(data_path='rotation_euler', index=1, frame=360)
action = turntable.animation_data.action
action.name = 'Single full turn | 12 seconds | constant speed'
for layer in action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for curve in bag.fcurves:
                for key in curve.keyframe_points:
                    key.interpolation = 'LINEAR'
turntable['Motion'] = 'One full rotation about the vertical Y axis, from frame 1 to 360.'
scene['Video'] = '12 seconds at 30 fps. Fixed camera and lights. One complete turn.'
scene.timeline_markers.clear()
for name, frame in [('Front / start',1), ('Side',91), ('Back',181), ('Side',270), ('Front / end',360)]:
    scene.timeline_markers.new(name, frame=frame)

scene.render.engine = 'BLENDER_EEVEE'
scene.eevee.taa_render_samples = 64
scene.eevee.use_raytracing = True
scene.eevee.use_fast_gi = True
scene.eevee.shadow_ray_count = 2
scene.eevee.shadow_step_count = 8
scene.render.resolution_x = 1080
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.image_settings.color_depth = '8'
scene.render.image_settings.compression = 15
scene.render.use_file_extension = True
scene.render.filepath = '//spin_frames/frame_'
scene.frame_set(1)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'silver_medallion_spin.blend'))
print('ANIMATION_SAVED: 360 frames at 30 fps, one full turn', flush=True)

if PREVIEW:
    for frame in (1, 91, 181, 270):
        scene.frame_set(frame)
        scene.render.filepath = os.path.join(FRAMES, f'preview_{frame:04d}.png')
        started = time.monotonic()
        bpy.ops.render.render(write_still=True)
        print(f'PREVIEW_FRAME: {frame}, {time.monotonic()-started:.1f} seconds', flush=True)
else:
    scene.render.filepath = os.path.join(FRAMES, 'frame_')
    bpy.ops.render.render(animation=True)
    print('ANIMATION_RENDERED: 360 frames', flush=True)
