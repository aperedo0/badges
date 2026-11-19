import bpy,json,numpy as np
from pathlib import Path
from mathutils.bvhtree import BVHTree
C=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase01/candidate28');ob=bpy.context.scene.objects['Chest Curved Hasp Tongue'];m=ob.data;m.calc_loop_triangles();v=[x.co.copy() for x in m.vertices];t=[tuple(x.vertices) for x in m.loop_triangles];tree=BVHTree.FromPolygons(v,t,all_triangles=True,epsilon=1e-8)
pairs=[]
for a,b in tree.overlap(tree):
 if a>=b or set(t[a])&set(t[b]):continue
 pairs.append([a,b])
(C/'self_intersection_screen.json').write_text(json.dumps(dict(nonadjacent_intersection_pairs=pairs,triangle_count=len(t),no_nonadjacent_self_intersections=not pairs,adjacent_triangles_excluded=True),indent=2));print('Nonadjacent tongue pairs',len(pairs));assert not pairs
