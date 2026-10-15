"""Build the water reliefs in a separate complete-coin Blender scene."""
from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector,Matrix
R=Path('/Users/antonioperedo/Desktop/badges/water_match_20261014');b=R/'clean'
scene=bpy.data.scenes.get('water_match')
if scene is None:
 source=bpy.data.scenes['clean'];scene=bpy.data.scenes.new('water_match');scene.world=source.world.copy()
 for old in source.objects:
  obj=old.copy()
  if old.data is not None and old.type=='MESH':obj.data=old.data.copy()
  scene.collection.objects.link(obj)
bpy.context.window.scene=scene
helper=R.parent/'achievement_coins_refine_20261014/blender_finish_shapes.py';ns={'__file__':str(helper)}
exec(helper.read_text().split("for name in ['hourglass_teal'")[0],ns)
m=json.loads((b/'design.json').read_text());loaded=np.load(b/'reliefs.npz');arrays={k:loaded[k] for k in loaded.files}
for i in [0,1,2]:
 f=m['features'][i];p,t,n,fc=ns['lathe'](f['blender_lathe']);f['front_count']=fc;f['triangles']=len(t)
 arrays[f'{i}_points']=p;arrays[f'{i}_triangles']=t;arrays[f'{i}_normals']=n
 for side in ['Front','Back']:
  obj=next(o for o in scene.objects if o.name.startswith(f'Relief{side}_{i}_water'))
  mats=list(obj.data.materials);vertices=p if side=='Front' else p*[-1,1,-1]+[0,0,-.33]
  mesh=bpy.data.meshes.new(f'Water_loft_{side}_{i}');mesh.from_pydata(vertices.tolist(),[],t.tolist());mesh.update();mesh.normals_split_custom_set(n.reshape(-1,3).tolist());obj.data=mesh
  for mat in mats:mesh.materials.append(mat)
  for poly in mesh.polygons:poly.use_smooth=True
  uv=mesh.uv_layers.new(name='CoinReliefUV')
  for loop in mesh.loops:
   q=mesh.vertices[loop.vertex_index].co;xx=q.x if side=='Front' else -q.x;uv.data[loop.index].uv=((xx+3.015)/6.03,(q.y+3.015)/6.03)
for obj in scene.objects:obj.select_set(False)
ref=next(o for o in scene.objects if o.type=='EMPTY' and 'reference' in o.name);ref.hide_viewport=False
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  r=area.spaces.active.region_3d;r.view_rotation=Matrix.Identity(3).to_quaternion();r.view_location=Vector((-3.3,0,0));r.view_distance=11;r.view_perspective='ORTHO'
np.savez_compressed(b/'reliefs.npz',**arrays);(b/'design.json').write_text(json.dumps(m,indent=2))
bpy.data.libraries.write(str(R/'water.blend'),{scene},compress=True)
print('Smooth water reliefs built in the separate water_match scene.')
