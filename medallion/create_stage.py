"""Add the reflective black floor and atmospheric studio from the new reference."""
import bpy
import math
import os
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))
scene = bpy.context.scene
scene.frame_set(1)
stage = bpy.data.collections.new('04 | Reflective floor and atmosphere')
scene.collection.children.link(stage)
lighting = bpy.data.collections.new('05 | Stage lights')
scene.collection.children.link(lighting)

def move_to(obj, collection):
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)

def aim(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

def light(name, kind, position, energy, color, target=None):
    data = bpy.data.lights.new(name,kind)
    data.energy = energy
    data.color = color
    obj = bpy.data.objects.new(name,data)
    lighting.objects.link(obj)
    obj.location = position
    if target is not None:
        aim(obj,target)
    return obj

floor_y = -3.015
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,floor_y,0),rotation=(-math.pi/2,0,0))
floor = bpy.context.object
floor.name = 'Floor | polished black with softened reflections'
move_to(floor,stage)
mat = bpy.data.materials.new('Floor | black reflective finish')
mat.use_nodes = True
nodes,links = mat.node_tree.nodes,mat.node_tree.links
bsdf = nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (.006,.008,.012,1)
bsdf.inputs['Metallic'].default_value = .45
bsdf.inputs['Roughness'].default_value = .24
bsdf.inputs['Coat Weight'].default_value = .35
bsdf.inputs['Coat Roughness'].default_value = .16
position = nodes.new('ShaderNodeNewGeometry')
xyz = nodes.new('ShaderNodeSeparateXYZ')
links.new(position.outputs['Position'],xyz.inputs[0])
rough = nodes.new('ShaderNodeMapRange')
rough.clamp = True
rough.inputs['From Min'].default_value = .2
rough.inputs['From Max'].default_value = 18
rough.inputs['To Min'].default_value = .14
rough.inputs['To Max'].default_value = .50
links.new(xyz.outputs['Z'],rough.inputs['Value'])
links.new(rough.outputs[0],bsdf.inputs['Roughness'])
near_fade = nodes.new('ShaderNodeMapRange')
near_fade.clamp = True
near_fade.interpolation_type = 'SMOOTHSTEP'
near_fade.inputs['From Min'].default_value = 2.5
near_fade.inputs['From Max'].default_value = 10.5
links.new(xyz.outputs['Z'],near_fade.inputs['Value'])
far_fade = nodes.new('ShaderNodeMapRange')
far_fade.clamp = True
far_fade.interpolation_type = 'SMOOTHSTEP'
far_fade.inputs['From Min'].default_value = -5
far_fade.inputs['From Max'].default_value = -1
far_fade.inputs['To Min'].default_value = 1
far_fade.inputs['To Max'].default_value = 0
links.new(xyz.outputs['Z'],far_fade.inputs['Value'])
fade = nodes.new('ShaderNodeMath')
fade.operation = 'MAXIMUM'
links.new(near_fade.outputs[0],fade.inputs[0])
links.new(far_fade.outputs[0],fade.inputs[1])
black = nodes.new('ShaderNodeBsdfDiffuse')
black.inputs['Color'].default_value = (0,0,0,1)
blend = nodes.new('ShaderNodeMixShader')
links.new(fade.outputs[0],blend.inputs[0])
links.new(bsdf.outputs[0],blend.inputs[1])
links.new(black.outputs[0],blend.inputs[2])
links.new(blend.outputs[0],nodes.get('Material Output').inputs['Surface'])
floor.data.materials.append(mat)

