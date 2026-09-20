"""Replace the stepped outer casing with one smoothly rounded solid shell."""
import bpy
import bmesh
import math
import os
import shutil
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
PREVIEWS = '/private/tmp/medallion-smooth-edge-frames'
os.makedirs(PREVIEWS, exist_ok=True)
scene = bpy.context.scene
scene.frame_set(1)
collection = bpy.data.collections['01 | Medallion']
rig = bpy.data.objects['Turntable | one slow 360 degree spin']
brushed = bpy.data.materials['Silver | circumferential brushed steel']
back = bpy.data.materials['Back and edge | gunmetal']

satin = bpy.data.materials.new('Outer edge | smooth satin silver')
satin.use_nodes = True
satin.diffuse_color = (.36,.35,.33,1)
shader = satin.node_tree.nodes.get('Principled BSDF')
shader.inputs['Base Color'].default_value = (.36,.35,.33,1)
shader.inputs['Metallic'].default_value = 1
shader.inputs['Roughness'].default_value = .27

# Radial section of a single closed casing. The two zero-radius points
# become triangle fans, rather than collapsed rings of duplicate vertices.
profile = [(0,-.135),(2.59,-.135),(2.62,-.115),(2.635,.145),
           (2.632,.185),(2.638,.211),(2.65,.226)]
materials = [2,2,2,0,0,0]
def append(point, material_index):
    profile.append(point)
    materials.append(material_index)

# A tangent-continuous front band flows into a quarter-circle corner.
points = [(2.65,.226),(2.71,.252),(2.83,.26),(2.90,.26)]
for step in range(1,25):
    t = step/24
    weights = [(1-t)**3,3*(1-t)**2*t,3*(1-t)*t*t,t**3]
    append(tuple(sum(w*p[axis] for w,p in zip(weights,points)) for axis in (0,1)),0)
for step in range(1,25):
    angle = math.pi/2*(1-step/24)
    append((2.90+.115*math.cos(angle),.145+.115*math.sin(angle)),1)
append((3.015,-.230),1)
for step in range(1,25):
    angle = -math.pi/2*step/24
    append((2.90+.115*math.cos(angle),-.230+.115*math.sin(angle)),1)
append((2.75,-.345),2)
append((0,-.345),2)

segments = 1024
vertices, rings = [], []
for radius,z in profile:
    if radius == 0:
        rings.append([len(vertices)])
        vertices.append((0,0,z))
    else:
        rings.append(list(range(len(vertices),len(vertices)+segments)))
        vertices.extend((radius*math.cos(math.tau*i/segments),
                         radius*math.sin(math.tau*i/segments),z) for i in range(segments))
faces, face_materials = [], []
for j in range(len(rings)-1):
    a,b = rings[j],rings[j+1]
    for i in range(segments):
        k = (i+1)%segments
        if len(a) == 1:
            face = (a[0],b[i],b[k])
        elif len(b) == 1:
            face = (a[i],b[0],a[k])
        else:
            face = (a[i],b[i],b[k],a[k])
        faces.append(face)
        face_materials.append(materials[j])

mesh = bpy.data.meshes.new('Casing | continuous rounded radial profile')
mesh.from_pydata(vertices,[],faces)
mesh.materials.clear()
for mat in (brushed,satin,back):
    mesh.materials.append(mat)
for polygon,material_index in zip(mesh.polygons,face_materials):
    polygon.material_index = material_index
    polygon.use_smooth = True
bm = bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
assert all(edge.is_manifold for edge in bm.edges), 'Casing must be a closed solid.'
bm.to_mesh(mesh)
bm.free()
mesh.update()
uv = mesh.uv_layers.new(name='Machining UV')
for polygon in mesh.polygons:
    coords = [mesh.vertices[mesh.loops[i].vertex_index].co for i in polygon.loop_indices]
    angles = [(math.atan2(co.y,co.x)/math.tau)%1 for co in coords]
    seam = max(angles)-min(angles) > .5
    for loop,co,u in zip(polygon.loop_indices,coords,angles):
        if seam and u < .5:
            u += 1
        uv.data[loop].uv = (u,(math.hypot(co.x,co.y)-2.6)/.5)

casing = bpy.data.objects.new('Casing | smooth rounded outer edge',mesh)
collection.objects.link(casing)
casing.parent = rig
casing['Edge'] = 'Continuous rounded front and back shoulders, with a smooth satin sidewall.'
for name in ('Rim | broad brushed annulus','Outer edge | hairline polished bevel','Body | solid backing'):
    bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)

scene.eevee.taa_render_samples = 32
scene.frame_set(1)
scene['Edge revision'] = 'One continuous casing replaces the stepped rim and backing join.'
scene.render.filepath = '//smooth_edge_frames/frame_'
bpy.ops.object.select_all(action='DESELECT')
casing.select_set(True)
bpy.context.view_layer.objects.active = casing
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'silver_medallion_smooth_edge.blend'))
print('EDGE_VALIDATED: closed casing, 1024 radial segments, 24 segments per rounded shoulder',flush=True)
for frame in (1,46,91):
    scene.frame_set(frame)
    scene.render.filepath = os.path.join(PREVIEWS,f'preview_{frame:04d}.png')
    bpy.ops.render.render(write_still=True)
print('EDGE_PREVIEWS_RENDERED',flush=True)
scene.frame_set(1)
preview_path = os.path.join(OUT,'medallion_smooth_edge.png')
shutil.copyfile(os.path.join(PREVIEWS,'preview_0001.png'),preview_path)
old_render = bpy.data.images.get('Medallion | finished 2048px render')
if old_render:
    bpy.data.images.remove(old_render)
finished = bpy.data.images.load(preview_path,check_existing=True)
finished.name = 'Medallion | smooth edge render'
finished.pack()
for screen in bpy.data.screens:
    if screen.name == 'Rendering':
        for area in screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.spaces.active.image = finished
scene.render.filepath = '//smooth_edge_frames/frame_'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'silver_medallion_smooth_edge.blend'))
if '--render' in sys.argv:
    scene.render.filepath = os.path.join(PREVIEWS,'frame_')
    bpy.ops.render.render(animation=True)
    print('SMOOTH_EDGE_ANIMATION_RENDERED: 360 frames',flush=True)
