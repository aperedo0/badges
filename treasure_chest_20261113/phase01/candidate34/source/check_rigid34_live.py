import bpy,json,hashlib,numpy as np,math
from pathlib import Path
from mathutils import Matrix
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate34';sc=bpy.context.scene
meta=json.loads((P/'candidate33/validation.json').read_text());base=np.load(P/'candidate33/geometry.npz');oldnorm=np.load(C/'baseline33_normals.npz');moved=json.loads((C/'rigid_arch_parts.json').read_text())['parts'];assert len(moved)==16 and len(set(moved))==16
rot=np.array(Matrix.Rotation(math.radians(32),3,'Y'));inv=rot.T;rows=[];joins=[]
for i,row in enumerate(meta['checks']):
 ob=sc.objects[row['name']];me=ob.data;me.calc_loop_triangles();a=np.array([v.co[:] for v in me.vertices]);v=np.c_[a[:,0],a[:,2],-a[:,1]];t=np.array([f.vertices[:] for f in me.loop_triangles]);old=base[f'part{i}_v'];assert np.array_equal(t,base[f'part{i}_t']),(ob.name,'topology changed')
 delta=np.zeros(3)
 if ob.name in moved:
  sx=-1 if float((old@inv.T)[:,0].mean())<0 else 1;delta=rot@np.array([-sx*.040,0,0])
 assert v.shape==old.shape,(ob.name,'vertex count')
 error=float(np.max(abs(v-(old+delta))));assert error<1e-6,(ob.name,'not the exact rigid change',error)
 normals=np.array([n.vector[:] for n in me.corner_normals]);assert np.isfinite(normals).all();nd=float(np.max(abs(normals-oldnorm[f'n{i}'])));assert nd<2e-5,(ob.name,'normal changed',nd)
 rows.append(dict(name=ob.name,moved=ob.name in moved,maximum_coordinate_error=error,maximum_normal_error=nd))
 if ob.name.startswith('Chest Broad End Arch'):
  q=v@inv.T;q[:,1]=(q[:,1]+.12275)/.95;points=[]
  for tri in q[t]:
   if tri[:,1].min()>1.15 or tri[:,1].max()<1.15:continue
   for a,b in [(tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])]:
    if abs(a[1]-1.15)<1e-7:points.append(a)
    if (a[1]-1.15)*(b[1]-1.15)<0:points.append(a+(b-a)*((1.15-a[1])/(b[1]-a[1])))
  assert points,ob.name
  actual=float(np.max(abs(np.array(points)[:,0])));assert actual<=2.716,(ob.name,'join still exposed',actual)
  assert actual+.040>2.716,'Unmoved arch negative control not rejected'
  joins.append(dict(name=ob.name,actual_join_maximum_x=actual,cap_toe_clearance=2.725-actual,unmoved_arch_rejected=True))
for rel,sha in json.loads((C/'baseline33_hashes.json').read_text()).items():assert hashlib.sha256((P/'candidate33'/rel).read_bytes()).hexdigest()==sha,'Baseline33 overwritten '+rel
report=dict(moved=16,unchanged=143,all_normals_unchanged=True,joins=joins,parts=rows,baseline33_files_unchanged=True);(C/'rigid_fit_proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='parts'}))
