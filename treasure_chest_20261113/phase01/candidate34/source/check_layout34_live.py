import bpy,json,hashlib,numpy as np,math
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate34';sc=bpy.context.scene
meta=json.loads((P/'candidate33/validation.json').read_text());base=np.load(P/'candidate33/geometry.npz');oldnorm=np.load(C/'baseline33_normals.npz');layout=json.loads((C/'layout_changes.json').read_text());moved=layout['translations'];rot=np.array(Matrix.Rotation(math.radians(32),3,'Y'));inv=rot.T;rows=[]
def local34(ob):
 a=np.array([v.co[:] for v in ob.data.vertices]);v=np.c_[a[:,0],a[:,2],-a[:,1]]@inv.T;v[:,1]=(v[:,1]+.12275)/.95;return v
def bvh34(ob):
 me=ob.data;me.calc_loop_triangles();return BVHTree.FromPolygons([v.co[:] for v in me.vertices],[t.vertices[:] for t in me.loop_triangles],all_triangles=True,epsilon=0)
def center34(name):
 v=local34(sc.objects[name]);return (v.min(0)+v.max(0))/2
for i,row in enumerate(meta['checks']):
 name=row['name'];ob=sc.objects[name]
 if name in layout['hide']:
  assert not ob.get('full_form') and ob.hide_render;continue
 assert ob.get('full_form') and not ob.hide_render,name
 me=ob.data;me.calc_loop_triangles();a=np.array([v.co[:] for v in me.vertices]);v=np.c_[a[:,0],a[:,2],-a[:,1]];t=np.array([f.vertices[:] for f in me.loop_triangles]);old=base[f'part{i}_v'];assert np.array_equal(t,base[f'part{i}_t']),(name,'topology changed')
 d=np.array(moved.get(name,[0,0,0]),float);d[1]*=.95;delta=rot@d
 error=float(np.max(abs(v-(old+delta))));assert error<1e-6,(name,'not the intended rigid change',error)
 normals=np.array([n.vector[:] for n in me.corner_normals]);assert np.isfinite(normals).all();nd=float(np.max(abs(normals-oldnorm[f'n{i}'])));den=np.linalg.norm(normals,axis=1)*np.linalg.norm(oldnorm[f'n{i}'],axis=1);angle=float(np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i',normals,oldnorm[f'n{i}'])/den,-1,1))).max());assert angle<(.75 if name.startswith('Chest Measured Rolled Handle Cover') else (.15 if name in moved else .001)),(name,'normal angle changed',angle,nd)
 rows.append(dict(name=name,moved=name in moved,maximum_coordinate_error=error,maximum_normal_error=nd,maximum_normal_degrees=angle))
assert len(rows)==158 and sum(r['moved'] for r in rows)==43
centers=[]
for sx in (-1,1):
 q=local34(sc.objects[f'Chest Broad End Arch {sx}']);top=q[q[:,1]>q[:,1].max()-1e-5];centers.append(float((top[:,0].min()+top[:,0].max())/2))
centers=sorted(centers+[float(center34('Chest Lid Hoop 2')[0]),float(center34('Chest Lid Hoop 3')[0])]);gaps=np.diff(centers);assert max(abs(np.array(centers)+np.array(centers)[::-1]))<1e-5;assert np.ptp(gaps)<1e-5,(centers,gaps)
assert abs(-1.20+.85)>1e-5,'Old asymmetric band negative control failed'
rear=[]
for sx,j in [(-1,0),(1,1)]:
 head=sc.objects[f'Chest Rail Rivet -1 {j}'];q=local34(head);plate=local34(sc.objects[f'Chest Rear Hinge Upper {sx}']);head_out=float((q[:,0]*sx).max());plate_in=float((plate[:,0]*sx).min());gap=plate_in-head_out;assert gap>=.070,(j,'head crowds hinge',gap)
 assert abs(center34(head.name)[1]-.735)<1e-5;rear.append(dict(name=head.name,lateral_gap=gap))
assert 1.27-(1.235+.074)<.070,'Old clipped rear head negative control failed'
for sz in (-1,1):
 for pair in [(f'Chest Rail Rivet {sz} 0',f'Chest Rail Rivet {sz} 1'),(f'Chest Rail Rivet {sz} 3',f'Chest Rail Rivet {sz} 4'),(f'Chest Body Lip Rivet {sz} 0',f'Chest Body Lip Rivet {sz} 1')]:
  a,b=map(center34,pair);assert abs(a[0]+b[0])<1e-5 and abs(a[1]-b[1])<1e-5,(pair,a,b)
handles=[]
for sx in (-1,1):
 plate=sc.objects[f'Chest Handle Mount {sx}'];ring=sc.objects[f'Chest Solid Ring Handle {sx}'];cover=sc.objects[f'Chest Measured Rolled Handle Cover {sx}'];q=local34(plate);assert abs((q[:,2].min()+q[:,2].max())/2)<1e-5
 for ob in (ring,cover):
  v=local34(ob);assert abs((v[:,2].min()+v[:,2].max())/2)<.0002,(ob.name,'not centered',v[:,2].min(),v[:,2].max())
 assert not bvh34(ring).overlap(bvh34(plate)),(sx,'ring crosses plate');assert not bvh34(ring).overlap(bvh34(cover)),(sx,'ring crosses cover')
 heads=[center34(f'Chest Handle Mount Rivet {sx} {sz}') for sz in (-1,1)];assert abs(heads[0][2]+heads[1][2])<1e-5
 # Root probes on actual completed cover must remain at or behind the plate surface.
 root=[]
 for y in [-.020,-.200,-.440]:
  for z in [-.20,0,.20]:
   p=rot@np.array([sx*2.780,.95*y-.12275,z]);d=rot@np.array([sx,0,0]);A=Vector((p[0],-p[2],p[1]));D=Vector((d[0],-d[2],d[1]));hit,pt,nn,index=cover.ray_cast(A,D);assert hit,(cover.name,'missing root support',y,z);q=np.array([pt.x,pt.z,-pt.y])@inv.T;assert abs(q[0])<=2.81001,(cover.name,'root floats',q[0]);root.append(float(q[0]))
 handles.append(dict(side=sx,centered=True,ring_plate_intersections=0,ring_cover_intersections=0,root_support_x=root))
positive=local34(sc.objects['Chest Rail Rivet 1 2']);negative=local34(sc.objects[layout['new_front_small']]);mirror=positive.copy();mirror[:,0]*=-1
assert len(negative)==len(mirror);dist=np.linalg.norm(negative[:,None,:]-mirror[None,:,:],axis=2);assert dist.min(1).max()<1e-5,'New front small head not mirror'
for ob in [sc.objects['Chest Rail Rivet 1 2'],sc.objects[layout['new_front_small']]]:
 q=local34(ob);assert q[:,2].min()<1.840 and q[:,2].max()>1.840,'Small head missing real base overlap'
for sx in (-1,1):
 for k in (0,1):assert abs(center34(f'Chest End Rail Rivet {sx} {k}')[2])<1e-5
for rel,sha in json.loads((C/'baseline33_hashes.json').read_text()).items():assert hashlib.sha256((P/'candidate33'/rel).read_bytes()).hexdigest()==sha,'Baseline33 overwritten '+rel
report=dict(moved=43,unchanged=115,hidden=layout['hide'],new=layout['new_front_small'],band_land_centers=centers,band_center_intervals=gaps.tolist(),rear_rivet_clearance=rear,handles=handles,parts=rows,baseline33_files_unchanged=True);(C/'layout_proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='parts'}))
