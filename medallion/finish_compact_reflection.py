"""Render, verify, and save the compact reflection in the existing Blender file."""
import bpy
import json
import os
import traceback

STATUS = '/private/tmp/badge-contact-status.json'

def status(stage, **details):
    with open(STATUS, 'w') as handle:
        json.dump(dict(stage=stage, **details), handle, indent=2)

try:
    scene = bpy.context.scene
    with open('/private/tmp/badge-contact-measurements.json') as handle:
        before = json.load(handle)
    assert bpy.data.filepath == before['filepath']
    assert list(scene.camera.location) == before['camera_location']
    assert list(scene.camera.rotation_euler) == before['camera_rotation']
    assert scene.frame_current == before['frame']
    floor = bpy.data.objects['Floor | polished black with softened reflections']
    casing = bpy.data.objects['Casing | smooth rounded outer edge']
    bottom = min((casing.matrix_world @ vertex.co).y for vertex in casing.data.vertices)
    assert abs(bottom-before['casing_bottom'][1]) < .00001
    assert abs(floor.location.y-bottom-.12) < .00001
    assert floor.data.materials[0].node_tree.nodes['Reflection | one-third height'].inputs[1].default_value[1] == 3
    assert not any(obj.name.startswith('Floor light |') for obj in scene.objects)
    rig = bpy.data.objects['Turntable | one slow 360 degree spin']
    assert rig.animation_data and rig.animation_data.action
    assert scene.frame_end == 360 and scene.render.fps == 30
    scene.cycles.samples = 96
    scene.cycles.adaptive_threshold = .012
    scene.render.resolution_percentage = 100
    output = os.path.join(os.path.dirname(bpy.data.filepath), 'medallion_compact_reflection.png')
    scene.render.filepath = output
    status('rendering_final', camera_unchanged=True, badge_unchanged=True,
           reflection_height_scale=1/3, physical_gap=max(0, bottom-floor.location.y))
    bpy.ops.render.render(write_still=True)
    finished = bpy.data.images.load(output, check_existing=True)
    finished.name = 'Medallion | compact grounded reflection'
    finished.use_fake_user = True
    finished.pack()
    area = bpy.context.area
    area.type = 'IMAGE_EDITOR'
    area.spaces.active.image = finished
    region = next(region for region in area.regions if region.type == 'WINDOW')
    with bpy.context.temp_override(area=area, region=region):
        bpy.ops.image.view_all(fit_view=True)
    scene.render.filepath = '//medallion_compact_reflection.png'
    bpy.ops.wm.save_as_mainfile(filepath=before['filepath'])
    assert finished.packed_file and os.path.getsize(output) > 0
    status('complete', blend=bpy.data.filepath, render=output,
           resolution=[scene.render.resolution_x, scene.render.resolution_y],
           camera_unchanged=True, badge_unchanged=True, animation_preserved=True,
           reflection_height_scale=1/3, physical_gap=max(0, bottom-floor.location.y),
           render_packed=True)
    print('CONTACT_VERIFIED: no floor gap; reflection height one-third; camera, badge and spin preserved; same project saved')
except Exception:
    status('error', traceback=traceback.format_exc())
    raise
