import bpy,math,json,time,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');C=R/'phase01/candidate27';sc=bpy.context.scene
meta=json.loads((C/'mechanism_parts.json').read_text());moving=meta['moving_hasp'];objects=[o for o in sc.objects if o.type=='MESH' and o.get('full_form')]
yaw=Matrix.Rotation(math.radians(32),3,'Y');q=yaw@Vector((0,.48525,2));pivot=Vector((q.x,-q.z,q.y));q=yaw@Vector((1,0,0));axis=Vector((q.x,-q.z,q.y))
mesh={};digest=hashlib.sha256()
for o in objects:
 m=o.data;m.calc_loop_triangles();v=np.array([x.co[:] for x in m.vertices]);t=np.array([x.vertices[:] for x in m.loop_triangles],dtype=int);mesh[o.name]=(v,t);digest.update(o.name.encode());digest.update(v.tobytes());digest.update(t.tobytes())
sig=digest.hexdigest();path=C/'continuous_motion.json'
state=json.loads(path.read_text()) if path.exists() else {}
if state.get('geometry_sha256')!=sig:state=dict(geometry_sha256=sig,certified=False,method='Adaptive nearest surface distance minus triangle radius and angular displacement bound',tolerance=.00001,parts={},initial_containment_checked=False)
fixed=[n for n in mesh if n not in moving];trees={};FV=[];FT=[]
for n in fixed:
 v,t=mesh[n];trees[n]=BVHTree.FromPolygons(v.tolist(),t.tolist(),all_triangles=True,epsilon=1e-8);base=len(FV);FV.extend(v.tolist());FT.extend((t+base).tolist())
static=BVHTree.FromPolygons(FV,FT,all_triangles=True,epsilon=1e-8)
end=time.time()+75;count=0

def guard():
 global count
 count+=1
 if count%2000==0:
  s=json.loads((R/'schedule.json').read_text())
  if time.time()>end or s['status']!='active' or s['phase']!='work' or time.time()+10>s['work_until_epoch']:raise TimeoutError('Finite certification slice ended')
def inside(p,tree):
 votes=[];original_point=Vector(p)
 for direction in [(0.4123,.7237,.5541),(.8331,.2417,.4992),(.2711,.9123,.3087)]:
  d=Vector(direction).normalized();p=original_point.copy();hits=0
  for _ in range(100):
   loc,normal,index,dist=tree.ray_cast(p,d,100)
   if loc is None:break
   hits+=1;p=loc+d*.00002
  else:raise AssertionError('Ambiguous containment ray')
  votes.append(hits%2)
 assert len(set(votes))==1,('Ambiguous containment parity',votes)
 return bool(votes[0])

class NeedRefinement(Exception):pass
pose_start=0
def tri_bound(tri,need,depth=0):
 guard();
 if count-pose_start>50000:raise NeedRefinement()
 center=tri.mean(axis=0);radius=float(np.linalg.norm(tri-center,axis=1).max());loc,n,i,d=static.find_nearest(Vector(center));assert loc is not None
 bound=d-radius
 if bound>need:return bound
 if d<=need or depth>=24:return None
 edges=[(0,1,2),(1,2,0),(2,0,1)];i,j,k=max(edges,key=lambda q:np.linalg.norm(tri[q[0]]-tri[q[1]]));a,b,c=tri[i],tri[j],tri[k];mid=(a+b)*.5;result=1e9
 for small in [(a,mid,c),(mid,b,c)]:
  val=tri_bound(np.array(small),need,depth+1)
  if val is None:return None
  result=min(result,val)
 return result

pose_cache={}
def pose_bound(name,deg,need):
 global pose_start
 key=(name,deg,round(need,12))
 if key in pose_cache:return pose_cache[key]
 pose_start=count
 v,t=mesh[name];trans=Matrix.Translation(pivot)@Matrix.Rotation(-math.radians(deg),4,axis)@Matrix.Translation(-pivot);A=np.array(trans);vv=v@A[:3,:3].T+A[:3,3];result=1e9
 try:
  for tri in vv[t]:
   value=tri_bound(tri,need)
   if value is None:pose_cache[key]=None;return None
   result=min(result,value)
 except NeedRefinement:pose_cache[key]=None;return None
 pose_cache[key]=result;return result

