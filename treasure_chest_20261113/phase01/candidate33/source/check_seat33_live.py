import bpy,json,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate33';sc=bpy.context.scene;inv=np.array(Matrix.Rotation(math.radians(32),3,'Y').inverted());yaw=np.array(Matrix.Rotation(math.radians(32),3,'Y'))
def local(ob):
 a=np.array([v.co[:] for v in ob.data.vertices]);return np.c_[a[:,0],a[:,2],-a[:,1]]@inv.T
def world(q):
 p=yaw@np.array(q);return Vector((p[0],-p[2],p[1]))
base=np.load(P/'candidate31/geometry.npz');meta=json.loads((P/'candidate31/validation.json').read_text());changed={f'Chest Boot {face} Rivet {sx} {sz} Seat' for face in ['Front','End'] for sx in (-1,1) for sz in (-1,1)}
unchanged=[]
for i,row in enumerate(meta['checks']):
 name=row['name']
 if name in changed:continue
 ob=sc.objects[name];a=np.array([v.co[:] for v in ob.data.vertices]);v=np.c_[a[:,0],a[:,2],-a[:,1]];old=base[f'part{i}_v']
 assert v.shape==old.shape,(name,'vertex count changed')
 delta=float(np.max(abs(v-old)));assert delta<.000001,(name,'unrelated geometry changed',delta)
 unchanged.append({'name':name,'maximum_coordinate_difference':delta})
seats=[]
for sx in (-1,1):
 for sz in (-1,1):
  for face in ['Front','End']:
   name=f'Chest Boot {face} Rivet {sx} {sz}';head=sc.objects[name];seat=sc.objects[name+' Seat'];target=sc.objects[f'Chest Angular Boot {sx} {sz}'];n=np.array((0,0,sz) if face=='Front' else (sx,0,0),float);v=local(head);w=local(seat);p=v.mean(0);p+=n*(float((v@n).max())-float(p@n)+.3);hit,point,nn,index=target.ray_cast(world(p),-world(n));assert hit,name
   q=np.array([point.x,point.z,-point.y])@inv.T;surface=float(q@n);front=float((w@n).max())-surface;back=surface-float((w@n).min());axis=0 if face=='Front' else 2;ratio=float(np.ptp(w[:,axis])/np.ptp(v[:,axis]))
   assert abs(front-.009)<.0001 and back>=.001 and abs(ratio-1.10)<.0001,(name,front,back,ratio)
   seats.append({'head':name,'front_exposure':front,'back_overlap':back,'radial_ratio':ratio})
arches=[]
for rel,sha in json.loads((C/'baseline31_hashes.json').read_text()).items():assert hashlib.sha256((P/'candidate31'/rel).read_bytes()).hexdigest()==sha,'Baseline overwritten: '+rel
(C/'seat_only33_proof.json').write_text(json.dumps({'seats':seats,'arches':arches,'unchanged_meshes':unchanged,'candidate31_files_unchanged':True},indent=2)+'\n')
print(json.dumps({'seats_passed':len(seats),'arch_joins':arches,'unrelated_meshes_unchanged':len(unchanged),'candidate31_preserved':True}))
