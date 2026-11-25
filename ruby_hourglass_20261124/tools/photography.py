"""Light the cut from a large translucent tent and narrow strip reflectors."""
import bpy, math, numpy as np
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).parent
scene=bpy.context.scene
w,h=512,256
u=(np.arange(w)+.5)/w;v=(np.arange(h)+.5)/h
lon,lat=np.meshgrid(2*np.pi*(.5-u),np.pi*(v-.5))
d=np.stack([np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)],axis=-1)
def normalize(a):return a/np.linalg.norm(a)
def gaussian(center,spread):return np.exp(-(1.-d@normalize(np.asarray(center)))/spread**2)
field=np.ones((h,w,3))*.30
for direction,spread,power,tint in [
    ((1,.35,.55),.36,4.8,(1,.86,.76)),((-.72,.12,.65),.45,4.2,(1,.96,.92)),
    ((.15,.7,-.15),.31,2.3,(1,.76,.67)),((-.4,-.72,-.25),.45,.9,(.92,.94,1)),
    ((.15,.10,1),.58,.8,(1,.94,.88))]:
    field+=gaussian(direction,spread)[:,:,None]*power*np.array(tint)
im=bpy.data.images.new('Ruby softbox tent',width=w,height=h,float_buffer=True)
im.colorspace_settings.name='Linear Rec.709'
im.pixels.foreach_set(np.dstack((field,np.ones((h,w)))).astype('float32').ravel())
im.file_format='OPEN_EXR';im.pack()
tree=scene.world.node_tree
card=tree.nodes.new('ShaderNodeTexEnvironment');card.image=im
mix=tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[0].default_value=.12
tree.links.new(tree.nodes.get('Environment Texture').outputs['Color'],mix.inputs[1])
tree.links.new(card.outputs['Color'],mix.inputs[2])
tree.links.new(mix.outputs['Color'],tree.nodes.get('Background').inputs['Color'])
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=1.05
for ob in scene.objects:
    if ob.type=='LIGHT':ob.data.energy*=.20;ob.data.size*=1.7;ob.data.size_y*=1.35
mat=scene.objects['Upper_Ruby'].active_material
bs=mat.node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=(.94,.105,.17,1)
mat.node_tree.nodes.get('Volume Absorption').inputs['Density'].default_value=.70
scene.cycles.samples=64
cam=scene.camera;cam.location=(0,-23,.56);cam.rotation_euler=(Vector((0,0,.27))-cam.location).to_track_quat('-Z','Y').to_euler()
if '--save' in __import__('sys').argv or globals().get('SAVE_HOURGLASS',False):
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
else:
    scene.render.resolution_percentage=60;scene.cycles.samples=24
    scene.render.filepath=str(root/scene.get('candidate','candidate01')/'light_test.png')
    bpy.ops.render.render(write_still=True)
