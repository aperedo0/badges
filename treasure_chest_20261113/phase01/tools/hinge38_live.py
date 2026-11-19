import bpy,numpy as np,json,math,hashlib,shutil,time
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate38';sc=bpy.context.scene
assert 'Status: APPROVED' in (P/'hinge38/PLAN.md').read_text();assert bpy.data.filepath==str(R/'treasure_chest.blend') and not bpy.data.is_dirty and sc.frame_current==0
policy=json.loads((R/'work_mode.json').read_text());assert policy['manual_work_authorized'] and not policy['owner_paused_badge_work']
assert hashlib.sha256((R/'treasure_chest.blend').read_bytes()).digest()==hashlib.sha256((P/'candidate37/chest.blend').read_bytes()).digest()
exec(compile((P/'tools/frame36_geometry.py').read_text(),'geometry36','exec'));exec(compile((P/'tools/hinge38_geometry.py').read_text(),'hinge_geometry38','exec'))
C.mkdir(exist_ok=True);model=[o for o in sc.objects if o.type=='MESH' and o.get('full_form')];assert len(model)==147;before38={o.name:capture36(o) for o in model};base=np.load(P/'candidate37/geometry.npz');meta=json.loads((P/'candidate37/validation.json').read_text())['checks']
for i,row in enumerate(meta):
 v=before38[row['name']]['v'];assert np.array_equal(np.c_[v[:,0],v[:,2],-v[:,1]],base[f'part{i}_v']),(row['name'],'not saved37')
(C/'before_manifest.json').write_text(json.dumps({name:{k:d[k] for k in ('vertex_hash','triangle_hash','normal_hash','materials')} for name,d in before38.items()},indent=2));np.savez_compressed(C/'before_geometry.npz',**{n:d['v'] for n,d in before38.items()})
structural=bpy.data.materials['Chest rough structural forms'];hardware=bpy.data.materials['Chest rough hardware forms'];fixed=[(-.300,-.190),(-.055,.055),(.190,.300)];moving=[(-.178,-.067),(.067,.178)];fixed_relief=[(-.306,-.184),(-.061,.061),(.184,.306)];moving_relief=[(-.184,-.061),(.061,.184)];stages={};fields38={};normal38={};newheads=[];lidframe=sc.objects['Chest Upper Lid Rim'];frame_sources=[before38[lidframe.name]];frame_stages=[]
for sx in (-1,1):
 cx=sx*1.55
 for role,slots,opposite,expected in [('Lower',fixed,moving_relief,-4),('Upper',moving,fixed_relief,-2)]:
  name=f'Chest Rear Hinge {role} {sx}';ob=sc.objects[name];sources=[before38[name]];ops=[]
  for i,(a,b) in enumerate(opposite):
   cutter=cylinder38(f'Chest Hinge38 {role} relief {sx} {i}',cx,a,b,.126,structural);source=negative38(capture36(cutter));sources.append(source);ops.append(boolean38(ob,cutter,'DIFFERENCE'))
   if role=='Upper':frame_sources.append(source);frame_stages.append(boolean38(lidframe,cutter,'DIFFERENCE'))
  for i,(a,b) in enumerate(slots):
   ring=ring38(f'Chest Hinge38 {role} sleeve source {sx} {i}',cx,a,b,structural);sources.append(capture36(ring));ops.append(boolean38(ob,ring,'UNION'))
  cutter=cylinder38(f'Chest Hinge38 {role} full bore {sx}',cx,-.42,.42,.056,structural);sources.append(negative38(capture36(cutter)));ops.append(boolean38(ob,cutter,'DIFFERENCE'));proof=topology36(ob);assert proof['euler']==expected,(name,'wrong real through bores',proof)
  field=source_field36(sources);transfer=transfer36(ob,field);normal38[name]=transfer.pop('loop_targets');fields38[name]=field;stages[name]=dict(operations=ops,expected_euler=expected,proof=proof,**transfer);(C/'build_progress.json').write_text(json.dumps(dict(completed=list(stages),current=name),indent=2))
 pin=pin38(f'Chest Rear Hinge Barrel {sx}',cx,hardware);proof=topology36(pin);assert proof['euler']==2;stages[pin.name]=dict(proof=proof,purpose='Actual retained circular pin, body fixed')
 for role,cy in [('Lower',.167),('Upper',.57125)]:
  plate=sc.objects[f'Chest Rear Hinge {role} {sx}'];pd=capture36(plate);pt=BVHTree.FromPolygons(pd['v'].tolist(),pd['t'].tolist(),all_triangles=True)
  for i,offset in enumerate((-.18,.18)):
   head=head38(f'Chest Rear Hinge {role} Rivet {sx} {i}',cx+offset,cy,hardware);proof=topology36(head);assert proof['euler']==2;hd=capture36(head);ht=BVHTree.FromPolygons(hd['v'].tolist(),hd['t'].tolist(),all_triangles=True);point=world38([[cx+offset,cy,-1.902]])[0];assert inside36(pt,point) and inside36(ht,point),(head.name,'not positively seated');newheads.append(dict(name=head.name,role='body' if role=='Lower' else 'lid',positive_root=point.tolist(),proof=proof))
