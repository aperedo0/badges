import bpy,numpy as np,math,json,time
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate42';sc=bpy.context.scene;master=sc.objects['Chest Rig Master'];rest=sc.frame_current;assert rest==0
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

def point_inside39(T, p):
    ans = []
    for ray in ([0.93, 0.21, 0.3], [-0.23, 0.89, 0.34], [0.27, 0.31, 0.91]):
        ray = np.array(ray)
        ray /= np.linalg.norm(ray)
        E = T[:, 1] - T[:, 0]
        F = T[:, 2] - T[:, 0]
        h = np.cross(np.broadcast_to(ray, F.shape), F)
        det = np.einsum('ij,ij->i', E, h)
        valid = abs(det) > 1e-14
        inv = np.divide(1.0, det, out=np.zeros_like(det), where=valid)
        S = p - T[:, 0]
        u = np.einsum('ij,ij->i', S, h) * inv
        Q = np.cross(S, E)
        v = Q @ ray * inv
        dist = np.einsum('ij,ij->i', F, Q) * inv
        hit = valid & (u >= 0) & (v >= 0) & (u + v <= 1) & (dist > 1e-07)
        d = np.sort(dist[hit])
        count = int(np.r_[True, np.diff(d) > 1e-06].sum()) if len(d) else 0
        ans.append(bool(count % 2))
    assert len(set(ans)) == 1, (p.tolist(), ans)
    return ans[0]

def material39(X):
 if 'material_witnesses' in X:return X['material_witnesses']
 tri=X['v'][X['t']];normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(normal,axis=1);order=np.argsort(area)[-32:][::-1];witnesses=[]
 for k in order:
  if area[k]<=1e-12:continue
  p=tri[k].mean(0)-normal[k]/area[k]*1e-5
  try:valid=point_inside39(tri,p)
  except AssertionError:continue
  if valid:witnesses.append(p)
  if len(witnesses)==3:break
 assert witnesses,'No verified solid interior witness'
 X['material_witnesses']=witnesses;return witnesses

