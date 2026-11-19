import bpy,numpy as np,math,json,time
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate39';sc=bpy.context.scene;master=sc.objects['Chest Rig Master'];rest=sc.frame_current;assert rest==0
policy=json.loads((R/'work_mode.json').read_text());assert policy['manual_work_authorized'] and not policy['owner_paused_badge_work']
exec(compile((P/'tools/frame36_geometry.py').read_text(),'helpers36','exec'))
roles=json.loads((C/'inspection_ownership.json').read_text())['parts'];lidnames=[n for n,r in roles.items() if r=='lid'];haspnames=[n for n,r in roles.items() if r=='hasp'];bodynames=[n for n,r in roles.items() if r=='body'];slider='Chest Key Driven Slider';leaf='Chest Compliant Catch Leaf';key='Chest Removable Crank Key';action=master.animation_data.action;curves=list(action.fcurves) if hasattr(action,'fcurves') else [f for l in action.layers for s in l.strips for bag in s.channelbags for f in bag.fcurves];curve=next(f for f in curves if f.data_path=='["lid_degrees"]');oldmute=curve.mute;yaw=Matrix.Rotation(math.radians(32),3,'Y');Y=np.array(yaw);axis=Vector((yaw[0][0],-yaw[2][0],yaw[1][0])).normalized();a=yaw@Vector((0,.36175,-1.93));pivot=Vector((a.x,-a.z,a.y));cache={};localcache={};bad=[];contacts={};angles=[];frames=[];negative={};end=time.time()+480

def stepgraph():
 master.update_tag(refresh={'TIME','OBJECT'});bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();dg.update();return dg

def geom(name,dg):
 ob=sc.objects[name];eo=ob.evaluated_get(dg);M=np.array(eo.matrix_world);deforms=bool(ob.data.shape_keys or any(m.show_viewport for m in ob.modifiers));signature=M.tobytes()
 if deforms:signature+=np.array([k.value for k in ob.data.shape_keys.key_blocks],dtype=float).tobytes() if ob.data.shape_keys else str(sc.frame_current).encode()
 if name in cache and cache[name][0]==signature:return cache[name][1]
 if name not in localcache or deforms:
  me=eo.to_mesh();me.calc_loop_triangles();v=np.array([p.co[:] for p in me.vertices]);t=np.array([f.vertices[:] for f in me.loop_triangles]);eo.to_mesh_clear()
  if not deforms:localcache[name]=(v,t)
 else:v,t=localcache[name]
 world=v@M[:3,:3].T+M[:3,3];local=np.c_[world[:,0],world[:,2],-world[:,1]]@Y;out=dict(v=world,t=t,q=local,tree=BVHTree.FromPolygons(world.tolist(),t.tolist(),all_triangles=True,epsilon=1e-8),low=world.min(0),high=world.max(0));cache[name]=(signature,out);return out

def owncheck(dg):
 deg=float(master['lid_degrees']);expected=Matrix.Translation(pivot)@Matrix.Rotation(-math.radians(deg),4,axis)@Matrix.Translation(-pivot);err=0.
 for name in lidnames:err=max(err,float(np.max(abs(np.array(sc.objects[name].evaluated_get(dg).matrix_world)-np.array(expected)))))
 assert err<1e-5,('lid ownership',sc.frame_current,deg,err)
 actual=float(sc.objects['Chest Rig LidOpen'].evaluated_get(dg).rotation_axis_angle[0]);assert abs(actual+math.radians(deg))<1e-6,('disabled lid driver',deg,actual)
 for name in bodynames:
  if name in (slider,leaf):continue
  assert np.max(abs(np.array(sc.objects[name].evaluated_get(dg).matrix_world)-np.eye(4)))<1e-7,(name,'body moved with lid')
 return err

