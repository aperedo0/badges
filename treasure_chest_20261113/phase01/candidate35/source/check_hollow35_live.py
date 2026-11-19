import bpy,numpy as np,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate35';sc=bpy.context.scene;Y35=np.array(Matrix.Rotation(math.radians(32),3,'Y'));I35=Y35.T
hash35=lambda a:hashlib.sha256(np.asarray(a).tobytes()).hexdigest()
def local35(a):
 a=np.asarray(a);return np.c_[a[:,0],a[:,2],-a[:,1]]@I35.T

def vector35(q):
 a=Y35@np.asarray(q,float);return Vector((a[0],-a[2],a[1]))

def arrays35(ob):
 me=ob.data;me.calc_loop_triangles();return np.array([v.co[:] for v in me.vertices]),np.array([t.vertices[:] for t in me.loop_triangles]),np.array([n.vector[:] for n in me.corner_normals])

def volume35(v,t):return float(np.einsum('ij,ij->i',v[t[:,0]],np.cross(v[t[:,1]],v[t[:,2]])).sum()/6)

def topology35(name,v,t):
 edges,counts=np.unique(np.sort(np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]),axis=1),axis=0,return_counts=True);assert (counts==2).all(),(name,'open solid')
 assert len(np.unique(np.sort(t,axis=1),axis=0))==len(t),(name,'duplicate triangles')
 areas=np.linalg.norm(np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]),axis=1)/2;assert areas.min()>1e-10,(name,'degenerate face',areas.min());chi=len(np.unique(t))-len(edges)+len(t);assert chi==2,(name,'wrong shell topology',chi)
 parents={int(i):int(i) for i in np.unique(t)}
 def root(i):
  while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
  return i
 for a,b in edges:
  a,b=root(int(a)),root(int(b))
  if a!=b:parents[b]=a
 assert len({root(i) for i in parents})==1,(name,'disconnected inner shell')
 vol=volume35(v,t);assert vol>0,(name,'negative volume');return dict(closed=True,connected=True,euler_characteristic=int(chi),positive_volume=vol,triangles=len(t))

