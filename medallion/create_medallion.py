"""Build an editable, studio-lit recreation of the supplied silver medallion."""
import bpy
import bmesh
import math
import os
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for collection in list(bpy.data.collections):
    if collection.name != 'Collection':
        bpy.data.collections.remove(collection)
root = bpy.data.collections.get('Collection')
root.name = '01 | Medallion'
studio = bpy.data.collections.new('02 | Studio lighting')
bpy.context.scene.collection.children.link(studio)
reference_collection = bpy.data.collections.new('03 | Reference (hidden in render)')
bpy.context.scene.collection.children.link(reference_collection)

def material(name, color, metallic, roughness):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*color, 1)
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat, bsdf

silver, shader = material('Silver | circumferential brushed steel', (.36, .35, .33), 1, .30)
shader.inputs['Anisotropic'].default_value = .4
nodes, links = silver.node_tree.nodes, silver.node_tree.links
uv = nodes.new('ShaderNodeTexCoord')
scale = nodes.new('ShaderNodeVectorMath')
scale.operation = 'MULTIPLY'
scale.inputs[1].default_value = (55, 95, 1)
links.new(uv.outputs['UV'], scale.inputs[0])
grain = nodes.new('ShaderNodeTexNoise')
grain.inputs['Scale'].default_value = 1
grain.inputs['Detail'].default_value = 2
grain.inputs['Roughness'].default_value = .65
links.new(scale.outputs[0], grain.inputs['Vector'])
bump = nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = .20
bump.inputs['Distance'].default_value = .003
links.new(grain.outputs['Fac'], bump.inputs['Height'])
links.new(bump.outputs['Normal'], shader.inputs['Normal'])
ramp = nodes.new('ShaderNodeMapRange')
ramp.inputs['To Min'].default_value = .25
ramp.inputs['To Max'].default_value = .40
links.new(grain.outputs['Fac'], ramp.inputs['Value'])
links.new(ramp.outputs[0], shader.inputs['Roughness'])
steel_tone = nodes.new('ShaderNodeValToRGB')
steel_tone.color_ramp.elements[0].color = (.29,.28,.265,1)
steel_tone.color_ramp.elements[1].color = (.40,.39,.37,1)
links.new(grain.outputs['Fac'], steel_tone.inputs[0])
links.new(steel_tone.outputs['Color'], shader.inputs['Base Color'])
tangent = nodes.new('ShaderNodeTangent')
tangent.direction_type = 'UV_MAP'
tangent.uv_map = 'Machining UV'
links.new(tangent.outputs['Tangent'], shader.inputs['Tangent'])

polished, bsdf = material('Silver | polished cut edges', (.64, .62, .58), 1, .19)
dark_metal, bsdf = material('Recess | smoked nickel', (.07, .067, .060), 1, .27)
back_metal, bsdf = material('Back and edge | gunmetal', (.095, .09, .08), .95, .32)

leather, shader = material('Inset | finely textured charcoal', (.016, .017, .017), .05, .83)
nodes, links = leather.node_tree.nodes, leather.node_tree.links
tex = nodes.new('ShaderNodeTexCoord')
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 185
noise.inputs['Detail'].default_value = 3
noise.inputs['Roughness'].default_value = .7
links.new(tex.outputs['Generated'], noise.inputs['Vector'])
pores = nodes.new('ShaderNodeTexVoronoi')
pores.feature = 'DISTANCE_TO_EDGE'
pores.inputs['Scale'].default_value = 220
links.new(tex.outputs['Generated'], pores.inputs['Vector'])
micro = nodes.new('ShaderNodeBump')
micro.inputs['Strength'].default_value = .46
micro.inputs['Distance'].default_value = .022
links.new(pores.outputs['Distance'], micro.inputs['Height'])
bump = nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = .38
bump.inputs['Distance'].default_value = .014
links.new(noise.outputs['Fac'], bump.inputs['Height'])
links.new(micro.outputs['Normal'], bump.inputs['Normal'])
links.new(bump.outputs['Normal'], shader.inputs['Normal'])
colors = nodes.new('ShaderNodeValToRGB')
colors.color_ramp.elements[0].position = .18
colors.color_ramp.elements[0].color = (.0014, .0016, .0017, 1)
colors.color_ramp.elements[1].position = .83
colors.color_ramp.elements[1].color = (.0045, .0049, .0050, 1)
links.new(noise.outputs['Fac'], colors.inputs[0])
links.new(colors.outputs['Color'], shader.inputs['Base Color'])

