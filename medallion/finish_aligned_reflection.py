"""Save the natural floor reflection with its compact fade and blur gradients."""
import bpy
import json
import os
import traceback

STATUS = '/private/tmp/badge-parallel-status.json'

def status(stage, **details):
    with open(STATUS, 'w') as handle:
        json.dump(dict(stage=stage, **details), handle, indent=2)

try:
    scene = bpy.context.scene
    session = bpy.app.driver_namespace['_badge_parallel_session']
    assert bpy.data.filepath == session['filepath']
    assert scene.frame_current == session['frame']
    assert all([list(row) for row in scene.objects[name].matrix_world] == matrix
               for name, matrix in session['transforms'].items())
    nodes = bpy.data.objects['Floor | polished black with softened reflections'].data.materials[0].node_tree.nodes
    nodes['Reflection blur | crisp contact to soft foreground'].inputs['From Max'].default_value = 5.75
    nodes['Reflection opacity | 90 percent to invisible'].inputs['From Max'].default_value = 5.75
    surface = next(node for node in nodes if node.type == 'BSDF_PRINCIPLED')
    assert not surface.inputs['Normal'].is_linked
    assert nodes.get('Reflection | one-third height') is None
    for name in ('Reflection blur | crisp contact to soft foreground',
                 'Reflection opacity | 90 percent to invisible'):
        assert nodes[name].inputs['Value'].links[0].from_node.type == 'SEPXYZ'
    rig = bpy.data.objects['Turntable | one slow 360 degree spin']
    assert rig.animation_data and rig.animation_data.action
    assert scene.frame_end == 360 and scene.render.fps == 30
    output = os.path.join(os.path.dirname(bpy.data.filepath), 'medallion_parallel_reflection.png')
    scene.render.filepath = output
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 96
    scene.cycles.adaptive_threshold = .012
    status('rendering_final', natural_alignment=True, geometry_and_contact_unchanged=True)
    bpy.ops.render.render(write_still=True)
    finished = bpy.data.images.load(output, check_existing=True)
    finished.name = 'Medallion | natural aligned reflection'
    finished.use_fake_user = True
    finished.pack()
    area = bpy.context.area
    area.type = 'IMAGE_EDITOR'
    area.spaces.active.image = finished
    region = next(region for region in area.regions if region.type == 'WINDOW')
    with bpy.context.temp_override(area=area, region=region):
        bpy.ops.image.view_all(fit_view=True)
    scene.render.filepath = '//medallion_parallel_reflection.png'
    bpy.ops.wm.save_as_mainfile(filepath=session['filepath'])
    assert finished.packed_file and os.path.getsize(output) > 0
    status('complete', blend=bpy.data.filepath, render=output,
           natural_alignment=True, geometry_and_contact_unchanged=True,
           size_control='opacity fade and increasing blur only',
           animation_preserved=True, render_packed=True)
except Exception:
    status('error', traceback=traceback.format_exc())
    raise