# A bounded haze volume keeps the studio background black outside the beam.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,4,-.9))
haze = bpy.context.object
haze.name = 'Atmosphere | subtle illuminated haze'
haze.dimensions = (16,17,6)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
move_to(haze,stage)
fog = bpy.data.materials.new('Atmosphere | cool studio haze')
fog.use_nodes = True
nodes,links = fog.node_tree.nodes,fog.node_tree.links
nodes.clear()
output = nodes.new('ShaderNodeOutputMaterial')
scatter = nodes.new('ShaderNodeVolumeScatter')
scatter.inputs['Color'].default_value = (.70,.78,.94,1)
scatter.inputs['Density'].default_value = .020
scatter.inputs['Anisotropy'].default_value = .20
links.new(scatter.outputs[0],output.inputs['Volume'])
position = nodes.new('ShaderNodeNewGeometry')
xyz = nodes.new('ShaderNodeSeparateXYZ')
links.new(position.outputs['Position'],xyz.inputs[0])
height = nodes.new('ShaderNodeMath')
height.operation = 'SUBTRACT'
height.inputs[0].default_value = 12
links.new(xyz.outputs['Y'],height.inputs[1])
radius = nodes.new('ShaderNodeMath')
radius.operation = 'MULTIPLY'
radius.inputs[1].default_value = .23
links.new(height.outputs[0],radius.inputs[0])
minimum = nodes.new('ShaderNodeMath')
minimum.operation = 'MAXIMUM'
minimum.inputs[1].default_value = .2
links.new(radius.outputs[0],minimum.inputs[0])
width = nodes.new('ShaderNodeMath')
width.operation = 'DIVIDE'
links.new(xyz.outputs['X'],width.inputs[0])
links.new(minimum.outputs[0],width.inputs[1])
depth = nodes.new('ShaderNodeMath')
depth.operation = 'ADD'
depth.inputs[1].default_value = 1.8
links.new(xyz.outputs['Z'],depth.inputs[0])
depth_scale = nodes.new('ShaderNodeMath')
depth_scale.operation = 'DIVIDE'
depth_scale.inputs[1].default_value = .9
links.new(depth.outputs[0],depth_scale.inputs[0])
gaussians = []
for source in (width,depth_scale):
    square = nodes.new('ShaderNodeMath')
    square.operation = 'MULTIPLY'
    links.new(source.outputs[0],square.inputs[0])
    links.new(source.outputs[0],square.inputs[1])
    negate = nodes.new('ShaderNodeMath')
    negate.operation = 'MULTIPLY'
    negate.inputs[1].default_value = -2
    links.new(square.outputs[0],negate.inputs[0])
    gaussian = nodes.new('ShaderNodeMath')
    gaussian.operation = 'EXPONENT'
    links.new(negate.outputs[0],gaussian.inputs[0])
    gaussians.append(gaussian)
shape = nodes.new('ShaderNodeMath')
shape.operation = 'MULTIPLY'
links.new(gaussians[0].outputs[0],shape.inputs[0])
links.new(gaussians[1].outputs[0],shape.inputs[1])
density = nodes.new('ShaderNodeMath')
density.operation = 'MULTIPLY'
density.inputs[1].default_value = .06
links.new(shape.outputs[0],density.inputs[0])
links.new(density.outputs[0],scatter.inputs['Density'])
haze.data.materials.append(fog)
haze.display_type = 'WIRE'

spot = light('Overhead | soft visible shaft','SPOT',(0,12,-1.8),6500,(.76,.84,1),
             (0,floor_y,-1.2))
spot.data.spot_size = math.radians(28)
spot.data.spot_blend = .75
spot.data.shadow_soft_size = .25

glow = bpy.data.materials.new('Floor lights | soft elliptical glow')
glow.use_nodes = True
glow.surface_render_method = 'BLENDED'
nodes,links = glow.node_tree.nodes,glow.node_tree.links
nodes.clear()
output = nodes.new('ShaderNodeOutputMaterial')
uv = nodes.new('ShaderNodeTexCoord')
center = nodes.new('ShaderNodeVectorMath')
center.operation = 'SUBTRACT'
center.inputs[1].default_value = (.5,.5,0)
links.new(uv.outputs['UV'],center.inputs[0])
length = nodes.new('ShaderNodeVectorMath')
length.operation = 'DOT_PRODUCT'
links.new(center.outputs[0],length.inputs[0])
links.new(center.outputs[0],length.inputs[1])
falloff = nodes.new('ShaderNodeMath')
falloff.operation = 'MULTIPLY'
falloff.inputs[1].default_value = -36
links.new(length.outputs['Value'],falloff.inputs[0])
exp = nodes.new('ShaderNodeMath')
exp.operation = 'EXPONENT'
links.new(falloff.outputs[0],exp.inputs[0])
transparent = nodes.new('ShaderNodeBsdfTransparent')
emission = nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value = (.67,.79,1,1)
emission.inputs['Strength'].default_value = 24
mix = nodes.new('ShaderNodeMixShader')
links.new(exp.outputs[0],mix.inputs[0])
links.new(transparent.outputs[0],mix.inputs[1])
links.new(emission.outputs[0],mix.inputs[2])
links.new(mix.outputs[0],output.inputs['Surface'])
for x,label in ((-3.45,'left'),(3.45,'right')):
    bpy.ops.mesh.primitive_plane_add(size=1,location=(x,floor_y+.007,-1.3),rotation=(-math.pi/2,0,0))
    pool = bpy.context.object
    pool.name = 'Floor light | '+label+' soft pool'
    pool.scale = (2.2,1.8,1)
    pool.data.materials.append(glow)
    move_to(pool,lighting)