try:
 if not state['initial_containment_checked']:
  for name in moving:
   v,t=mesh[name];mt=BVHTree.FromPolygons(v.tolist(),t.tolist(),all_triangles=True,epsilon=1e-8)
   for other in fixed:
    w,u=mesh[other]
    if np.any(v.max(0)<w.min(0)) or np.any(w.max(0)<v.min(0)):continue
    assert not mt.overlap(trees[other]),(name,other,'initial surface collision')
    assert not inside(v[0],trees[other]),(name,other,'moving part inside fixed')
    assert not inside(w[0],mt),(name,other,'fixed part inside moving')
  state['initial_containment_checked']=True
 # A bounding annular cylinder contains every rotated facet of the sleeve.
 # Certifying all fixed surfaces outside this envelope proves all sleeve angles.
 barrel='Chest Front Hasp Barrel'
 bp=state['parts'].setdefault(barrel,dict(pending=[[0.,60.]],certified_intervals=[],unresolved=[]))
 reuse=C/'sleeve_envelope_reuse.json'
 if reuse.exists() and not bp.get('rotation_envelope_certified'):
  saved=json.loads(reuse.read_text())
  def hash27(names):
   h=hashlib.sha256()
   for n in names:
    v,t=mesh[n];h.update(n.encode());h.update(v.tobytes());h.update(t.tobytes())
   return h.hexdigest()
  assert sorted(fixed)==saved['fixed_names']
  assert hash27(saved['fixed_names'])==saved['fixed_geometry_sha256']
  assert hash27([barrel])==saved['barrel_geometry_sha256']
  bp.update(saved['envelope_certificate']);bp['reuse_source']=saved['source'];path.write_text(json.dumps(state,indent=2))
 if not bp.get('rotation_envelope_certified'):
  inv=np.array(yaw.inverted());local=lambda v:np.c_[v[:,0],v[:,2],-v[:,1]]@inv.T-np.array([0,.48525,2.])
  v,t=mesh[barrel];lv=local(v);rr=np.linalg.norm(lv[:,1:],axis=1);angles=np.unique(np.round(np.mod(np.arctan2(lv[:,2],lv[:,1]),2*math.pi),5));gaps=np.diff(np.r_[angles,angles[0]+2*math.pi]);gap=float(gaps.max())
  # Measured duplicated angle noise cannot reduce the maximum angular sector.
  inner=float(rr.min()*math.cos((gap+.00002)/2))-.000002;outer=float(rr.max())+.000002;lo=float(lv[:,0].min())-.000002;hi=float(lv[:,0].max())+.000002
  assert inner>0 and gap<.11
  def envelope_bound(tri,depth=0):
   guard();xgap=max(lo-float(tri[:,0].max()),float(tri[:,0].min())-hi)
   if xgap>.00001:return xgap
   yz=tri[:,1:];rmax=float(np.linalg.norm(yz,axis=1).max());center=yz.mean(0);radius=float(np.linalg.norm(yz-center,axis=1).max());rmin=max(0,float(np.linalg.norm(center))-radius)
   gap=max(inner-rmax,rmin-outer)
   if gap>.00001:return gap
   if depth>=24:return None
   edges=[(0,1,2),(1,2,0),(2,0,1)];i,j,k=max(edges,key=lambda q:np.linalg.norm(tri[q[0]]-tri[q[1]]));a,b,c=tri[i],tri[j],tri[k];mid=(a+b)*.5
   one=envelope_bound(np.array([a,mid,c]),depth+1)
   if one is None:return None
   two=envelope_bound(np.array([mid,b,c]),depth+1)
   return min(one,two) if two is not None else None
  bound=1e9
  for other in fixed:
   v,t=mesh[other];triangles=local(v)[t]
   for tri in triangles:
    val=envelope_bound(tri)
    if val is None:raise AssertionError(('Sleeve envelope not certified against',other))
    bound=min(bound,val)
  bp.update(pending=[],unresolved=[],certified_intervals=[dict(start=0.,end=60.,clearance_lower_bound=bound)],rotation_envelope_certified=True,envelope=dict(inner_radius=inner,outer_radius=outer,x_min=lo,x_max=hi,maximum_measured_sector=gap))
  path.write_text(json.dumps(state,indent=2))
 for name in moving:
  part=state['parts'].setdefault(name,dict(pending=[[float(a),float(a+2.5)] for a in np.arange(0,60,2.5)],certified_intervals=[],unresolved=[]))
  v,t=mesh[name];rel=v-np.array(pivot);axisnp=np.array(axis);rad=float(np.linalg.norm(rel-(rel@axisnp)[:,None]*axisnp,axis=1).max());part['axis_radius_bound']=rad
  while part['pending']:
   guard();a,b=part['pending'][0];motion=2*rad*math.sin(math.radians(b-a)/4);need=motion+.00001
   left=pose_bound(name,a,need);right=pose_bound(name,b,need) if left is not None else None
   if left is not None and right is not None:
    part['certified_intervals'].append(dict(start=a,end=b,endpoint_lower_bound=min(left,right),nearest_endpoint_displacement_bound=motion,clearance_lower_bound=min(left,right)-motion));part['pending'].pop(0)
   elif b-a<=.01953125:
    part['unresolved'].append([a,b]);part['pending'].pop(0)
   else:
    mid=(a+b)/2;part['pending'][:1]=[[a,mid],[mid,b]]
   if len(part['certified_intervals'])%8==0:path.write_text(json.dumps(state,indent=2))
 state['certified']=all(not state['parts'][n]['pending'] and not state['parts'][n]['unresolved'] for n in moving)
except TimeoutError as e:state['slice_end']=str(e)
finally:
 state['nearest_queries']=state.get('nearest_queries',0)+count;state['updated_epoch']=time.time();path.write_text(json.dumps(state,indent=2))
print(json.dumps(dict(certified=state['certified'],parts={n:{k:len(p[k]) for k in ['pending','certified_intervals','unresolved']} for n,p in state['parts'].items()},nearest_queries=state['nearest_queries'])))
