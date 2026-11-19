import bpy,numpy as np,json,hashlib,shutil
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate37';sc=bpy.context.scene
assert bpy.data.filepath==str(P/'candidate36/chest.blend') and sc.frame_current==0
policy=json.loads((R/'work_mode.json').read_text());assert policy['manual_work_authorized'] and not policy['owner_paused_badge_work']
exec(compile((P/'tools/frame36_geometry.py').read_text(),'helpers36','exec'))
model=[o for o in sc.objects if o.type=='MESH' and o.get('full_form')];assert len(model)==147;before={o.name:capture36(o) for o in model};base=np.load(P/'candidate36/geometry.npz');meta=json.loads((P/'candidate36/validation.json').read_text())['checks']
for i,row in enumerate(meta):
 v=before[row['name']]['v'];assert np.array_equal(np.c_[v[:,0],v[:,2],-v[:,1]],base[f'part{i}_v']),(row['name'],'not36')
changed={};caps={}
for name,level,direction in [('Chest Body Upper Rim',.36365,1),('Chest Upper Lid Rim',.38075,-1)]:
 ob=sc.objects[name];me=ob.data;normals=before[name]['n'].copy();indices=[]
 for f in me.polygons:
  V=np.array([me.vertices[i].co[:] for i in f.vertices]);G=np.cross(V[1]-V[0],V[2]-V[0]);G/=np.linalg.norm(G)
  if np.max(abs(V[:,2]-level))<1e-6 and G[2]*direction>.99999:
   for li in f.loop_indices:normals[li]=[0,0,direction]
   indices.extend(f.loop_indices)
   f.use_smooth=False
 assert indices,name;me.normals_split_custom_set(normals.tolist());caps[name]=dict(level=level,direction=direction,flat_loop_count=len(indices));changed[name]='flat mating surface normals'
for side in (-1,1):
 name=f'Chest Rear Hinge Upper {side}';ob=sc.objects[name]
 for v in ob.data.vertices:v.co.z+=.010
 ob.data.update();changed[name]='upper leaf lifted0.010'
bpy.context.view_layer.update();rows=[];packed={};allv=[]
for i,ob in enumerate(model):
 d=capture36(ob);b=before[ob.name];assert np.array_equal(d['t'],b['t']),(ob.name,'topology changed');assert d['materials']==b['materials'];assert np.max(abs(np.array(ob.matrix_world)-np.eye(4)))<1e-7
 if ob.name not in changed:
  for k in ('vertex_hash','triangle_hash','normal_hash'):assert d[k]==b[k],(ob.name,k)
 elif ob.name in caps:
  assert np.array_equal(d['v'],b['v']);mask=np.ones(len(d['n']),bool);level=caps[ob.name]['level'];direction=caps[ob.name]['direction']
  for f in ob.data.polygons:
   V=np.array([ob.data.vertices[i].co[:] for i in f.vertices]);G=np.cross(V[1]-V[0],V[2]-V[0]);G/=np.linalg.norm(G)
   if np.max(abs(V[:,2]-level))<1e-6 and G[2]*direction>.99999:
    mask[list(f.loop_indices)]=False;angle=float(np.degrees(np.arccos(np.clip(d['n'][list(f.loop_indices),2]*direction,-1,1))).max());assert angle<.1,(ob.name,'flat normal encoding error',angle)
  dot=np.einsum('ij,ij->i',d['n'][mask],b['n'][mask]);angle=float(np.degrees(np.arccos(np.clip(dot,-1,1))).max());assert angle<.3,(ob.name,'exterior normals changed',angle)
 else:
  delta=d['v']-b['v'];assert np.max(abs(delta-[0,0,.010]))<2e-7;angle=float(np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i',d['n'],b['n']),-1,1))).max());assert angle<.3,(ob.name,'translated normal changed',angle);assert abs(d['v'][:,2].min()-.39075)<1e-6
 proof=topology36(ob);rows.append(dict(name=ob.name,change=changed.get(ob.name,'unchanged'),**proof));allv.append(d['v']);packed[f'part{i}_v']=np.c_[d['v'][:,0],d['v'][:,2],-d['v'][:,1]];packed[f'part{i}_t']=d['t']
for rel,sha in json.loads((C/'baseline36_hashes.json').read_text()).items():assert hashlib.sha256((P/'candidate36'/rel).read_bytes()).hexdigest()==sha,rel
V=np.vstack(allv);app=np.c_[V[:,0],V[:,2],-V[:,1]];turn=float(2*np.linalg.norm(app[:,[0,2]],axis=1).max());assert turn<=6.7 and app[:,1].min()>=-2.895 and app[:,1].max()<=3.015
inventory={};code=(P/'tools/cavity35_inventory_live.py').read_text().replace("C=P/'candidate35'","C=P/'candidate37'");exec(compile(code,'inventory37','exec'),inventory);assert not inventory['rows']
result=dict(complete_badge=False,meshes=147,unchanged_meshes=143,total_triangles=sum(r['triangles'] for r in rows),flat_caps=caps,checks=rows,hardware_intrusions=0,maximum_rotational_width=turn,baseline36_unchanged=True);(C/'validation.json').write_text(json.dumps(result,indent=2)+'\n');np.savez_compressed(C/'geometry.npz',**packed);shutil.copy2(P/'candidate36/inspection_ownership.json',C/'inspection_ownership.json');(C/'source').mkdir(exist_ok=True)
for f in ('seats37_live.py','frame36_geometry.py'):shutil.copy2(P/'tools'/f,C/'source'/f)
old=bpy.context.preferences.filepaths.save_version
try:bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'chest.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
print(json.dumps({k:v for k,v in result.items() if k not in ('checks',)}))
