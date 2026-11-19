import bpy,math,json,time,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');C=R/'phase01/candidate25';sc=bpy.context.scene
parts=json.loads((C/'mechanism_parts.json').read_text());moving=set(parts['moving_hasp']);active=[o for o in sc.objects if o.type=='MESH' and o.get('full_form')]
yaw=Matrix.Rotation(math.radians(32),3,'Y');pivot=yaw@Vector((0,.48525,2.0));pivot=Vector((pivot.x,-pivot.z,pivot.y));axis=yaw@Vector((1,0,0));axis=Vector((axis.x,-axis.z,axis.y))
def tree(ob,trans=None):
 me=ob.data;me.calc_loop_triangles();v=[(trans@q.co if trans is not None else q.co.copy()) for q in me.vertices];t=[tuple(p.vertices) for p in me.loop_triangles];return BVHTree.FromPolygons(v,t,all_triangles=True,epsilon=1e-7),v
fixed={o.name:tree(o) for o in active if o.name not in moving};records=[]
for angle in [0,2.5,5,10,20,40,60,90,120,150]:
 state=json.loads((R/'schedule.json').read_text());assert state['status']=='active' and state['phase']=='work' and time.time()+15<state['work_until_epoch'],'Work block must remain active'
 trans=Matrix.Translation(pivot)@Matrix.Rotation(-math.radians(angle),4,axis)@Matrix.Translation(-pivot)
 for name in moving:
  mt,mv=tree(sc.objects[name],trans)
  for other,(ft,fv) in fixed.items():
   overlaps=mt.overlap(ft)
   if overlaps:records.append(dict(angle=angle,moving=name,fixed=other,triangle_intersections=len(overlaps)))
(C/'motion_screen.json').write_text(json.dumps(dict(certified=False,screen_only=True,collision_pairs=records,pose_angles=[0,2.5,5,10,20,40,60,90,120,150]),indent=2));print(json.dumps(records))
