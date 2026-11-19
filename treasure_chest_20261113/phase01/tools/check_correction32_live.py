import bpy,json,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate32';sc=bpy.context.scene;inv=np.array(Matrix.Rotation(math.radians(32),3,'Y').inverted());yaw=np.array(Matrix.Rotation(math.radians(32),3,'Y'))
def local(ob):
 a=np.array([v.co[:] for v in ob.data.vertices]);return np.c_[a[:,0],a[:,2],-a[:,1]]@inv.T
def world(q):
 p=yaw@np.array(q);return Vector((p[0],-p[2],p[1]))
base=np.load(P/'candidate31/geometry.npz');meta=json.loads((P/'candidate31/validation.json').read_text());changed={f'Chest Boot {face} Rivet {sx} {sz} Seat' for face in ['Front','End'] for sx in (-1,1) for sz in (-1,1)}|{f'Chest Broad End Arch {sx}' for sx in (-1,1)}
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
for sx in (-1,1):
 name=f'Chest Broad End Arch {sx}';ob=sc.objects[name];q=local(ob);q[:,1]=(q[:,1]+.12275)/.95;ob.data.calc_loop_triangles();T=np.array([f.vertices[:] for f in ob.data.loop_triangles]);points=[]
 for tri in q[T]:
  if tri[:,1].min()>1.15 or tri[:,1].max()<1.15:continue
  for a,b in [(tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])]:
   if abs(a[1]-1.15)<1e-7:points.append(a)
   if (a[1]-1.15)*(b[1]-1.15)<0:points.append(a+(b-a)*((1.15-a[1])/(b[1]-a[1])))
 assert points,name+' no actual join section'
 maximum=float(np.max(np.array(points)[:,0]*sx));assert maximum<=2.721,(name,'arch still protrudes over cap toe',maximum)
 i=next(i for i,r in enumerate(meta['checks']) if r['name']==name);old=base[f'part{i}_v']@inv.T;old[:,1]=(old[:,1]+.12275)/.95;assert len(q)==len(old)
 mask=old[:,1]>=1.55;delta=float(np.max(abs(q[mask]-old[mask])));assert delta<.000001,(name,'upper arch changed',delta)
 assert np.isfinite(np.array([n.vector[:] for n in ob.data.corner_normals])).all(),name+' invalid normal'
 arches.append({'side':sx,'actual_join_maximum_x':maximum,'cap_toe_clearance':2.725-maximum,'upper_arch_maximum_difference':delta})
for rel,sha in json.loads((C/'baseline31_hashes.json').read_text()).items():assert hashlib.sha256((P/'candidate31'/rel).read_bytes()).hexdigest()==sha,'Baseline overwritten: '+rel
(C/'correction32_proof.json').write_text(json.dumps({'seats':seats,'arches':arches,'unchanged_meshes':unchanged,'candidate31_files_unchanged':True},indent=2)+'\n')
print(json.dumps({'seats_passed':len(seats),'arch_joins':arches,'unrelated_meshes_unchanged':len(unchanged),'candidate31_preserved':True}))