def on_boundary39(X,p):
 if 'double_field' not in X:
  tri=X['v'][X['t']];G=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);G/=np.linalg.norm(G,axis=1)[:,None];X['double_field']=dict(tri=tri,geom=G,index=index36(tri))
 return bool(near36(X['double_field'],p,1e-6))

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
   enclosed=False;classified=0
   for p in material39(X):
    try:value=point_inside39(Z['v'][Z['t']],p)
    except AssertionError:
     if on_boundary39(Z,p):continue
     raise
    classified+=1
    if value:enclosed=True;break
   assert classified,(x,y,'No strict containment witness')
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
 sc.frame_set(240);bpy.context.view_layer.update();curve.mute=True;master['lid_degrees']=0.;dg=stepgraph();fixed={n:geom(n,dg) for n in bodynames};moving=lidnames+haspnames
 for degree in range(0,111,2):
  assert time.time()<end,'Motion screen time bound reached';master['lid_degrees']=float(degree);dg=stepgraph();err=owncheck(dg);before=len(bad);pairs(moving,fixed,'opening'+str(degree),dg,relative=(degree==0));angles.append(dict(degrees=degree,ownership_error=err,new_unclassified=len(bad)-before));progress('opening sweep')
 curve.mute=oldmute;master.update_tag(refresh={'TIME'});sc.frame_set(0);dg=stepgraph();fixed={n:geom(n,dg) for n in bodynames if n not in (slider,leaf)}
 for frame in range(0,491,5):
  assert time.time()<end,'Motion screen time bound reached';sc.frame_set(frame);dg=stepgraph();err=owncheck(dg);names=lidnames+haspnames+[slider,leaf]+([key] if float(master['show_key'])>.5 else []);before=len(bad);pairs(names,fixed,'frame'+str(frame),dg);frames.append(dict(frame=frame,lid_degrees=float(master['lid_degrees']),hasp_degrees=math.degrees(float(master['hasp'])),ownership_error=err,new_unclassified=len(bad)-before));progress('complete action screen')
 # A real locked hasp must obstruct forced lid opening.
 sc.frame_set(0);bpy.context.view_layer.update();curve.mute=True;locked=[]
 for degree in (.25,.5,1.,2.):
  master['lid_degrees']=degree;dg=stepgraph();A=geom('Chest Curved Hasp Tongue',dg);row=[]
  for other in (slider,'Chest Hollow Lock Case Walls','Chest Lock Backing With Bore','Chest Shield Lock Plate With Bore'):
   B=geom(other,dg);count=len(A['tree'].overlap(B['tree']))
   if count:row.append(dict(other=other,triangle_intersections=count))
  locked.append(dict(forced_lid_degrees=degree,actual_obstructions=row))
 assert any(r['actual_obstructions'] for r in locked),'Locked hasp negative control did not obstruct';negative['locked_hasp_forced_open']=dict(rejected=True,poses=locked)
 # Deliberately misparent an actual lid mesh, test the ownership gate, then restore.
 master['lid_degrees']=95.;dg=stepgraph();obj=sc.objects['Chest Barrel Lid Envelope'];saved=(obj.parent,obj.matrix_parent_inverse.copy(),obj.matrix_basis.copy())
 try:
  obj.parent=None;obj.matrix_world=Matrix.Identity(4);dg=stepgraph();rejected=False
  try:owncheck(dg)
  except AssertionError:rejected=True
  assert rejected,'Wrong owner was not rejected';negative['actual_wrong_ownership']=dict(rejected=True,part=obj.name)
 finally:obj.parent=saved[0];obj.matrix_parent_inverse=saved[1];obj.matrix_basis=saved[2];dg=stepgraph();owncheck(dg)
 # Verify detection of an actual enclosed solid with no crossing surfaces.
 Q=np.array([[2.44+x,-1+y,z] for x,y,z in [(-.01,-.01,-.01),(.01,-.01,-.01),(.01,.01,-.01),(-.01,.01,-.01),(-.01,-.01,.01),(.01,-.01,.01),(.01,.01,.01),(-.01,.01,.01)]]);app=Q@Y.T;W=np.c_[app[:,0],-app[:,2],app[:,1]];T=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]);cube=dict(v=W,t=T,q=Q,tree=BVHTree.FromPolygons(W.tolist(),T.tolist(),all_triangles=True),low=W.min(0),high=W.max(0));body=geom('Chest Body Envelope',dg);start=len(bad);assert not cube['tree'].overlap(body['tree']);paircheck('Virtual enclosed solid','Chest Body Envelope',cube,body,'containment negative control');found=bad[start:];assert any(r.get('contained_without_crossing') for r in found),'Enclosed solid escaped containment check';del bad[start:];negative['enclosed_solid_without_crossing']=dict(rejected=True,observed=found)
finally:
 curve.mute=oldmute;master.update_tag(refresh={'TIME'});sc.frame_set(rest);bpy.context.view_layer.update();bpy.context.evaluated_depsgraph_get().update()
 report=dict(certified=False,sampled_screen=True,opening_angles=angles,action_frames=frames,unclassified=bad,intended_contacts=contacts,negative_controls=negative,complete=len(angles)==56 and len(frames)==99,restored_frame=sc.frame_current,metal_finish_changed=False,wood_grain_added=False)
 (C/'whole_motion_screen.json').write_text(json.dumps(report,indent=2))
assert report['complete'] and [a['degrees'] for a in angles]==list(range(0,111,2)) and [f['frame'] for f in frames]==list(range(0,491,5)),'Incomplete motion report'
assert not bad,('Actual whole chest interference',bad[:12]);assert len(negative)==3
assert sc.frame_current==0 and abs(master['lid_degrees'])<1e-7
for n in roles:assert np.max(abs(np.array(sc.objects[n].matrix_world)-np.eye(4)))<1e-7,(n,'failed rest restore')
print(json.dumps(dict(angles=len(angles),action_frames=len(frames),unclassified_count=len(bad),intended_contacts=contacts,negative_controls={k:v['rejected'] for k,v in negative.items()},whole_chest_restored=True,sampled_not_continuously_certified=True)))
