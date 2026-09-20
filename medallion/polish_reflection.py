"""Refine the floor in the already open Blender scene and render in place."""
import bpy
import json
import traceback

STATUS = '/private/tmp/badge-polished-floor-status.json'

def status(stage, **details):
    with open(STATUS, 'w') as handle:
        json.dump(dict(stage=stage, **details), handle, indent=2)

def run():
    scene = bpy.context.scene
    session = bpy.app.driver_namespace.get('_badge_floor_session')
    if session is None:
        session = dict(
            filepath=bpy.data.filepath,
            transforms={obj.name: [list(row) for row in obj.matrix_world]
                        for obj in scene.objects},
            frame=scene.frame_current,
            render_path=scene.render.filepath,
            resolution=(scene.render.resolution_x, scene.render.resolution_y,
                        scene.render.resolution_percentage),
            samples=scene.cycles.samples,
            threshold=scene.cycles.adaptive_threshold,
        )
        bpy.app.driver_namespace['_badge_floor_session'] = session
        bpy.ops.wm.save_as_mainfile(filepath='/private/tmp/badge-before-floor-polish.blend', copy=True)
    floor = bpy.data.objects['Floor | polished black with softened reflections']
    material = floor.data.materials[0]
    nodes, links = material.node_tree.nodes, material.node_tree.links
    surface = next(node for node in nodes if node.type == 'BSDF_PRINCIPLED')
    surface.inputs['Base Color'].default_value = (.0005, .0007, .001, 1)
    surface.inputs['Metallic'].default_value = 0
    surface.inputs['IOR'].default_value = 1.5
    surface.inputs['Coat Weight'].default_value = 0

    distance = nodes.get('Reflection blur | crisp contact to soft foreground')
    distance.label = 'Reflection distance: contact to original fade endpoint'
    distance.interpolation_type = 'LINEAR'
    distance.inputs['From Min'].default_value = 0
    distance.inputs['From Max'].default_value = 13
    distance.inputs['To Min'].default_value = 0
    distance.inputs['To Max'].default_value = 1
    distance.clamp = True
    blur = nodes.get('Reflection | delayed blur') or nodes.new('ShaderNodeValToRGB')
    blur.name = 'Reflection | delayed blur'
    blur.label = 'Preserve facets through the middle, soften the lower reflection'
    ramp = blur.color_ramp
    while len(ramp.elements) > 2:
        ramp.elements.remove(ramp.elements[-1])
    ramp.interpolation = 'EASE'
    points = [(0, .018), (.35, .025), (.65, .060), (.85, .16), (1, .32)]
    ramp.elements[0].position = 0
    ramp.elements[0].color = (.018, .018, .018, 1)
    ramp.elements[1].position = 1
    ramp.elements[1].color = (.32, .32, .32, 1)
    for position, value in points[1:-1]:
        ramp.elements.new(position).color = (value, value, value, 1)
    links.new(distance.outputs[0], blur.inputs['Fac'])
    links.new(blur.outputs['Color'], surface.inputs['Roughness'])
    links.new(blur.outputs['Color'], surface.inputs['Coat Roughness'])
    fade = nodes['Reflection opacity | 90 percent to invisible']
    fade.label = 'Restrained rim, clear middle, original fade endpoint'
    fade.inputs['From Min'].default_value = 3.5
    fade.inputs['From Max'].default_value = 13
    fade.inputs['To Min'].default_value = .40
    fade.inputs['To Max'].default_value = 1
    fade.interpolation_type = 'SMOOTHSTEP'
    bpy.data.objects['Atmosphere | subtle illuminated haze'].visible_glossy = False
    floor['Reflection'] = 'Polished black glass: restrained rim, readable facets, delayed blur and independent fade.'
    assert all([list(row) for row in scene.objects[name].matrix_world] == matrix
               for name, matrix in session['transforms'].items())
    assert scene.frame_current == session['frame']
    status('rendering_preview', filepath=bpy.data.filepath,
           geometry_and_camera_unchanged=True, fade_endpoint=13)
    scene.render.resolution_percentage = 60
    scene.cycles.samples = 48
    scene.cycles.adaptive_threshold = .025
    scene.render.filepath = '/private/tmp/badge-polished-floor-preview.png'
    try:
        bpy.ops.render.render(write_still=True)
    finally:
        scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = session['resolution']
        scene.cycles.samples = session['samples']
        scene.cycles.adaptive_threshold = session['threshold']
        scene.render.filepath = session['render_path']
    status('preview_ready', image='/private/tmp/badge-polished-floor-preview.png')
    area = bpy.context.area
    if area:
        area.type = 'IMAGE_EDITOR'
        picture = bpy.data.images.load('/private/tmp/badge-polished-floor-preview.png', check_existing=True)
        picture.reload()
        area.spaces.active.image = picture
        region = next(region for region in area.regions if region.type == 'WINDOW')
        with bpy.context.temp_override(area=area, region=region):
            bpy.ops.image.view_all(fit_view=True)

try:
    run()
except Exception:
    status('error', traceback=traceback.format_exc())
    raise