def classification(a,b,qa,qb):
 pair={a,b}
 if pair=={leaf,'Chest Fixed Leaf Clamp'}:
  L=qa if a==leaf else qb
  if L[:,0].min()>=.280-1e-5:return 'fixed_leaf_root_clamp'
 if pair=={key,'Chest Shield Lock Plate With Bore'}:
  K=qa if a==key else qb;S=qb if a==key else qa
  if S[:,2].max()<=2.107+.000001 and K[:,2].min()>=2.107-.000001:return 'actual_stop_supporting_plane_contact'
 if pair=={key,slider}:
  K=qa if a==key else qb;S=qb if a==key else qa;c=float(master['cycle'])%2;alpha=min(c,2-c)*math.pi/2;pc=np.array([-.14*math.sin(alpha),-.536-.14*math.cos(alpha)]);d=float(sc.objects['Chest Rig BoltShift']['shift']);left,right=-.045+d,.025+d;separated=(K[:,0].min()>=left-.000001 and S[:,0].max()<=left+.000001) or (K[:,0].max()<=right+.000001 and S[:,0].min()>=right-.000001)
  if K[:,2].max()<=1.89502 and np.linalg.norm(K[:,:2]-pc,axis=1).max()<=.02502 and separated:return 'crank_driving_support_plane_contact'
 return None

def paircheck(a,b,A,B,label):
 if np.any(A['high']<B['low']-1e-7) or np.any(B['high']<A['low']-1e-7):return
 hits=A['tree'].overlap(B['tree']);unknown=[]
 for ia,ib in hits:
  kind=classification(a,b,A['q'][A['t'][ia]],B['q'][B['t'][ib]])
  if kind:contacts[kind]=contacts.get(kind,0)+1
  else:unknown.append((int(ia),int(ib)))
 if unknown:bad.append(dict(pose=label,a=a,b=b,intersections=len(unknown),sample=unknown[:4]));return
 if hits:return
 # Each model mesh is connected. Without crossing surfaces, an enclosed component
 # must have its full bounds inside the other bounds; probe both such cases.
 for x,y,X,Z in ((a,b,A,B),(b,a,B,A)):
  if np.all(X['low']>=Z['low']-1e-7) and np.all(X['high']<=Z['high']+1e-7):
   try:enclosed=inside36(Z['tree'],X['v'][0])
   except AssertionError:
    (C/'boundary_probe_diagnosis.json').write_text(json.dumps(dict(pose=label,source=x,target=y,point=X['v'][0].tolist()),indent=2));raise
   if enclosed:bad.append(dict(pose=label,a=x,b=y,contained_without_crossing=True))

def pairs(moving,fixed,label,dg,relative=True):
 data={n:geom(n,dg) for n in moving};fn=list(fixed);lows=np.array([fixed[n]['low'] for n in fn]);highs=np.array([fixed[n]['high'] for n in fn])
 for a,A in data.items():
  possible=np.where(np.all(highs>=A['low']-1e-7,axis=1)&np.all(lows<=A['high']+1e-7,axis=1))[0]
  for j in possible:paircheck(a,fn[j],A,fixed[fn[j]],label)
 if relative:
  for i,a in enumerate(moving):
   for b in moving[i+1:]:
    if (a in lidnames and b in lidnames) or (a in haspnames and b in haspnames):continue
    paircheck(a,b,data[a],data[b],label)
 return data

def progress(stage):
 (C/'motion_progress.json').write_text(json.dumps(dict(stage=stage,opening_angles_complete=len(angles),action_frames_complete=len(frames),unclassified_count=len(bad)),indent=2))

try:
 sc.frame_set(0);dg=stepgraph();fixed={n:geom(n,dg) for n in bodynames if n not in (slider,leaf)};sc.frame_set(75);dg=stepgraph();names=lidnames+haspnames+[slider,leaf]+([key] if float(master['show_key'])>.5 else []);pairs(names,fixed,'frame75 diagnostic',dg)
except AssertionError as e:print('Observed original boundary probe failure',str(e))
finally:sc.frame_set(0);bpy.context.view_layer.update()
