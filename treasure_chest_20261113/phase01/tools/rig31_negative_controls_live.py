import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');C=R/'phase01/candidate34';sc=bpy.context.scene
Y=Matrix.Rotation(math.radians(32),3,'Y');IN=np.array(Y.inverted());A=np.array(Y)
def world(q):
 p=A@np.array(q);return Vector((p[0],-p[2],p[1]))
def mesh(ob):
 dg=bpy.context.evaluated_depsgraph_get();eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();v=np.array([p.co[:] for p in me.vertices]);t=np.array([p.vertices[:] for p in me.loop_triangles]);M=np.array(eo.matrix_world);eo.to_mesh_clear();v=v@M[:3,:3].T+M[:3,3];local=np.c_[v[:,0],v[:,2],-v[:,1]]@IN.T
 return local,t,BVHTree.FromPolygons(v.tolist(),t.tolist(),all_triangles=True,epsilon=1e-8)
import time
schedule=json.loads((R/'schedule.json').read_text());manual_path=R/'work_mode.json';manual=json.loads(manual_path.read_text()) if manual_path.exists() else {};manual_ok=manual.get('mode')=='manual' and manual.get('manual_work_authorized') and not manual.get('overnight_enabled');assert manual_ok or (schedule['status']=='active' and schedule['phase']=='work' and time.time()+30<schedule['work_until_epoch'])
def at(frame,names):
 sc.frame_set(frame);bpy.context.view_layer.update();return {n:mesh(sc.objects[n]) for n in names}
def tree(local,tri):
 v=np.array([world(q)[:] for q in local]);return BVHTree.FromPolygons(v.tolist(),tri.tolist(),all_triangles=True,epsilon=1e-8)
leaf='Chest Compliant Catch Leaf';slider='Chest Key Driven Slider';tongue='Chest Curved Hasp Tongue';key='Chest Removable Crank Key';face='Chest Shield Lock Plate With Bore'
try:
 rest=at(0,[leaf,slider]);release=at(90,[leaf,slider]);hasp=at(101,[tongue,slider]);result={}
 lifted_hits=len(release[leaf][2].overlap(release[slider][2]));unlifted_hits=len(rest[leaf][2].overlap(release[slider][2]))
 assert lifted_hits==0 and unlifted_hits>0,(lifted_hits,unlifted_hits)
 result['no_spring_lift']={'correct_surface_intersections':lifted_hits,'negative_surface_intersections':unlifted_hits,'rejected':True}
 free_hits=len(hasp[tongue][2].overlap(hasp[slider][2]));locked_hits=len(hasp[tongue][2].overlap(rest[slider][2]))
 assert free_hits==0 and locked_hits>0,(free_hits,locked_hits)
 result['engaged_pin_during_release']={'correct_surface_intersections':free_hits,'negative_surface_intersections':locked_hits,'hasp_degrees':2.,'rejected':True}
 drive=[]
 for frame,branch in [(70,'opening'),(160,'return')]:
  data=at(frame,[key]);v,t,tr=data[key];rear=v[v[:,2]<1.85501];assert len(rear)>100
  c=float(sc.objects['Chest Rig Master']['cycle'])%2;alpha=min(c,2-c)*math.pi/2;d=float(sc.objects['Chest Rig BoltShift']['shift'])
  actual_gap=float(rear[:,0].min()-(-.045+d)) if branch=='opening' else float(.025+d-rear[:,0].max())
  fake=-.14*math.sin(alpha) if branch=='opening' else min(0,-.14*math.sin(alpha)+.02)
  fake_gap=float(rear[:,0].min()-(-.045+fake)) if branch=='opening' else float(.025+fake-rear[:,0].max())
  assert abs(actual_gap)<.000006 and fake_gap>.019,(frame,actual_gap,fake_gap)
  drive.append({'frame':frame,'branch':branch,'actual_driving_side_gap':actual_gap,'negative_wrong_side_gap':fake_gap,'rejected':True})
 result['centered_fake_opening_and_wrong_return_branch']=drive
 data=at(70,[key,face]);v,t,tr=data[key];f=data[face];hits=[]
 for offset in np.linspace(.01,.8,80):
  shifted=v.copy();shifted[:,2]+=offset;count=len(tree(shifted,t).overlap(f[2]))
  if count:hits.append({'outward_offset':float(offset),'surface_intersections':count})
 assert hits,'Chosen wrong key withdrawal orientation was not obstructed'
 result['wrong_key_withdrawal_orientation']={'key_degrees':45.,'actual_obstructed_offsets':hits,'rejected':True,'not_a_claim_of_captivity_at_every_nonzero_angle':True}
 (C/'rig_negative_controls.json').write_text(json.dumps({'controls':result,'complete_continuous_motion_proof':False,'method':'Actual finished surfaces and measured driving side support gaps'},indent=2)+'\n')
 print(json.dumps(result))
finally:
 sc.frame_set(0);bpy.context.view_layer.update()
