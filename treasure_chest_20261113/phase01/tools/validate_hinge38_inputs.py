import json,numpy as np
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase01/candidate37');d=np.load(R/'geometry.npz');rows=json.loads((R/'validation.json').read_text())['checks'];lookup={r['name']:i for i,r in enumerate(rows)};a=np.deg2rad(32);rot=np.array([[np.cos(a),0,np.sin(a)],[0,1,0],[-np.sin(a),0,np.cos(a)]])
def tri(name):
 i=lookup[name];v=d[f'part{i}_v']@rot;return v[d[f'part{i}_t']]
def inside(T,p):
 ans=[]
 for ray in [[.93,.21,.3],[-.23,.89,.34],[.27,.31,.91]]:
  ray=np.array(ray);ray/=np.linalg.norm(ray);E=T[:,1]-T[:,0];F=T[:,2]-T[:,0];h=np.cross(np.broadcast_to(ray,F.shape),F);det=np.einsum('ij,ij->i',E,h);valid=abs(det)>1e-14;inv=np.divide(1.,det,out=np.zeros_like(det),where=valid);S=p-T[:,0];u=np.einsum('ij,ij->i',S,h)*inv;Q=np.cross(S,E);v=Q@ray*inv;dist=np.einsum('ij,ij->i',F,Q)*inv;hit=valid&(u>=0)&(v>=0)&(u+v<=1)&(dist>1e-7);vals=np.sort(dist[hit]);count=int(np.r_[True,np.diff(vals)>1e-6].sum()) if len(vals) else 0;ans.append(bool(count%2))
 assert len(set(ans))==1,(p,ans)
 return ans[0]

def clip(poly,axis,limit,greater):
 out=[]
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  da=(a[axis]-limit)*(1 if greater else -1);db=(b[axis]-limit)*(1 if greater else -1)
  if da>=0:out.append(a)
  if (da>=0)!=(db>=0):out.append(a+(b-a)*da/(da-db))
 return np.array(out)
slots=[(sx*1.55+a,sx*1.55+b) for sx in (-1,1) for a,b in [(-.184,-.061),(.061,.184)]]
T=tri('Chest Body Upper Rim');points=[]
for low,high in slots:
 for face in T:
  q=clip(face,0,low,True)
  if len(q):q=clip(q,0,high,False)
  if len(q):points.extend(q)
points=np.array(points);minimum_back_clearance=float(points[:,2].min()+1.930);assert minimum_back_clearance>.120+.02,minimum_back_clearance
negative=T.copy();negative[:,:,2]-=.08;intruders=[]
for sx in (-1,1):
 for offset in (-.1225,.1225):
  x=sx*1.55+offset
  for scale in (.6,.8,.95,.999):
   for phi in np.arange(64)*2*np.pi/64:
    p=np.array([x,.36175+.114*scale*np.cos(phi),-1.93+.120*scale*np.sin(phi)])
    if inside(negative,p):intruders.append(p.tolist())
assert intruders,'Body collision negative control failed to produce real intrusion'
# The current lid must not be accepted without its actual fixed sleeve seats.
T=tri('Chest Upper Lid Rim');known=np.array([1.55,.41175,-1.830]);assert inside(T,known),'Missing lid relief control did not observe the real current obstruction'
report=dict(body_frame_minimum_back_distance_in_moving_slots=minimum_back_clearance,maximum_moving_sleeve_radius=.120,guaranteed_back_coordinate_gap=minimum_back_clearance-.120,body_frame_relief_required=False,actual_deliberately_intruding_body_sample_count=len(intruders),intruder_samples=intruders[:6],missing_lid_relief_actual_containment=True,nominal_bore_radius=.056,minimum_polygonal_bore_radius=float(.056*np.cos(np.pi/64)),minimum_pin_clearance=float(.056*np.cos(np.pi/64)-.050),minimum_running_cut_radius=float(.126*np.cos(np.pi/64)),minimum_running_sleeve_clearance=float(.126*np.cos(np.pi/64)-.120),model_modified=False)
print(json.dumps(report,indent=2));Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase01/hinge38/input_validation.json').write_text(json.dumps(report,indent=2))
