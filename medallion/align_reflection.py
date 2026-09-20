"""Restore an undistorted mirror reflection and control its extent with fading."""
import bpy
import json
import traceback

STATUS = '/private/tmp/badge-parallel-status.json'

def status(stage, **details):
    with open(STATUS, 'w') as handle:
        json.dump(dict(stage=stage, **details), handle, indent=2)

try:
    scene = bpy.context.scene
    session = bpy.app.driver_namespace.get('_badge_parallel_session')
    if session is None:
        session = dict(filepath=bpy.data.filepath, frame=scene.frame_current,
                       transforms={obj.name: [list(row) for row in obj.matrix_world] for obj in scene.objects})
        bpy.app.driver_namespace['_badge_parallel_session'] = session
        bpy.ops.wm.save_as_mainfile(filepath='/private/tmp/badge-before-parallel-reflection.blend', copy=True)
    floor = bpy.data.objects['Floor | polished black with softened reflections']
    nodes = floor.data.materials[0].node_tree.nodes
    links = floor.data.materials[0].node_tree.links
    surface = next(node for node in nodes if node.type == 'BSDF_PRINCIPLED')
    for link in list(surface.inputs['Normal'].links):
        links.remove(link)
    surface.inputs['IOR'].default_value = 1.5
    for name in (
        'Reflection | one-third height', 'Reflection | normalized outgoing ray',
        'Reflection | surface half vector', 'Reflection | compact floor normal',
        'Reflection | scaled distance numerator', 'Reflection | distance denominator scale',
        'Reflection | distance denominator', 'Reflection | original distance coordinates',
    ):
        if nodes.get(name):
            nodes.remove(nodes[name])
    xyz = next(node for node in nodes if node.type == 'SEPXYZ')
    distance = nodes['Reflection blur | crisp contact to soft foreground']
    distance.label = 'Natural reflection: increasing blur with floor distance'
    distance.inputs['From Min'].default_value = 0
    distance.inputs['From Max'].default_value = 5.75
    links.new(xyz.outputs['Z'], distance.inputs['Value'])
    fade = nodes['Reflection opacity | 90 percent to invisible']
    fade.label = 'Visible extent controlled only by opacity fade'
    fade.inputs['From Min'].default_value = 1.3
    fade.inputs['From Max'].default_value = 5.75
    fade.inputs['To Min'].default_value = .40
    fade.inputs['To Max'].default_value = 1
    links.new(xyz.outputs['Z'], fade.inputs['Value'])
    floor['Reflection'] = 'Natural undistorted reflection; compact visible extent from increasing blur and opacity fade.'
    assert not surface.inputs['Normal'].is_linked
    assert all([list(row) for row in scene.objects[name].matrix_world] == matrix
               for name, matrix in session['transforms'].items())
    saved = (scene.render.resolution_percentage, scene.cycles.samples,
             scene.cycles.adaptive_threshold, scene.render.filepath)
    status('rendering_preview', natural_alignment=True, geometry_and_floor_contact_unchanged=True)
    scene.render.resolution_percentage = 60
    scene.cycles.samples = 48
    scene.cycles.adaptive_threshold = .025
    scene.render.filepath = '/private/tmp/badge-parallel-preview.png'
    try:
        bpy.ops.render.render(write_still=True)
    finally:
        scene.render.resolution_percentage, scene.cycles.samples, scene.cycles.adaptive_threshold, scene.render.filepath = saved
    status('preview_ready', image='/private/tmp/badge-parallel-preview.png')
except Exception:
    status('error', traceback=traceback.format_exc())
    raise
