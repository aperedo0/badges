"""Correct physical floor contact and shorten the reflection in the live scene."""
import bpy
import json
import traceback

STATUS = '/private/tmp/badge-contact-status.json'

def status(stage, **details):
    with open(STATUS, 'w') as handle:
        json.dump(dict(stage=stage, **details), handle, indent=2)

try:
    scene = bpy.context.scene
    floor = bpy.data.objects['Floor | polished black with softened reflections']
    casing = bpy.data.objects['Casing | smooth rounded outer edge']
    bottom = min((casing.matrix_world @ vertex.co).y for vertex in casing.data.vertices)
    # Seat the dark rounded underside slightly into the floor so the visible
    # silver front edge meets its reflection instead of reading as a black gap.
    seating_depth = .12
    floor.location.y = bottom + seating_depth
    bpy.context.view_layer.update()
    nodes = floor.data.materials[0].node_tree.nodes
    links = floor.data.materials[0].node_tree.links
    # Compress the reflected height while retaining the complete reflected shape.
    # The half-vector between the view direction and the adjusted reflected ray
    # defines the floor's shading normal. Geometry remains exactly at contact.
    geometry = next(node for node in nodes if node.type == 'NEW_GEOMETRY')
    def vector_node(name, operation):
        node = nodes.get(name) or nodes.new('ShaderNodeVectorMath')
        node.name = name
        node.operation = operation
        return node
    direction = vector_node('Reflection | one-third height', 'MULTIPLY')
    direction.inputs[1].default_value = (-1, 3, -1)
    links.new(geometry.outputs['Incoming'], direction.inputs[0])
    ray = vector_node('Reflection | normalized outgoing ray', 'NORMALIZE')
    links.new(direction.outputs[0], ray.inputs[0])
    half = vector_node('Reflection | surface half vector', 'ADD')
    links.new(geometry.outputs['Incoming'], half.inputs[0])
    links.new(ray.outputs[0], half.inputs[1])
    normal = vector_node('Reflection | compact floor normal', 'NORMALIZE')
    links.new(half.outputs[0], normal.inputs[0])
    surface = next(node for node in nodes if node.type == 'BSDF_PRINCIPLED')
    links.new(normal.outputs[0], surface.inputs['Normal'])
    surface.inputs['IOR'].default_value = 2.0
    # Express distance in the former reflection's coordinates so the established
    # blur and opacity profiles compress with the image rather than cropping it.
    xyz = next(node for node in nodes if node.type == 'SEPXYZ')
    camera_z = scene.camera.matrix_world.translation.z
    def math_node(name, operation, value):
        node = nodes.get(name) or nodes.new('ShaderNodeMath')
        node.name = name
        node.operation = operation
        node.inputs[1].default_value = value
        return node
    numerator = math_node('Reflection | scaled distance numerator', 'MULTIPLY', 3*camera_z)
    denominator_scale = math_node('Reflection | distance denominator scale', 'MULTIPLY', 2)
    denominator = math_node('Reflection | distance denominator', 'ADD', camera_z)
    restored = math_node('Reflection | original distance coordinates', 'DIVIDE', 1)
    links.new(xyz.outputs['Z'], numerator.inputs[0])
    links.new(xyz.outputs['Z'], denominator_scale.inputs[0])
    links.new(denominator_scale.outputs[0], denominator.inputs[0])
    links.new(numerator.outputs[0], restored.inputs[0])
    links.new(denominator.outputs[0], restored.inputs[1])
    distance = nodes['Reflection blur | crisp contact to soft foreground']
    distance.inputs['From Min'].default_value = 0
    distance.inputs['From Max'].default_value = 13
    links.new(restored.outputs[0], distance.inputs['Value'])
    distance.label = 'Compact reflection: clear contact to soft tail'
    fade = nodes['Reflection opacity | 90 percent to invisible']
    fade.inputs['From Min'].default_value = 3.5
    fade.inputs['From Max'].default_value = 13
    links.new(restored.outputs[0], fade.inputs['Value'])
    fade.label = 'Short reflection: fade completely near the badge'
    floor['Reflection'] = 'Compact polished reflection, about one-third the former visible length.'
    scene['Floor contact'] = 'Rounded underside seated into the floor; visible silver edge meets its reflection.'
    assert abs(floor.location.y-bottom-seating_depth) < .00001
    saved = (scene.render.resolution_percentage, scene.cycles.samples,
             scene.cycles.adaptive_threshold, scene.render.filepath)
    status('rendering_preview', physical_gap=max(0, bottom-floor.location.y), seating_depth=seating_depth,
           floor_height=floor.location.y, reflection_height_scale=1/3)
    scene.render.resolution_percentage = 60
    scene.cycles.samples = 48
    scene.cycles.adaptive_threshold = .025
    scene.render.filepath = '/private/tmp/badge-contact-preview.png'
    try:
        bpy.ops.render.render(write_still=True)
    finally:
        scene.render.resolution_percentage, scene.cycles.samples, scene.cycles.adaptive_threshold, scene.render.filepath = saved
    status('preview_ready', image='/private/tmp/badge-contact-preview.png', physical_gap=max(0, bottom-floor.location.y), seating_depth=seating_depth)
except Exception:
    status('error', traceback=traceback.format_exc())
    raise
