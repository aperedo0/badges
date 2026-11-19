import numpy as np,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=R/'phase01';C=P/'candidate39';B=P/'candidate38';data=np.load(B/'geometry.npz');rows=json.loads((B/'validation.json').read_text())['checks'];lookup={r['name']:i for i,r in enumerate(rows)};a=math.radians(32);rot=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
def tri(name):
 i=lookup[name];v=data[f'part{i}_v']@rot;return v[data[f'part{i}_t']]
def clip(poly,axis,limit,greater):
 out=[]
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  da=(a[axis]-limit)*(1 if greater else -1);db=(b[axis]-limit)*(1 if greater else -1)
  if da>=0:out.append(a)
  if (da>=0)!=(db>=0):out.append(a+(b-a)*da/(da-db))
 return np.array(out)
def polygons(T,lo,hi):
 possible=T[(T[:,:,0].max(1)>=lo)&(T[:,:,0].min(1)<=hi)]
 for f in possible:
  q=clip(f,0,lo,True)
  if len(q):q=clip(q,0,hi,False)
  if len(q):yield q

def radius_min(T,lo,hi,axis=np.array([.36175,-1.930])):
 best=float('inf')
 for q in polygons(T,lo,hi):
  yz=q[:,1:]-axis;area=np.cross(yz,np.roll(yz,-1,axis=0)).sum();cross=np.cross(np.roll(yz,-1,axis=0)-yz,-yz)
  if abs(area)>1e-18 and (np.all(cross>=-1e-18) or np.all(cross<=1e-18)):best=0.;continue
  for A,B in zip(yz,np.roll(yz,-1,axis=0)):
   E=B-A;u=np.clip(-np.dot(A,E)/np.dot(E,E),0,1) if E@E>1e-24 else 0;best=min(best,float(np.linalg.norm(A+u*E)))
 return best

def inside(T,p):
 ans=[]
 for ray in ([.93,.21,.3],[-.23,.89,.34],[.27,.31,.91]):
  ray=np.array(ray);ray/=np.linalg.norm(ray);E=T[:,1]-T[:,0];F=T[:,2]-T[:,0];h=np.cross(np.broadcast_to(ray,F.shape),F);det=np.einsum('ij,ij->i',E,h);valid=abs(det)>1e-14;inv=np.divide(1.,det,out=np.zeros_like(det),where=valid);S=p-T[:,0];u=np.einsum('ij,ij->i',S,h)*inv;Q=np.cross(S,E);v=Q@ray*inv;dist=np.einsum('ij,ij->i',F,Q)*inv;hit=valid&(u>=0)&(v>=0)&(u+v<=1)&(dist>1e-7);d=np.sort(dist[hit]);count=int(np.r_[True,np.diff(d)>1e-6].sum()) if len(d) else 0;ans.append(bool(count%2))
 assert len(set(ans))==1,(p.tolist(),ans)
 return ans[0]
fixed=[(-.300,-.190),(-.055,.055),(.190,.300)];moving=[(-.178,-.067),(.067,.178)];proof=[];frame=tri('Chest Upper Lid Rim')
for side in (-1,1):
 cx=side*1.55
 for role,slots,other in [('Lower',fixed,moving),('Upper',moving,fixed)]:
  name=f'Chest Rear Hinge {role} {side}';T=tri(name)
  for a,b in slots:
   lo=cx+a+.004;hi=cx+b-.004;r=radius_min(T,lo,hi);p=np.array([cx+(a+b)/2,.36175,-1.93]);assert not inside(T,p),(name,'filled bore');assert r>=.055930,(name,'bore too small',r);assert r<=.055936,(name,'wrong bore',r);proof.append(dict(name=name,slot=[a,b],bore_minimum_radius=r,axis_empty=True))
  for a,b in other:
   r=radius_min(T,cx+a,cx+b);assert r>=.125845,(name,'opposite sleeve root obstruction',r);proof.append(dict(name=name,other_slot=[a,b],minimum_running_radius=r,minimum_outer_ellipse_gap=r-.120))
 for a,b in fixed:
  r=radius_min(frame,cx+a,cx+b);assert r>=.125845,('Lid frame lacks actual sleeve clearance',side,a,b,r);proof.append(dict(name='Chest Upper Lid Rim',side=side,slot=[a,b],minimum_running_radius=r))
 pin=tri(f'Chest Rear Hinge Barrel {side}');points=np.vstack(list(polygons(pin,cx-.300,cx+.300)));rmax=float(np.linalg.norm(points[:,1:]-[.36175,-1.93],axis=1).max());assert rmax<=.050002 and rmax>=.049998;assert inside(pin,np.array([cx,.36175,-1.93]));proof.append(dict(name=f'Chest Rear Hinge Barrel {side}',actual_shaft_maximum_radius=rmax,positive_solid_shaft=True))
# Actual failed old frame versus actual newly built fixed sleeve.
old=np.load(P/'candidate37/geometry.npz');oldrows=json.loads((P/'candidate37/validation.json').read_text())['checks'];oldids={r['name']:i for i,r in enumerate(oldrows)}
def oldtri(name):
 i=oldids[name];return (old[f'part{i}_v']@rot)[old[f'part{i}_t']]
p=np.array([1.55,.41175,-1.830]);assert inside(oldtri('Chest Upper Lid Rim'),p) and inside(tri('Chest Rear Hinge Lower 1'),p);assert not inside(frame,p)
body_bad=oldtri('Chest Body Upper Rim').copy();body_bad[:,:,2]-=.08;intruders=json.loads((P/'hinge38/input_validation.json').read_text())['intruder_samples'];observed=[q for q in intruders if inside(body_bad,np.array(q)) and inside(tri('Chest Rear Hinge Upper -1'),np.array(q))];assert observed,'Actual body collision negative control did not collide'
# A real solid cube filling a bore must fail both axis and minimum radius tests.
cx=1.55;V=np.array([[cx+x,.36175+y,-1.93+z] for x,y,z in [(-.01,-.01,-.01),(.01,-.01,-.01),(.01,.01,-.01),(-.01,.01,-.01),(-.01,-.01,.01),(.01,-.01,.01),(.01,.01,.01),(-.01,.01,.01)]]);F=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]);filled=np.concatenate([tri('Chest Rear Hinge Lower 1'),V[F]]);assert inside(filled,np.array([cx,.36175,-1.93]));assert radius_min(filled,cx-.02,cx+.02)<.05
wrong=radius_min(tri('Chest Rear Hinge Lower 1'),cx-.04,cx+.04,axis=np.array([.38175,-1.93]));assert wrong<.05
report=dict(actual_geometry_checked=True,regions=proof,negative_controls=dict(missing_lid_frame_relief_rejected=True,deliberately_intruding_body_rejected=True,filled_bore_rejected=True,offset_axis_rejected=True),minimum_polygonal_pin_gap=min(r['bore_minimum_radius'] for r in proof if 'bore_minimum_radius' in r)-max(r['actual_shaft_maximum_radius'] for r in proof if 'actual_shaft_maximum_radius' in r),full_motion_screen_pending=True);C.mkdir(exist_ok=True);(C/'actual_hinge_geometry_proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(regions=len(proof),minimum_pin_gap=report['minimum_polygonal_pin_gap'],negative_controls=report['negative_controls'])))
