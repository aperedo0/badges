import bpy,numpy as np,sys,math
from pathlib import Path
from mathutils import Vector
R=Path('/Users/antonioperedo/Desktop/badges/ruby_heart_smooth_20261112')
sys.path.insert(0,str(R/'tools'))
import smooth_frame
D=smooth_frame.make();np.savez(R/'candidate01/geometry.npz',**D)
previous=bpy.context.scene
sc=bpy.data.scenes.get('Ruby Heart Smooth') or bpy.data.scenes.new('Ruby Heart Smooth')
bpy.context.window.scene=sc
sc.world=previous.world.copy()
if sc.camera is None:
 for ob in previous.objects:
  if ob.type in ('CAMERA','LIGHT'):
   name='Ruby Heart '+ob.type+' '+ob.name.split('Development')[-1]
   if name in sc.objects:continue
   new=ob.copy();new.data=ob.data.copy();new.name=name;sc.collection.objects.link(new)
   if ob.type=='CAMERA':sc.camera=new
sc.render.engine='CYCLES';sc.cycles.samples=128;sc.cycles.use_denoising=True
sc.render.resolution_x=sc.render.resolution_y=1100;sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'

def material(name,col,metal,rough):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 return m

gold=material('Ruby Heart preserved gold',(1,.44,.07),1,.30)
nt=gold.node_tree
if not nt.nodes.get('Preserved gold grain'):
 tex=nt.nodes.new('ShaderNodeTexImage');tex.name='Preserved gold grain';tex.image=bpy.data.images.load(str(R.parent/'ruby_heart_claude_20261107/trace/gold_brush_roughness.png'),check_existing=True);tex.image.colorspace_settings.name='Non-Color';tex.extension='EXTEND';nt.links.new(tex.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Roughness'])
ruby=material('Ruby Heart unchanged gem preview',(.55,.01,.08),0,.05)
# The app optical shader stays unchanged. This material is only for rim shape inspection.
def convert(v):return np.c_[v[:,0],-v[:,2],v[:,1]]
for key,mat in [('frame',gold),('gem',ruby)]:
 name='Ruby Heart '+key
 ob=sc.objects.get(name)
 if ob is None:
  me=bpy.data.meshes.new(name);ob=bpy.data.objects.new(name,me);sc.collection.objects.link(ob)
 else:me=ob.data;me.clear_geometry();me.materials.clear()
 me.from_pydata(convert(D[key+'_v']).tolist(),[],D[key+'_t'].tolist());me.update()
 me.polygons.foreach_set('use_smooth',[True]*len(me.polygons))
 ids=np.array([x.vertex_index for x in me.loops]);me.normals_split_custom_set(convert(D[key+'_n'][ids]).tolist())
 if key=='frame':
  uv=me.uv_layers.get('st') or me.uv_layers.new(name='st');uv.data.foreach_set('uv',D['frame_uv'][ids].ravel())
 me.materials.append(mat)
if not sc.objects.get('Ruby Heart mockup'):
 ref=bpy.data.objects.new('Ruby Heart mockup',None);ref.empty_display_type='IMAGE';ref.data=bpy.data.images.load('/Users/antonioperedo/Downloads/Faceted Ruby Heart Emblem.png',check_existing=True);ref.location=(-6.8,0,.27);ref.rotation_euler=(math.pi/2,0,0);ref.empty_display_size=5.5;sc.collection.objects.link(ref)
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  area.spaces.active.region_3d.view_location=(0,0,.27);area.spaces.active.region_3d.view_distance=7.2
  area.spaces.active.region_3d.view_rotation=sc.camera.rotation_euler.to_quaternion()
  area.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ruby_heart.blend'))
print('Saved complete Ruby Heart with repaired frame, unchanged gem and reference')