emblem, shader = material('Emblem | satin silver facets', (.56, .54, .50), 1, .29)
shader.inputs['Anisotropic'].default_value = .18
nodes, links = emblem.node_tree.nodes, emblem.node_tree.links
tex = nodes.new('ShaderNodeTexCoord')
stretch = nodes.new('ShaderNodeVectorMath')
stretch.operation = 'MULTIPLY'
stretch.inputs[1].default_value = (190, 8, 110)
links.new(tex.outputs['Generated'], stretch.inputs[0])
grain = nodes.new('ShaderNodeTexNoise')
grain.inputs['Scale'].default_value = 3
grain.inputs['Detail'].default_value = 2
links.new(stretch.outputs[0], grain.inputs[0])
bump = nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = .13
bump.inputs['Distance'].default_value = .004
links.new(grain.outputs['Fac'], bump.inputs['Height'])
links.new(bump.outputs[0], shader.inputs['Normal'])

def lathe(name, profile, mat, segments=768):
    verts = [(r*math.cos(2*math.pi*i/segments), r*math.sin(2*math.pi*i/segments), z)
             for r, z in profile for i in range(segments)]
    count = len(profile)
    faces = []
    for j in range(count):
        for i in range(segments):
            faces.append((j*segments+i, j*segments+(i+1)%segments,
                         ((j+1)%count)*segments+(i+1)%segments, ((j+1)%count)*segments+i))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    root.objects.link(obj)
    uv = mesh.uv_layers.new(name='Machining UV')
    for polygon in mesh.polygons:
        polygon.use_smooth = True
        coords = [mesh.vertices[mesh.loops[loop].vertex_index].co for loop in polygon.loop_indices]
        angles = [(math.atan2(co.y,co.x)/(2*math.pi)) % 1 for co in coords]
        seam = max(angles)-min(angles) > .5
        for loop, co, u in zip(polygon.loop_indices, coords, angles):
            if seam and u < .5:
                u += 1
            uv.data[loop].uv = (u, (math.hypot(co.x,co.y)-2.6)/.5)
    return obj

lathe('Rim | broad brushed annulus', [
    (2.635,.145), (2.632,.185), (2.638,.211), (2.65,.226),
    (2.67,.232), (2.75,.247), (2.85,.263), (2.925,.265),
    (2.967,.255), (2.987,.252), (2.998,.239),
    (3.006,.218), (3.009,.191), (3.009,-.08), (3.002,-.104),
    (2.982,-.12), (2.65,-.12), (2.635,-.10)], silver)
lathe('Outer edge | hairline polished bevel', [
    (2.981,.251),(2.991,.255),(3.004,.244),(3.013,.222),
    (3.016,.20),(3.010,.191),(3.004,.214),(2.996,.236)], polished)
lathe('Inner channel | shadowed bevel', [
    (2.492,.038),(2.50,.070),(2.515,.091),(2.546,.11),
    (2.574,.118),(2.609,.151),(2.633,.186),(2.638,.201),
    (2.640,.151),(2.59,.068),(2.53,.025),(2.49,.018)], dark_metal)
lathe('Inner edge | fine silver reveal', [
    (2.502,.064),(2.510,.082),(2.52,.092),(2.532,.096),
    (2.539,.089),(2.535,.079),(2.522,.079),(2.513,.061)], polished)
