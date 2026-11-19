"""Create a complete editable Blender checkpoint without repacking its USD."""
from pathlib import Path
import bpy,numpy as np,json
from mathutils import Vector,Quaternion
ROOT=Path('/Users/antonioperedo/Desktop/badges/astral_compact_20261104');C=ROOT/'candidate01'
D=np.load(C/'optimized_geometry.npz');groups=json.loads((C/'optimized_groups.json').read_text())
source=ROOT.parent/'forge_tide_compass_20261103/astral_navigator/source/astral_navigator.blend'
with bpy.data.libraries.load(str(source),link=False) as (available,loaded):loaded.scenes=[available.scenes[0]]
donor=loaded.scenes[0];materials={}
for ob in donor.objects:
 if ob.type=='MESH' and not ob.get('construction_guide'):
  for mat in ob.data.materials:
   if mat:materials.setdefault(mat.name.split('.')[0],mat)
scene=bpy.data.scenes.new('Astral Navigator compact working copy');bpy.context.window.scene=scene
for i,g in enumerate(groups):
 p=D[str(i)+'_points'];t=D[str(i)+'_triangles'];n=D[str(i)+'_normals'];uv=D[str(i)+'_uv']
 me=bpy.data.meshes.new(g['name']);me.from_pydata(p.tolist(),[],t.tolist());me.update()
 ob=bpy.data.objects.new(g['name'],me);scene.collection.objects.link(ob)
 key=g['material'].rsplit('/',1)[-1];assert key in materials,key;me.materials.append(materials[key])
 for face in me.polygons:face.use_smooth=True
 me.normals_split_custom_set(n.reshape(-1,3).tolist())
 if not g['gem'] and key.endswith(('_metal','_field')):
  layer=me.uv_layers.new(name='BadgeUV')
  for k,loop in enumerate(me.loops):layer.data[k].uv=uv.reshape(-1,2)[k]
 ob['approved_triangle_attributes_preserved']=True
for ob in donor.objects:
 if ob.type=='EMPTY' and ob.empty_display_type=='IMAGE':
  ref=ob.copy();ref.name='Approved reference';scene.collection.objects.link(ref)
scene.view_settings.view_transform=donor.view_settings.view_transform;scene.view_settings.look=donor.view_settings.look
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  s=a.spaces.active;s.region_3d.view_rotation=Quaternion((1,0,0,0));s.region_3d.view_location=Vector((0,.28,0));s.region_3d.view_distance=9.1;s.region_3d.view_perspective='ORTHO';s.shading.type='MATERIAL';s.overlay.show_overlays=False
bpy.data.libraries.write(str(C/'source/astral_navigator_compact.blend'),{scene},compress=True)
print('Saved complete editable working copy:',len([ob for ob in scene.objects if ob.type=='MESH']),'meshes')
