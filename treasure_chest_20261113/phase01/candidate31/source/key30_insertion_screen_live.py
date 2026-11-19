import bpy,math,json,time,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');C=R/'phase01/candidate30';sc=bpy.context.scene;key=sc.objects['Chest Removable Crank Key'];yaw=Matrix.Rotation(math.radians(32),3,'Y');q=yaw@Vector((0,0,1));direction=Vector((q.x,-q.z,q.y))
def data(ob):
 me=ob.data;me.calc_loop_triangles();v=np.array([p.co[:] for p in me.vertices]);t=np.array([p.vertices[:] for p in me.loop_triangles]);return v,t
kv,kt=data(key);fixed={o.name:data(o) for o in sc.objects if o.type=='MESH' and o.get('full_form')};trees={n:BVHTree.FromPolygons(v.tolist(),t.tolist(),all_triangles=True,epsilon=1e-8) for n,(v,t) in fixed.items()};pairs=[]
for off in [1.,.8,.6,.4,.2,.1,.05,.01,.001,0.]:
 v=kv+np.array(direction)*off;tr=BVHTree.FromPolygons(v.tolist(),kt.tolist(),all_triangles=True,epsilon=1e-8)
 for name,tree in trees.items():
  hits=tr.overlap(tree)
  if hits:pairs.append(dict(insertion_offset=off,fixed=name,triangle_pairs=len(hits),sample=hits[:4]))
(C/'key_insertion_screen.json').write_text(json.dumps(dict(certified=False,screen_only=True,pairs=pairs),indent=2));print(json.dumps(pairs))