field=source_field36(frame_sources);transfer=transfer36(lidframe,field);normal38[lidframe.name]=transfer.pop('loop_targets');fields38[lidframe.name]=field;proof=topology36(lidframe);assert proof['euler']==-8;stages[lidframe.name]=dict(operations=frame_stages,proof=proof,**transfer)
changed=set(stages);assert len(changed)==7;allmodel=[o for o in sc.objects if o.type=='MESH' and o.get('full_form')];assert len(allmodel)==155;rows=[];allv=[];packed={};unchanged=0
for i,ob in enumerate(allmodel):
 d=capture36(ob);proof=topology36(ob);assert np.max(abs(np.array(ob.matrix_world)-np.eye(4)))<1e-7
 if ob.name in before38 and ob.name not in changed:
  for k in ('vertex_hash','triangle_hash','normal_hash'):assert d[k]==before38[ob.name][k],(ob.name,'unrelated change',k)
  unchanged+=1
 rows.append(dict(name=ob.name,changed=ob.name in changed or ob.name not in before38,**proof));allv.append(d['v']);packed[f'part{i}_v']=np.c_[d['v'][:,0],d['v'][:,2],-d['v'][:,1]];packed[f'part{i}_t']=d['t']
assert unchanged==140;assert before38['Chest Body Upper Rim']['vertex_hash']==capture36(sc.objects['Chest Body Upper Rim'])['vertex_hash']
V=np.vstack(allv);app=np.c_[V[:,0],V[:,2],-V[:,1]];turn=float(2*np.linalg.norm(app[:,[0,2]],axis=1).max());total=sum(r['triangles'] for r in rows);assert turn<=6.7 and app[:,1].min()>=-2.895 and app[:,1].max()<=3.015 and total<=185000
for rel,sha in json.loads((C/'baseline37_hashes.json').read_text()).items():assert hashlib.sha256((P/'candidate37'/rel).read_bytes()).hexdigest()==sha,rel
inventory={};code=(P/'tools/cavity35_inventory_live.py').read_text().replace("C=P/'candidate35'","C=P/'candidate38'");exec(compile(code,'cavity38','exec'),inventory);assert not inventory['rows']
roles=json.loads((P/'candidate37/inspection_ownership.json').read_text())['parts'];roles.update({h['name']:h['role'] for h in newheads});(C/'inspection_ownership.json').write_text(json.dumps(dict(parts=roles,counts={r:list(roles.values()).count(r) for r in ('body','lid','hasp')}),indent=2))
fields={}
for name,f in fields38.items():
 for k in ('v','t','tn'):fields[name+' '+k]=f[k]
np.savez_compressed(C/'source_fields.npz',**fields);np.savez_compressed(C/'normal_targets.npz',**normal38);np.savez_compressed(C/'geometry.npz',**packed);(C/'hinge_stage.json').write_text(json.dumps(dict(stages=stages,heads=newheads,full_lid_rig=False),indent=2));result=dict(complete_badge=False,stage='True rear hinge geometry, lid rig not yet added',meshes=155,total_triangles=total,unchanged_meshes=140,maximum_rotational_width=turn,hardware_intrusions=0,checks=rows);(C/'validation.json').write_text(json.dumps(result,indent=2))
(C/'source').mkdir(exist_ok=True)
for f in ('hinge38_live.py','hinge38_geometry.py','frame36_geometry.py','validate_hinge38_inputs.py'):shutil.copy2(P/'tools'/f,C/'source'/f)
old=bpy.context.preferences.filepaths.save_version
try:bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'chest.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
