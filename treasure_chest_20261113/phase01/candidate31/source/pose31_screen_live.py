import bpy,math,json,time,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');C=R/'phase01/candidate31';sc=bpy.context.scene;inv=Matrix.Rotation(math.radians(32),3,'Y').inverted();IN=np.array(inv);master=sc.objects['Chest Rig Master'];rest=sc.frame_current
moving=['Chest Front Hasp Barrel','Chest Curved Hasp Tongue','Chest Key Driven Slider','Chest Compliant Catch Leaf','Chest Removable Crank Key']
def geometry(ob):
 if ob.name=='Chest Compliant Catch Leaf':
  dg=bpy.context.evaluated_depsgraph_get();eo=ob.evaluated_get(dg);m=eo.to_mesh();m.calc_loop_triangles();v=np.array([x.co[:] for x in m.vertices]);t=np.array([x.vertices[:] for x in m.loop_triangles]);A=np.array(eo.matrix_world);eo.to_mesh_clear()
 else:
  m=ob.data;m.calc_loop_triangles();v=np.array([x.co[:] for x in m.vertices]);t=np.array([x.vertices[:] for x in m.loop_triangles]);A=np.array(ob.matrix_world)
 v=v@A[:3,:3].T+A[:3,3];local=np.c_[v[:,0],v[:,2],-v[:,1]]@IN.T;return v,t,local,BVHTree.FromPolygons(v.tolist(),t.tolist(),all_triangles=True,epsilon=1e-8)
sc.frame_set(0);bpy.context.view_layer.update();fixed={o.name:geometry(o) for o in sc.objects if o.type=='MESH' and o.get('full_form') and o.name not in moving};bad=[];contacts={};poses=[];end=time.time()+75
try:
 for frame in list(range(0,491,10)):
  s=json.loads((R/'schedule.json').read_text())
  if time.time()>end or s['phase']!='work' or time.time()+10>s['work_until_epoch']:break
  sc.frame_set(frame);bpy.context.view_layer.update();names=[n for n in moving if n!='Chest Removable Crank Key' or float(master['show_key'])>.5];data={n:geometry(sc.objects[n]) for n in names};tests=[]
  for name in names:
   for other,value in fixed.items():tests.append((name,other,data[name],value))
  for i,name in enumerate(names):
   for other in names[i+1:]:
    if {name,other}=={'Chest Front Hasp Barrel','Chest Curved Hasp Tongue'}:continue
    tests.append((name,other,data[name],data[other]))
  for a,b,da,db in tests:
   hits=da[3].overlap(db[3])
   if not hits:continue
   unknown=[]
   for ia,ib in hits:
    qa=da[2][da[1][ia]];qb=db[2][db[1][ib]];kind=None
    if {a,b}=={'Chest Compliant Catch Leaf','Chest Fixed Leaf Clamp'}:
     leaf=qa if a=='Chest Compliant Catch Leaf' else qb
     if leaf[:,0].min()>=.280-1e-5:kind='fixed_leaf_root_clamp'
    if {a,b}=={'Chest Removable Crank Key','Chest Shield Lock Plate With Bore'}:
     keytri=qa if a=='Chest Removable Crank Key' else qb;platetri=qb if a=='Chest Removable Crank Key' else qa
     # A beveled flange triangle may extend forward from a tangent edge.
     # Both actual triangles must remain in opposite closed halfspaces of the stop plane.
     if platetri[:,2].max()<=2.107+.000001 and keytri[:,2].min()>=2.107-.000001:kind='actual_stop_supporting_plane_contact'
    if {a,b}=={'Chest Removable Crank Key','Chest Key Driven Slider'}:
     key=qa if a=='Chest Removable Crank Key' else qb;sl=qb if a=='Chest Removable Crank Key' else qa;c=float(master['cycle'])%2;alpha=min(c,2-c)*math.pi/2;pc=np.array([-.14*math.sin(alpha),-.536-.14*math.cos(alpha)]);d=float(sc.objects['Chest Rig BoltShift']['shift']);walls=[-.045+d,.025+d]
     left,right=walls
     separated=(key[:,0].min()>=left-.000001 and sl[:,0].max()<=left+.000001) or (key[:,0].max()<=right+.000001 and sl[:,0].min()>=right-.000001)
     if key[:,2].max()<=1.89502 and np.linalg.norm(key[:,:2]-pc,axis=1).max()<=.02502 and separated:kind='crank_driving_support_plane_contact'
    if kind:contacts[kind]=contacts.get(kind,0)+1
    else:unknown.append([int(ia),int(ib)])
   if unknown:bad.append(dict(frame=frame,a=a,b=b,unclassified_triangle_pairs=len(unknown),sample=unknown[:3]))
  poses.append(dict(frame=frame,shift=float(sc.objects['Chest Rig BoltShift']['shift']),spring_lift=float(sc.objects['Chest Rig SpringLift']['lift'])))
finally:
 sc.frame_set(rest);bpy.context.view_layer.update()
(C/'pose_motion_screen.json').write_text(json.dumps(dict(certified=False,screen_only=True,frames=poses,unclassified=bad,intended_contacts=contacts,full_frame_screen_complete=len(poses)==50),indent=2));print(json.dumps(dict(frames=len(poses),unclassified_pairs=bad[:12],unclassified_count=len(bad),contacts=contacts)))