lathe('Rim inner lip | narrow highlight', [
    (2.632,.187),(2.639,.205),(2.649,.219),(2.658,.224),
    (2.661,.220),(2.651,.213),(2.642,.197)], polished)

def cylinder(name, radius, depth, z, mat, bevel=0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=512, radius=radius, depth=depth, location=(0,0,z))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    if bevel:
        modifier = obj.modifiers.new('Soft machined edge', 'BEVEL')
        modifier.width = bevel
        modifier.segments = 3
        obj.modifiers.new('Weighted surface normals', 'WEIGHTED_NORMAL')
    return obj

cylinder('Body | solid backing', 3.002, .31, -.19, back_metal, .035)
cylinder('Inset | charcoal textured disk', 2.525, .17, -.046, leather, .015)

# Ten broad planar front facets. The top four preserve the folded chevron.
T = (0, 2.02, .36)
P = (0, .365, .98)
gradient = (.36-.98)/(2.02-.365)
def upper_z(x,y):
    return .98 + gradient*(y-.365) + .80*x
L = (-1.09,.055,.44)
A = (-.723,.104,upper_z(-.723,.104))
B = (-.387,.005,upper_z(-.387,.005))
C = (.387,.005,B[2])
D = (.723,.104,A[2])
R = (1.09,.055,.44)
S = (0,-2.05,.27)
vertices = [T,L,A,B,P,C,D,R,S]
faces = [(0,1,2),(0,2,3,4),(0,4,5,6),(0,6,7),
         (1,8,2),(2,8,3),(3,8,4),(4,8,5),(5,8,6),(6,8,7)]
# Close the back so the emblem is a real solid mesh.
vertices.extend([(0,2.02,.12),(-1.09,.055,.12),(0,-2.05,.12),(1.09,.055,.12)])
faces.extend([(0,9,10,1),(1,10,11,8),(8,11,12,7),(7,12,9,0),(9,12,11,10)])
mesh = bpy.data.meshes.new('Emblem | hand-built folded facets')
mesh.from_pydata(vertices, [], faces)
mesh.materials.append(emblem)
mesh.materials.append(polished)
facet_satin = emblem.copy()
facet_satin.name = 'Emblem | shaded outer facets'
facet_satin.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (.21,.20,.185,1)
mesh.materials.append(facet_satin)
mesh.update()
for i in (4,5,8,9):
    mesh.polygons[i].material_index = 2
hero = bpy.data.objects.new('Emblem | faceted compass spear', mesh)
root.objects.link(hero)
bpy.context.view_layer.objects.active = hero
hero.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
bevel = hero.modifiers.new('Fine glints along facet edges', 'BEVEL')
bevel.width = .006
bevel.segments = 2
bevel.affect = 'EDGES'
bevel.limit_method = 'ANGLE'
bevel.angle_limit = .045
bevel.material = 1
bevel.harden_normals = True
hero.modifiers.new('Keep broad facets planar', 'WEIGHTED_NORMAL')
hero['Design'] = 'Raised silver compass spear, rebuilt from the supplied reference.'
hero['Editable'] = 'Base mesh retains all ten front facets. Edge bevels remain non-destructive.'

def area(name, location, target, energy, size, size_y, color):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = 'RECTANGLE'
    data.size, data.size_y = size, size_y
    data.color = color
    obj = bpy.data.objects.new(name, data)
    studio.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    return obj

area('Key | tall left softbox', (-5.4,3.5,2.8), (0,0,.2), 350, 2.2, 4.0, (1,.98,.95))
area('Rim | right strip', (4.8,1.8,4.2), (0,0,0), 190, 1.0, 3.0, (.98,.99,1))
area('Top | silver crown', (-.3,5.1,3.5), (0,0,.2), 280, 2.1, 1.0, (1,.99,.98))
area('Bottom | narrow reflection', (-1.8,-4.7,4.6), (0,-.3,.2), 320, .8, 2.5, (1,.985,.96))
area('Fill | large frontal card', (0,.6,7.5), (0,0,0), 40, 3, 3, (1,1,1))