trim_stage=json.loads((C/'trim_stage.json').read_text());trim_old=np.load(C/'trim_old.npz');trim_targets=np.load(C/'trim_normal_targets.npz');
manifest=json.loads((C/'before_manifest.json').read_text());stage=json.loads((C/'hollow_stage.json').read_text());coremeta=json.loads((C/'core_before.json').read_text());core=np.load(C/'core_before.npz');base34=np.load(P/'candidate34/geometry.npz');meta34=json.loads((P/'candidate34/validation.json').read_text());rows=[];allv=[];total=0;unchanged=0;trees={};modified={};packed={}
for i,row in enumerate(meta34['checks']):
 name=row['name'];ob=sc.objects[name];assert ob.get('full_form') and not ob.hide_render,name;v,t,n=arrays35(ob);assert np.isfinite(n).all();assert np.max(abs(np.array(ob.matrix_world)-np.eye(4)))<1e-7,(name,'rest transform');allv.append(v);total+=len(t);app=np.c_[v[:,0],v[:,2],-v[:,1]];packed[f'part{i}_v']=app;packed[f'part{i}_t']=t
 if name in trim_stage:
  assert len(ob.data.materials)==1 and ob.data.materials[0] is not None and all(f.material_index==0 for f in ob.data.polygons),(name,'cut introduced an invalid material slot')
  proof=topology35(name,v,t);oldv=trim_old[name+' v'];oldt=trim_old[name+' t'];oldtree=BVHTree.FromPolygons(oldv.tolist(),oldt.tolist(),all_triangles=True,epsilon=0);newtree=BVHTree.FromPolygons(v.tolist(),t.tolist(),all_triangles=True,epsilon=0)
  def outside_cut35(points):
   q=local35(points);lo=np.array([-2.34,-2.0275,-1.39]);hi=np.array([2.34,.46,1.39]);return ((q<lo-1e-5)|(q>hi+1e-5)).any(1)
  oldsamples=np.vstack([oldv,oldv[oldt].mean(1)]);new_samples=np.vstack([v,v[t].mean(1)]);maximum=0.
  for points,tree in [(oldsamples[outside_cut35(oldsamples)],newtree),(new_samples[outside_cut35(new_samples)],oldtree)]:
   for q in points:
    hit,normal,index,distance=tree.find_nearest(Vector(q));assert hit is not None and distance<.0006,(name,'exterior surface changed',distance);maximum=max(maximum,distance)
  target=trim_targets[name];assert n.shape==target.shape;den=np.linalg.norm(n,axis=1)*np.linalg.norm(target,axis=1);angles=np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i',n,target)/den,-1,1)));assert max(angles)<.75,(name,'transferred surface shading changed',max(angles))
  matched=trim_targets[name+' matched'];loop_points=v[np.array([loop.vertex_index for loop in ob.data.loops])];assert matched[outside_cut35(loop_points)].all(),(name,'exterior normal not transferred')
  oldvolume=volume35(oldv,oldt);assert 0<proof['positive_volume']<oldvolume,(name,'trim volume invalid')
  proof.update(name=name,concealed_corner_trim=True,exterior_maximum_surface_error=maximum,maximum_normal_encoding_degrees=float(max(angles)),removed_volume=oldvolume-proof['positive_volume']);rows.append(proof);modified[name]=proof;continue
 if name not in stage:
  for key,a in [('vertex_hash',v),('triangle_hash',t),('normal_hash',n)]:assert hash35(a)==manifest[name][key],(name,'unrelated data changed',key)
  unchanged+=1;rows.append(dict(name=name,unchanged=True,triangles=len(t)));continue
 d=stage[name];label='body' if d['kind']=='body' else 'lid';oldv=core[label+'_v'];oldn=core[label+'_n'];assert np.array_equal(v[:len(oldv)],oldv),(name,'exterior vertices changed');me=ob.data;angles=[];oldloops=np.cumsum([0]+[len(f) for f in coremeta[name]['faces']])
 for oldidx,newidx in d['retained']:
  f=me.polygons[newidx];assert list(f.vertices)==coremeta[name]['faces'][oldidx],(name,'exterior face changed',oldidx);a=coremeta[name]['attrs'][oldidx];assert f.use_smooth==a['smooth'] and f.material_index==a['material'],(name,'exterior attributes changed')
  A=n[list(f.loop_indices)];B=oldn[oldloops[oldidx]:oldloops[oldidx+1]];den=np.linalg.norm(A,axis=1)*np.linalg.norm(B,axis=1);angle=np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i',A,B)/den,-1,1)));angles.extend(angle.tolist())
 assert max(angles)<.15,(name,'exterior normal changed',max(angles));proof=topology35(name,v,t);oldvolume=volume35(oldv,base34[f'part{i}_t']);removed=oldvolume-proof['positive_volume']
 if label=='body':expected=(2*2.33)*(2*1.38)*(d['level']+2.0175)
 else:
  q=np.array(d['inner']);area=abs(np.cross(q,np.roll(q,-1,axis=0)).sum())/2;expected=area*(2*2.38)
 assert abs(removed-expected)<2e-5,(name,'cavity volume does not match',removed,expected)
 proof.update(name=name,old_outer_vertices_unchanged=True,retained_outer_faces=len(d['retained']),exterior_maximum_normal_degrees=max(angles),removed_volume=removed,expected_cavity_volume=expected);modified[name]=proof;rows.append(proof);trees[name]=BVHTree.FromPolygons(v.tolist(),t.tolist(),all_triangles=True,epsilon=0)
assert unchanged==149