# Lift the existing lower studio light above the new floor.
low = bpy.data.objects['Bottom | narrow reflection']
low.location = (-1.8,-2.1,4.6)
low.data.energy = 230
low.data.size_y = 1.8
aim(low,(0,-.3,.2))
bpy.data.objects['Key | tall left softbox'].data.energy = 450
bpy.data.objects['Rim | right strip'].data.energy = 260
bpy.data.objects['Top | silver crown'].data.energy = 430

camera = scene.camera
camera.data.type = 'PERSP'
camera.data.sensor_fit = 'HORIZONTAL'
camera.data.sensor_width = 36
camera.data.lens = 75
camera.location = (0,1.8,23)
aim(camera,(0,-.55,0))
camera.rotation_euler = (-math.atan2(2.35,23),0,0)
for node in scene.world.node_tree.nodes:
    if node.type == 'BACKGROUND' and node.inputs['Color'].default_value[0] > 0:
        node.inputs['Strength'].default_value = .025
for obj in scene.objects:
    if obj.type == 'LIGHT' and hasattr(obj.data,'volume_factor'):
        obj.data.volume_factor = 1 if obj == spot else (.05 if obj.name.startswith('Floor light') else 0)
scene.render.resolution_x = 1080
scene.render.resolution_y = 1440
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = 32
scene.eevee.volumetric_samples = 48
scene.eevee.volumetric_tile_size = '8'
scene.eevee.use_volumetric_shadows = True
scene.render.film_transparent = False
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 96
scene.cycles.use_denoising = True
scene.cycles.adaptive_threshold = .018

# Blender 5.2 uses a compositor node group as the scene output.
compositor = bpy.data.node_groups.new('Stage | soft photographic bloom','CompositorNodeTree')
compositor.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
scene.compositing_node_group = compositor
nodes,links = compositor.nodes,compositor.links
render = nodes.new('CompositorNodeRLayers')
render.scene = scene
bloom = nodes.new('CompositorNodeGlare')
for value in ('FOG_GLOW','Fog Glow'):
    try:
        bloom.inputs['Type'].default_value = value
        break
    except (TypeError,ValueError):
        pass
bloom.inputs['Threshold'].default_value = 1.5
bloom.inputs['Strength'].default_value = .45
bloom.inputs['Size'].default_value = .6
output = nodes.new('NodeGroupOutput')
links.new(render.outputs['Image'],bloom.inputs['Image'])
links.new(bloom.outputs['Image'],output.inputs['Image'])
print('BLOOM_TYPE:',bloom.inputs['Type'].default_value,flush=True)

reference_path = '/var/folders/gl/mpj0czg96klfknfbtdxsw0400000gn/T/codex-clipboard-mNQofF.png'
reference = bpy.data.images.load(reference_path,check_existing=True)
reference.name = 'Reference | reflective floor and overhead beam'
reference.use_fake_user = True
reference.pack()
scene['Stage reference'] = 'Dark reflective floor, overhead beam and two low cool light pools.'
scene['Floor contact'] = 'Floor at Y = -3.015, matching the rounded casing radius.'
scene.render.filepath = os.path.join(OUT,'medallion_stage.png')
shell = bpy.data.objects['Casing | smooth rounded outer edge']
bottom = min((shell.matrix_world @ vertex.co).y for vertex in shell.data.vertices)
assert abs(bottom-floor_y) < .0001, 'The badge must touch the floor.'
rig = bpy.data.objects['Turntable | one slow 360 degree spin']
scene.frame_set(360)
assert abs(rig.rotation_euler.y-math.tau) < .0001
scene.frame_set(1)
assert abs(rig.rotation_euler.y) < .0001
print('STAGE_VALIDATED: badge touches floor; original 360-frame full turn preserved',flush=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'silver_medallion_stage.blend'))
bpy.ops.render.render(write_still=True)
old_render = bpy.data.images.get('Medallion | smooth edge render')
if old_render:
    bpy.data.images.remove(old_render)
finished = bpy.data.images.load(scene.render.filepath,check_existing=True)
finished.name = 'Medallion | reflective stage render'
finished.pack()
for screen in bpy.data.screens:
    if screen.name == 'Rendering':
        for area in screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.spaces.active.image = finished
if bpy.context.window and bpy.data.workspaces.get('Rendering'):
    bpy.context.window.workspace = bpy.data.workspaces['Rendering']
scene.render.filepath = '//medallion_stage.png'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'silver_medallion_stage.blend'))
print('STAGE_RENDERED: 1080 x 1440 image saved and packed into the Blender scene',flush=True)
