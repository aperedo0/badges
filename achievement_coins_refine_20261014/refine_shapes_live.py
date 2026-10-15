from pathlib import Path
import bpy,json,numpy as np
R=Path('/Users/antonioperedo/Desktop/badges/achievement_coins_refine_20261014')
# Run only the helper definitions; retain the owner's open working scenes.
ns={'__file__':str(R/'blender_workbench.py')};exec((R/'blender_workbench.py').read_text().split('LIVE=globals()')[0],ns)
ln={'__file__':str(R/'blender_finish_shapes.py')};exec((R/'blender_finish_shapes.py').read_text().split("for name in ['hourglass_teal'")[0],ln)
for name in ['hourglass_teal','hourglass_gold','sprout']:
 scene=bpy.data.scenes[name];bpy.context.window.scene=scene;b=R/name;m=json.loads((b/'design.json').read_text());old=np.load(b/'reliefs.npz');arrays={k:old[k] for k in old.files}
 if name.startswith('hourglass'):
  for i,f in enumerate(m['features']):
   if 'blender_lathe' not in f:continue
   p,t,n,fc=ln['lathe'](f['blender_lathe']);arrays[f'{i}_points']=p;arrays[f'{i}_triangles']=t;arrays[f'{i}_normals']=n;f['front_count']=fc;f['triangles']=len(t)
  np.savez_compressed(b/'reliefs.npz',**arrays);(b/'design.json').write_text(json.dumps(m,indent=2))
 # Install the new solids into the complete coins, keeping the existing shell.
 for i,f in enumerate(m['features']):
  p=arrays[f'{i}_points'];t=arrays[f'{i}_triangles']
  for side in ['Front','Back']:
   prefix=f'Relief{side}_{i}_{f["role"]}';obj=next(o for o in scene.objects if o.name.startswith(prefix));mats=list(obj.data.materials)
   vertices=p if side=='Front' else p*[-1,1,-1]+[0,0,-.33]
   mesh=bpy.data.meshes.new(prefix+'_Refined');mesh.from_pydata(vertices.tolist(),[],t.tolist());mesh.update();obj.data=mesh
   for mat in mats:mesh.materials.append(mat)
   for face in mesh.polygons:face.use_smooth=f['role'] not in ['emerald','soil','emerald_background']
 ns['build_curved_borders'](scene,name)
for scene in bpy.data.scenes:
 for obj in scene.objects:
  if obj.type=='MESH' and obj.name.startswith(('ReliefFront_','ReliefBack_')) and obj.name.endswith('background'):
   for mat in obj.data.materials:
    mat.diffuse_color=(.008,.010,.012,1)
bpy.context.window.scene=bpy.data.scenes['hourglass_teal']
bpy.ops.wm.save_as_mainfile(filepath=str(R/'coins.blend'),compress=True)
print('Refined hourglass bars, column profiles, and sprout facets in live Blender.')
