"""Render and save the approved floor refinement in the current Blender file."""
import bpy
import json
import os
import traceback

STATUS = '/private/tmp/badge-polished-floor-status.json'

def status(stage, **details):
    with open(STATUS, 'w') as handle:
        json.dump(dict(stage=stage, **details), handle, indent=2)

try:
    scene = bpy.context.scene
    session = bpy.app.driver_namespace['_badge_floor_session']
    assert bpy.data.filepath == session['filepath']
    assert scene.frame_current == session['frame']
    assert all([list(row) for row in scene.objects[name].matrix_world] == matrix
               for name, matrix in session['transforms'].items())
    floor = bpy.data.objects['Floor | polished black with softened reflections']
    fade = floor.data.materials[0].node_tree.nodes['Reflection opacity | 90 percent to invisible']
    assert fade.inputs['From Max'].default_value == 13
    assert not any(obj.name.startswith('Floor light |') for obj in scene.objects)
    rig = bpy.data.objects['Turntable | one slow 360 degree spin']
    assert rig.animation_data and rig.animation_data.action
    assert scene.frame_end == 360 and scene.render.fps == 30
    scene.cycles.samples = 96
    scene.cycles.adaptive_threshold = .012
    scene.render.resolution_percentage = 100
    output = os.path.join(os.path.dirname(bpy.data.filepath), 'medallion_polished_floor.png')
    scene.render.filepath = output
    status('rendering_final', geometry_and_camera_unchanged=True,
           fade_endpoint_unchanged=True, animation_preserved=True)
    bpy.ops.render.render(write_still=True)
    finished = bpy.data.images.load(output, check_existing=True)
    finished.name = 'Medallion | polished black glass floor'
    finished.use_fake_user = True
    finished.pack()
    # Return Layout to its original 3D editor; show the finished image in Rendering.
    bpy.context.area.type = 'VIEW_3D'
    workspace = bpy.data.workspaces.get('Rendering')
    if workspace:
        bpy.context.window.workspace = workspace
    for screen in bpy.data.screens:
        if screen.name == 'Rendering':
            for area in screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    area.spaces.active.image = finished
    scene.render.filepath = '//medallion_polished_floor.png'
    bpy.ops.wm.save_as_mainfile(filepath=session['filepath'])
    assert finished.packed_file and os.path.getsize(output) > 0
    status('complete', blend=bpy.data.filepath, render=output,
           resolution=[scene.render.resolution_x, scene.render.resolution_y],
           geometry_and_camera_unchanged=True, fade_endpoint_unchanged=True,
           animation_preserved=True, render_packed=True)
    print('FLOOR_VERIFIED: original geometry, camera, reflection endpoint and spin preserved; render saved and packed')
except Exception:
    status('error', traceback=traceback.format_exc())
    raise
