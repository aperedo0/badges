"""Widen the beam's lower end and add separate reflection blur and fade gradients."""
import bpy
import math
import os
import sys
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))
PREVIEW = '--preview' in sys.argv
scene = bpy.context.scene
scene.frame_set(1)
bpy.context.view_layer.update()
floor = bpy.data.objects['Floor | polished black with softened reflections']
floor_y = floor.location.y

# Remove the visible floor pools and their now-unused data in this revision.
removed = []
for obj in list(scene.objects):
    if obj.name.startswith('Floor light |'):
        removed.append(obj.name)
        data = obj.data
        kind = obj.type
        bpy.data.objects.remove(obj,do_unlink=True)
        if data and data.users == 0:
            if kind == 'MESH':
                bpy.data.meshes.remove(data)
            elif kind == 'LIGHT':
                bpy.data.lights.remove(data)
glow = bpy.data.materials.get('Floor lights | soft elliptical glow')
if glow and glow.users == 0:
    bpy.data.materials.remove(glow)

fog = bpy.data.materials['Atmosphere | cool studio haze']
nodes = fog.node_tree.nodes
width = next(node for node in nodes if node.type == 'MATH' and node.operation == 'DIVIDE'
             and node.inputs[0].links and node.inputs[0].links[0].from_socket.name == 'X')
minimum = width.inputs[1].links[0].from_node
radius = minimum.inputs[0].links[0].from_node
height = radius.inputs[0].links[0].from_node
old_slope = radius.inputs[1].default_value
old_apex = height.inputs[0].default_value

# Anchor the beam at the upper edge of this camera's frame. Its lower width
# grows by 35 percent while the visible upper width remains unchanged.
camera = scene.camera
frame = sorted(camera.data.view_frame(scene=scene),key=lambda point: point.y)
top_center = (frame[-1]+frame[-2])*.5
ray = camera.matrix_world @ top_center-camera.matrix_world.translation
beam_depth = bpy.data.objects['Overhead | soft visible shaft'].location.z
t = (beam_depth-camera.location.z)/ray.z
top_y = camera.location.y+t*ray.y
top_radius = old_slope*(old_apex-top_y)
bottom_radius = old_slope*(old_apex-floor_y)
new_slope = (bottom_radius*1.35-top_radius)/(top_y-floor_y)
new_apex = top_y+top_radius/new_slope
height.inputs[0].default_value = new_apex
height.label = 'Beam apex | upper visible width preserved'
radius.inputs[1].default_value = new_slope
radius.label = 'Beam fan | 35 percent wider at the floor'

spot = bpy.data.objects['Overhead | soft visible shaft']
old_half_angle = spot.data.spot_size*.5
new_half_angle = math.atan(math.tan(old_half_angle)*new_slope/old_slope)
spot.data.energy *= ((1-math.cos(new_half_angle))/(1-math.cos(old_half_angle))
                     *((new_apex-top_y)/(old_apex-top_y))**2)
spot.data.spot_size = 2*new_half_angle
spot.location.y = new_apex
spot.rotation_euler = (Vector((0,floor_y,-1.2))-spot.location).to_track_quat('-Z','Y').to_euler()

material = floor.data.materials[0]
nodes,links = material.node_tree.nodes,material.node_tree.links
surface = next(node for node in nodes if node.type == 'BSDF_PRINCIPLED')
roughness = surface.inputs['Roughness'].links[0].from_node
roughness.name = 'Reflection blur | crisp contact to soft foreground'
roughness.label = 'About 90 percent clear at contact, then increasingly blurred'
roughness.interpolation_type = 'SMOOTHSTEP'
roughness.inputs['From Min'].default_value = 0
roughness.inputs['From Max'].default_value = 10
roughness.inputs['To Min'].default_value = .025
roughness.inputs['To Max'].default_value = .65
roughness.clamp = True
links.new(roughness.outputs[0],surface.inputs['Coat Roughness'])

fade = next(node for node in nodes if node.type == 'MAP_RANGE' and node != roughness
            and node.inputs['From Min'].default_value >= 0)
fade.name = 'Reflection opacity | 90 percent to invisible'
fade.label = 'Separate smooth opacity gradient'
fade.interpolation_type = 'SMOOTHSTEP'
fade.inputs['From Min'].default_value = 0
fade.inputs['From Max'].default_value = 13
fade.inputs['To Min'].default_value = .10
fade.inputs['To Max'].default_value = 1
fade.clamp = True
floor['Reflection'] = 'Crisp near the badge, increasingly blurred and transparent toward the foreground.'
scene['Stage refinement'] = 'Same beam width at frame top, 35 percent wider at floor; no floor light pools.'

assert abs(new_slope*(new_apex-top_y)-top_radius) < .0001
assert abs(new_slope*(new_apex-floor_y)/bottom_radius-1.35) < .0001
assert not any(obj.name.startswith('Floor light |') for obj in scene.objects)
rig = bpy.data.objects['Turntable | one slow 360 degree spin']
scene.frame_set(360)
assert abs(rig.rotation_euler.y-math.tau) < .0001
scene.frame_set(1)
print(f'BEAM_VERIFIED: top radius {top_radius:.3f} unchanged; floor radius {bottom_radius:.3f} -> {bottom_radius*1.35:.3f}',flush=True)
print(f'FLOOR_VERIFIED: {len(removed)} light pools removed; blur and opacity have independent smooth gradients',flush=True)

scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 48 if PREVIEW else 96
scene.cycles.use_denoising = True
scene.cycles.adaptive_threshold = .03 if PREVIEW else .018
scene.render.resolution_x = 720 if PREVIEW else 1080
scene.render.resolution_y = 960 if PREVIEW else 1440
scene.render.resolution_percentage = 100
scene.render.filepath = ('/private/tmp/medallion-stage-refined-preview.png' if PREVIEW else
                        os.path.join(OUT,'medallion_stage_refined.png'))
bpy.ops.render.render(write_still=True)
if not PREVIEW:
    reference = bpy.data.images.get('Reference | reflective floor and overhead beam')
    if reference is None:
        reference = bpy.data.images.load('/var/folders/gl/mpj0czg96klfknfbtdxsw0400000gn/T/codex-clipboard-mNQofF.png')
        reference.name = 'Reference | reflective floor and overhead beam'
    reference.use_fake_user = True
    reference.pack()
    old = bpy.data.images.get('Medallion | reflective stage render')
    if old:
        bpy.data.images.remove(old)
    finished = bpy.data.images.load(scene.render.filepath,check_existing=True)
    finished.name = 'Medallion | refined beam and reflection'
    finished.use_fake_user = True
    finished.pack()
    for screen in bpy.data.screens:
        if screen.name == 'Rendering':
            for area in screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    area.spaces.active.image = finished
    scene.render.filepath = '//medallion_stage_refined.png'
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'silver_medallion_stage_refined.blend'))
    print('REFINED_STAGE_SAVED: 1080 x 1440 render packed; original full-turn animation preserved',flush=True)
