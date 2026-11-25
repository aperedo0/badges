"""Run in the dedicated, empty Ruby Hourglass Blender scene."""
from pathlib import Path
import bpy, json, math
from mathutils import Vector, Quaternion
from bpy_extras.object_utils import world_to_camera_view

root = Path(__file__).resolve().parents[1]
directory=root/json.loads((root/'design.json').read_text())['candidate']
geometry=json.loads((directory/'geometry.json').read_text())
for name in ('Upper_Ruby','Lower_Ruby'):
    if name+'_Facing' in geometry:geometry[name]=geometry.pop(name+'_Facing')
scene = bpy.context.scene
assert scene.name == 'Ruby Hourglass Studio', 'Open the dedicated badge scene'
assert not bpy.data.filepath or Path(bpy.data.filepath).parent == root
studio = bpy.data.collections.new('Studio')
model = bpy.data.collections.new('Ruby Hourglass')
scene.collection.children.link(model)
scene.collection.children.link(studio)
for ob in list(scene.objects):
    if ob.name in ('Camera','Cube','Light'):
        for coll in list(ob.users_collection):
            coll.objects.unlink(ob)
refpath=Path.home()/'Downloads/Faceted ruby hourglass with side rails.png'
reference=bpy.data.images.load(str(refpath)); reference.name='Reference | Ruby hourglass'; reference.pack(); reference.use_fake_user=True

def create_material(name, color):
    mat=bpy.data.materials.new(name);mat.diffuse_color=(*color,1);mat.use_nodes=True
    return mat,mat.node_tree,mat.node_tree.nodes.get('Principled BSDF')

ruby,nt,bs=create_material('CrestGem_Ruby',(.45,.003,.012))
bs.inputs['Base Color'].default_value=(.96,.32,.36,1)
bs.inputs['Transmission Weight'].default_value=1.
bs.inputs['IOR'].default_value=1.77
bs.inputs['Roughness'].default_value=.012
absorb=nt.nodes.new('ShaderNodeVolumeAbsorption');absorb.location=(0,-260)
absorb.inputs['Color'].default_value=(.89,.012,.035,1);absorb.inputs['Density'].default_value=1.15
nt.links.new(absorb.outputs[0],nt.nodes.get('Material Output').inputs['Volume'])
bronze,nt,bs=create_material('Brushed Bronze',(.19,.115,.077))
bs.inputs['Base Color'].default_value=(.19,.115,.077,1)
bs.inputs['Metallic'].default_value=.88
bs.inputs['Anisotropic'].default_value=.23
brush=bpy.data.images.load(str(directory/'BronzeBrush.png'));brush.colorspace_settings.name='Non-Color';brush.pack()
node=nt.nodes.new('ShaderNodeTexImage');node.image=brush;node.location=(-300,150);nt.links.new(node.outputs['Color'],bs.inputs['Roughness'])

def axes(value):return (value[0],-value[2],value[1])
for name,obj in geometry.items():
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([axes(p) for p in obj['points']],[],obj['triangles']);mesh.update()
    ob=bpy.data.objects.new(name,mesh);model.objects.link(ob)
    ob.data.materials.append(bronze if 'uv' in obj else ruby)
    if 'uv' in obj:
        uvs=mesh.uv_layers.new(name='st')
        for poly in mesh.polygons:
            poly.use_smooth=True
            for i in poly.loop_indices:uvs.data[i].uv=obj['uv'][mesh.loops[i].vertex_index]
        mesh.normals_split_custom_set_from_vertices([axes(n) for n in obj['normals']])
    ob['construction']='Closed swept bronze rail' if 'uv' in obj else 'Independent closed convex ruby'
world=bpy.data.worlds.new('Jewelry photography studio');world.use_nodes=True;scene.world=world
wn=world.node_tree.nodes;wl=world.node_tree.links
hdri=bpy.data.images.load(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/studiolights/world/studio.exr'))
hdri.pack();env=wn.new('ShaderNodeTexEnvironment');env.image=hdri;env.location=(-400,0)
bg=wn.get('Background');wl.new(env.outputs['Color'],bg.inputs['Color']);bg.inputs['Strength'].default_value=.85
def light(name,position,power,color,size,height):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='RECTANGLE';data.size=size;data.size_y=height;data.color=color
    ob=bpy.data.objects.new(name,data);studio.objects.link(ob);ob.location=position;ob.rotation_euler=(Vector((0,0,.2))-ob.location).to_track_quat('-Z','Y').to_euler()
light('High softbox',(-3.7,-4.4,5.6),290,(1,.88,.79),2.2,4.)
light('Right ribbon',(4.8,-2.8,2.8),215,(1,.94,.91),1.15,5.)
light('Rear strip',(-2.6,3.7,1.1),540,(1,.81,.67),1.5,4.5)
light('Cool fill',(2.3,3.6,4.3),350,(.76,.86,1),3.2,3.6)
cam=bpy.data.objects.new('Badge camera',bpy.data.cameras.new('Badge camera'));studio.objects.link(cam);scene.camera=cam
center=Vector((0,0,.27));cam.location=(0,-23,1.8);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=6.26
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.cycles.max_bounces=18;scene.cycles.transmission_bounces=16;scene.cycles.glossy_bounces=10
scene.render.resolution_x=780;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.film_transparent=True
scene.cycles.film_transparent_glass=False
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
scene.render.filepath='//candidate01/studio_front.png'
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        space=area.spaces.active;space.region_3d.view_perspective='CAMERA';space.overlay.show_overlays=False;space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.shading.light='STUDIO'
    elif area.type=='PROPERTIES':
        area.type='IMAGE_EDITOR';area.spaces.active.image=reference
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Ruby Hourglass.blend'),compress=True)
