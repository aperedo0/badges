# Add cavities to two accepted meshes. Never regenerate the full chest.
import bpy,math,json,numpy as np,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate35';sc=bpy.context.scene
assert 'Status: APPROVED' in (P/'hollow35/PLAN.md').read_text()
policy=json.loads((R/'work_mode.json').read_text());assert policy['mode']=='manual' and policy['manual_work_authorized'] and not policy['overnight_enabled']
assert sc.frame_current==0
Y35=np.array(Matrix.Rotation(math.radians(32),3,'Y'));I35=Y35.T

def local35(a):
 a=np.asarray(a);return np.c_[a[:,0],a[:,2],-a[:,1]]@I35.T

def vector35(q):
 a=Y35@np.asarray(q,float);return np.array((a[0],-a[2],a[1]))

def hash35(a):return hashlib.sha256(np.asarray(a).tobytes()).hexdigest()

def capture35(ob):
 me=ob.data;me.calc_loop_triangles();v=np.array([p.co[:] for p in me.vertices]);t=np.array([p.vertices[:] for p in me.loop_triangles]);n=np.array([p.vector[:] for p in me.corner_normals]);faces=[list(f.vertices) for f in me.polygons];attrs=[dict(smooth=f.use_smooth,material=f.material_index) for f in me.polygons];fn=[n[list(f.loop_indices)].tolist() for f in me.polygons]
 return dict(name=ob.name,v=v,t=t,n=n,tn=n[np.array([tri.loops[:] for tri in me.loop_triangles])],tattrs=[attrs[tri.polygon_index] for tri in me.loop_triangles],faces=faces,attrs=attrs,face_normals=fn,vertex_hash=hash35(v),triangle_hash=hash35(t),normal_hash=hash35(n),matrix=np.array(ob.matrix_world).tolist())

visible35=[o for o in sc.objects if o.type=='MESH' and o.get('full_form')];assert len(visible35)==159
before35={o.name:capture35(o) for o in visible35}
# Prove this is the untouched accepted34 geometry before any change.
base35=np.load(P/'candidate34/geometry.npz');meta35=json.loads((P/'candidate34/validation.json').read_text())
for i,row in enumerate(meta35['checks']):
 a=before35[row['name']]['v'];app=np.c_[a[:,0],a[:,2],-a[:,1]];assert np.array_equal(app,base35[f'part{i}_v']),(row['name'],'not accepted34')
manifest={k:{f:v for f,v in d.items() if f in ('name','vertex_hash','triangle_hash','normal_hash','matrix')} for k,d in before35.items()};(C/'before_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
np.savez_compressed(C/'core_before.npz',body_v=before35['Chest Body Envelope']['v'],body_n=before35['Chest Body Envelope']['n'],lid_v=before35['Chest Barrel Lid Envelope']['v'],lid_n=before35['Chest Barrel Lid Envelope']['n'])
(C/'core_before.json').write_text(json.dumps({name:{key:before35[name][key] for key in ('faces','attrs')} for name in ('Chest Body Envelope','Chest Barrel Lid Envelope')},indent=2)+'\n')
modified35={}

def hollow35(name,kind):
 ob=sc.objects[name];old=before35[name];v=old['v'].tolist();oldlocal=local35(old['v']);level=float(oldlocal[:,1].max() if kind=='body' else oldlocal[:,1].min());caps=[i for i,f in enumerate(old['faces']) if np.max(abs(oldlocal[f,1]-level))<1e-5];expected=148 if kind=='body' else 832;assert caps==[expected],(name,'unexpected closing faces',caps)
 cap=caps[0];outer=old['faces'][cap];assert len(outer)==4
 faces=[];attrs=[];normals=[];retained=[];newfaces=[]
 for i,f in enumerate(old['faces']):
  if i==cap:continue
  retained.append((i,len(faces)));faces.append(f);attrs.append(old['attrs'][i]);normals.append(old['face_normals'][i])
 def point(q):
  v.append(vector35(q).tolist());return len(v)-1
 def face(ids,desired,smooth=False,corner=None):
  ids=list(ids);p=np.array([v[i] for i in ids]);n=np.cross(p,np.roll(p,-1,axis=0)).sum(0);target=vector35(desired);target/=np.linalg.norm(target)
  values=[vector35(x).tolist() for x in corner] if corner is not None else [target.tolist() for _ in ids]
  if np.dot(n,target)<0:ids.reverse();values.reverse()
  newfaces.append(len(faces));faces.append(ids);attrs.append(dict(smooth=smooth,material=old['attrs'][cap]['material']));normals.append(values)
 if kind=='body':
  opening=[point([math.copysign(2.33,oldlocal[i,0]),level,math.copysign(1.38,oldlocal[i,2])]) for i in outer]
  floor=[point([math.copysign(2.33,oldlocal[i,0]),-2.0175,math.copysign(1.38,oldlocal[i,2])]) for i in outer]
  for i in range(4):
   j=(i+1)%4;face([outer[i],outer[j],opening[j],opening[i]],[0,1,0]);mid=(oldlocal[outer[i]]+oldlocal[outer[j]])/2;target=[-np.sign(mid[0]),0,0] if abs(mid[0])>2 else [0,0,-np.sign(mid[2])];face([opening[i],opening[j],floor[j],floor[i]],target)
  face(floor,[0,1,0]);inner=np.array([[2.33,level,1.38],[2.33,-2.0175,1.38]])
 else:
  N=96;angles=np.linspace(0,math.pi,N+1);curve=[];inward=[]
  for i,a in enumerate(angles):
   n=np.array([math.sin(a)/1.9475,math.cos(a)/1.65]);n/=np.linalg.norm(n);y=.38075+1.9475*math.sin(a)-.18*n[0];z=1.65*math.cos(a)-.18*n[1]
   if i in (0,N):y=level;z=1.47 if i==0 else -1.47
   curve.append([y,z]);inward.append([0,-n[0],-n[1]])
  L=[point([-2.38,y,z]) for y,z in curve];U=[point([2.38,y,z]) for y,z in curve]
  for i in range(N):
   j=i+1;desired=(np.array(inward[i])+inward[j])/2;face([L[i],L[j],U[j],U[i]],desired,True,[inward[i],inward[j],inward[j],inward[i]])
  face(L,[1,0,0]);face(U,[-1,0,0])
  opening=[(L[0] if oldlocal[i,2]>0 else L[-1]) if oldlocal[i,0]<0 else (U[0] if oldlocal[i,2]>0 else U[-1]) for i in outer]
  for i in range(4):j=(i+1)%4;face([outer[i],outer[j],opening[j],opening[i]],[0,-1,0])
  inner=np.array(curve)
 me=ob.data;me.clear_geometry();me.from_pydata(v,[],faces);me.update()
 for f,a in zip(me.polygons,attrs):f.use_smooth=a['smooth'];f.material_index=a['material']
 flat=[x for row in normals for x in row];assert len(flat)==len(me.loops);me.normals_split_custom_set(flat)
 modified35[name]=dict(kind=kind,old_cap=cap,level=level,old_vertex_count=len(old['v']),retained=retained,new_faces=newfaces,inner=inner.tolist(),old_faces=len(old['faces']),new_face_count=len(faces))

hollow35('Chest Body Envelope','body');hollow35('Chest Barrel Lid Envelope','lid');bpy.context.view_layer.update()
(C/'hollow_stage.json').write_text(json.dumps(modified35,indent=2)+'\n');print('Added actual hollow body and curved lid; original outer points and other157 meshes retained. Not saved until checks pass.')