scene = bpy.context.scene
world = bpy.data.worlds.new('Black studio | invisible ambient reflection')
world.use_nodes = True
scene.world = world
nodes, links = world.node_tree.nodes, world.node_tree.links
nodes.clear()
output = nodes.new('ShaderNodeOutputWorld')
ambient = nodes.new('ShaderNodeBackground')
ambient.inputs['Color'].default_value = (.35,.35,.35,1)
ambient.inputs['Strength'].default_value = .2
black = nodes.new('ShaderNodeBackground')
black.inputs['Color'].default_value = (0,0,0,1)
path = nodes.new('ShaderNodeLightPath')
mix = nodes.new('ShaderNodeMixShader')
links.new(path.outputs['Is Camera Ray'], mix.inputs[0])
links.new(ambient.outputs[0], mix.inputs[1])
links.new(black.outputs[0], mix.inputs[2])
links.new(mix.outputs[0], output.inputs[0])

camera_data = bpy.data.cameras.new('Camera | reference front view')
camera = bpy.data.objects.new('Camera | reference front view', camera_data)
studio.objects.link(camera)
camera.location = (0,-.33,15)
camera.rotation_euler = (0,0,0)
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 8.42
camera.data.lens = 70
scene.camera = camera

reference_path = '/Users/antonioperedo/Downloads/ChatGPT Image Sep 16, 2026, 09_15_31 PM.png'
reference_image = bpy.data.images.load(reference_path, check_existing=True)
reference_image.pack()
reference = bpy.data.objects.new('Supplied reference | packed image', None)
reference.empty_display_type = 'IMAGE'
reference.data = reference_image
reference.empty_display_size = 8.42
reference.location = (9,-.39,0)
reference.hide_render = True
reference_collection.objects.link(reference)
reference_collection.hide_viewport = True

scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.cycles.adaptive_threshold = .012
scene.cycles.max_bounces = 8
scene.cycles.transparent_max_bounces = 4
scene.cycles.device = 'CPU'
print('RENDER_DEVICE: CPU', flush=True)
scene.render.resolution_x = 2048
scene.render.resolution_y = 2048
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '8'
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.render.film_transparent = False
scene.render.filepath = os.path.join(OUT, 'medallion.png')
scene['Reference'] = 'ChatGPT Image Sep 16, 2026, 09_15_31 PM.png (packed)'
scene['Contents'] = 'Editable solid geometry, procedural materials, five studio lights and front camera.'

bpy.ops.object.select_all(action='DESELECT')
hero.select_set(True)
bpy.context.view_layer.objects.active = hero
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type == 'VIEW_3D':
            a.spaces.active.region_3d.view_perspective = 'CAMERA'
            a.spaces.active.overlay.show_overlays = False
            a.spaces.active.shading.type = 'MATERIAL'
            a.spaces.active.shading.use_scene_lights = True
            a.spaces.active.shading.use_scene_world = True
            a.spaces.active.shading.studiolight_rotate_z = .4
            a.spaces.active.region_3d.view_camera_zoom = 10
mesh_count = 0
for obj in root.objects:
    if obj.type != 'MESH':
        continue
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    assert all(edge.is_manifold for edge in bm.edges), obj.name + ' has an open edge'
    bm.free()
    mesh_count += 1
print(f'GEOMETRY_VALIDATED: {mesh_count} closed editable meshes', flush=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'silver_medallion.blend'))
print('MODEL_SAVED', flush=True)
bpy.ops.render.render(write_still=True)
render_image = bpy.data.images.load(scene.render.filepath, check_existing=True)
render_image.name = 'Medallion | finished 2048px render'
render_image.pack()
for screen in bpy.data.screens:
    if screen.name == 'Rendering':
        for area in screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.spaces.active.image = render_image
scene.render.filepath = '//medallion.png'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'silver_medallion.blend'))
print('FINAL_RENDER_SAVED: 2048 x 2048 PNG, also packed inside the blend file', flush=True)