def ray35(name,start,direction):
 p,n,idx,dist=trees[name].ray_cast(vector35(start),vector35(direction).normalized(),50);assert p is not None,(name,'missing cavity surface',start,direction);return local35([p])[0],local35([n])[0]

def inside35(name,point):
 result=[]
 for d in ([.93,.21,.30],[-.23,.89,.34],[.27,.31,.91]):
  direction=vector35(d).normalized();origin=vector35(point);hits=0;travel=0
  for _ in range(40):
   p,n,idx,dist=trees[name].ray_cast(origin,direction,50-travel)
   if p is None:break
   hits+=1;travel+=dist+1e-5;origin=p+direction*1e-5
  else:raise AssertionError((name,'parity ray did not leave solid'))
  result.append(hits%2==1)
 assert len(set(result))==1,(name,'ambiguous containment',point,result);return result[0]

samples=[('Chest Body Envelope',(0,-1,0),False),('Chest Body Envelope',(0,-2.1175,0),True),('Chest Body Envelope',(2.44,-1,0),True),('Chest Body Envelope',(0,-1,1.49),True),('Chest Barrel Lid Envelope',(0,1,0),False),('Chest Barrel Lid Envelope',(0,2.23825,0),True),('Chest Barrel Lid Envelope',(2.49,1,0),True)]
for name,p,expected in samples:assert inside35(name,p)==expected,(name,'wrong hollow containment',p,expected)
pt,n=ray35('Chest Body Envelope',[0,1,0],[0,-1,0]);assert abs(pt[1]+2.0175)<1e-5 and n[1]>.99,('body floor missing/inverted',pt,n)
pt,n=ray35('Chest Barrel Lid Envelope',[0,0,0],[0,1,0]);assert abs(pt[1]-2.14825)<1e-5 and n[1]<-.99,('lid inner roof missing/inverted',pt,n)
# The old filled source must fail the same cavity containment test.
negative=[]
for label,name,point in [('body','Chest Body Envelope',[0,-1,0]),('lid','Chest Barrel Lid Envelope',[0,1,0])]:
 i=next(i for i,r in enumerate(meta34['checks']) if r['name']==name);saved=trees[name];trees[name]=BVHTree.FromPolygons(core[label+'_v'].tolist(),base34[f'part{i}_t'].tolist(),all_triangles=True,epsilon=0);assert inside35(name,point),'Solid old source not rejected';trees[name]=saved;negative.append(dict(name=name,old_solid_rejected=True))
inventory35={'CAVITY35_INVENTORY_OUTPUT':'intrusion_inventory_after.json'}
exec(compile((P/'tools/cavity35_inventory_live.py').read_text(),'actual_cavity_inventory35.py','exec'),inventory35)
assert not inventory35['rows'],('Hardware remains in empty cavity',inventory35['rows'])
V=np.vstack(allv);app=np.c_[V[:,0],V[:,2],-V[:,1]];turn=float(2*np.linalg.norm(app[:,[0,2]],axis=1).max());assert turn<=6.7 and app[:,1].min()>=-2.895 and app[:,1].max()<=3.015;assert total<=180000
for rel,sha in json.loads((C/'baseline34_hashes.json').read_text()).items():assert hashlib.sha256((P/'candidate34'/rel).read_bytes()).hexdigest()==sha,'Frozen34 changed '+rel
result=dict(phase='hollow construction',complete_badge=False,meshes=159,total_triangles=total,bounds=[app.min(0).tolist(),app.max(0).tolist()],maximum_rotational_width=turn,modified=modified,unchanged_meshes=149,trimmed_concealed_corner_parts=8,hardware_intrusions_after=0,containment_samples_passed=len(samples),old_solid_negative_controls=negative,checks=rows,baseline34_files_unchanged=True);(C/'validation.json').write_text(json.dumps(result,indent=2)+'\n');np.savez_compressed(C/'geometry.npz',**packed);print(json.dumps({k:v for k,v in result.items() if k not in ('checks','modified')}))
