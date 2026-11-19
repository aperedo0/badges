from pathlib import Path
import bpy,numpy as np,json
R=Path('/Users/antonioperedo/Desktop/badges/royal_heart_compass_20261106');C=R/'amethyst_crown/candidate17';G=json.loads((C/'groups.json').read_text());D={k:v.copy() for k,v in np.load(C/'blender_geometry.npz').items()};changed=[]
for i,g in enumerate(G):
 if g['name']!='Top fleur clean faceted gold finial frame':continue
 p=D[f'{i}_points']
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH' or not ob.name.startswith(g['name']) or len(ob.data.vertices)!=len(p):continue
  co=np.empty(p.size,np.float32);ob.data.vertices.foreach_get('co',co)
  if not np.array_equal(co.reshape(-1,3),p):continue
  me=ob.data
  for poly in me.polygons:poly.use_smooth=True
  me.update();me.calc_loop_triangles();corner=np.empty(len(me.corner_normals)*3,np.float32);me.corner_normals.foreach_get('vector',corner);loops=np.array([x.loops[:] for x in me.loop_triangles]);D[f'{i}_normals']=corner.reshape(-1,3)[loops];g['smooth']=True;changed.append(ob.name);break
assert len(changed)==2,changed
np.savez_compressed(C/'blender_geometry.npz',**D);(C/'groups.json').write_text(json.dumps(G,indent=2));bpy.data.libraries.write(str(C/'source/amethyst_crown.blend'),{bpy.context.scene},compress=True);print('Only finial frame normals changed',changed)
