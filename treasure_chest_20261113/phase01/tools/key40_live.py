import bpy,numpy as np,json,hashlib,shutil
from pathlib import Path
from mathutils import Matrix
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';B=P/'candidate39';C=P/'candidate40';sc=bpy.context.scene;assert bpy.data.filepath==str(B/'chest.blend') and sc.frame_current==0
policy=json.loads((R/'work_mode.json').read_text());assert policy['manual_work_authorized'] and not policy['owner_paused_badge_work']
exec(compile((P/'tools/frame36_geometry.py').read_text(),'helpers36','exec'));exec(compile((P/'tools/hinge38_geometry.py').read_text(),'helpers38','exec'));C.mkdir(exist_ok=True)
key=sc.objects['Chest Removable Crank Key'];before=capture36(key);local=local38(before['v']);tri=before['t'];Z=local[tri,2];drive_faces=np.where((Z.min(1)<=1.85501)&(Z.max(1)>=1.82999))[0];ids=np.unique(tri[drive_faces]);center=np.array([0.,-.676]);radii=np.linalg.norm(local[ids,:2]-center,axis=1);assert len(ids)>20 and radii.max()<.02505,('Selection contains an intentional arm or shaft',float(radii.max()));changed=ids[radii>.025];assert len(changed)>0
oldlocal=local.copy()
for i in changed:
 q=local[i,:2]-center;q*=.025/np.linalg.norm(q);local[i,:2]=center+q
world=world38(local)
# Assign only the selected pin points; outside vertices stay bit exact.
for i in changed:key.data.vertices[int(i)].co=world[i]
key.data.update();normals=before['n'].copy();me=key.data
for face in me.polygons:
 V=local[np.array(face.vertices)];rho=np.linalg.norm(V[:,:2]-center,axis=1)
 if V[:,2].min()<=1.85501 and V[:,2].max()>=1.82999 and np.ptp(V[:,2])>.005 and rho.min()>=.02498:
  for li in face.loop_indices:
   i=me.loops[li].vertex_index;d=local[i,:2]-center;n=world38([[d[0]/np.linalg.norm(d),d[1]/np.linalg.norm(d),0]])[0];n/=np.linalg.norm(n);normals[li]=n
me.normals_split_custom_set(normals.tolist());after=capture36(key);assert np.array_equal(before['t'],after['t']);keep=np.ones(len(local),bool);keep[changed]=False;assert np.array_equal(before['v'][keep],after['v'][keep]);movement=np.linalg.norm(after['v']-before['v'],axis=1);assert movement.max()<.000051
proof=topology36(key);assert proof['euler']==0;actual=local38(after['v']);maximum=float(np.linalg.norm(actual[ids,:2]-center,axis=1).max());assert maximum<=.0250004,maximum
# The pilot, stop, shaft, bow and intentional crank arm are outside this selection.
assert actual[ids,2].max()<1.89501 and oldlocal[ids,2].min()>1.83499
body_before=np.load(B/'geometry.npz');meta=json.loads((B/'validation.json').read_text());packed={}
for i,row in enumerate(meta['checks']):
 ob=sc.objects[row['name']];d=capture36(ob);app=np.c_[d['v'][:,0],d['v'][:,2],-d['v'][:,1]];assert np.array_equal(app,body_before[f'part{i}_v']),(ob.name,'unrelated body or lid geometry changed');assert np.array_equal(d['t'],body_before[f'part{i}_t']);assert np.max(abs(np.array(ob.matrix_world)-np.eye(4)))<1e-7;packed[f'part{i}_v']=app;packed[f'part{i}_t']=d['t']
for rel,sha in json.loads((C/'baseline39_hashes.json').read_text()).items():assert hashlib.sha256((B/rel).read_bytes()).hexdigest()==sha,rel
np.savez_compressed(C/'geometry.npz',**packed);shutil.copy2(B/'inspection_ownership.json',C/'inspection_ownership.json');shutil.copy2(B/'rig_stage.json',C/'rig_stage.json');shutil.copy2(B/'actual_hinge_geometry_proof.json',C/'actual_hinge_geometry_proof.json');meta.update(stage='Full lid rig with nominal cylindrical key drive pin, full motion recheck pending');(C/'validation.json').write_text(json.dumps(meta,indent=2));result=dict(part=key.name,drive_pin_nominal_radius=.025,selected_vertex_count=len(ids),corrected_vertices=len(changed),old_maximum_radius=float(radii.max()),new_maximum_radius=maximum,maximum_vertex_movement=float(movement.max()),other_key_vertices_unchanged=True,all155_static_export_meshes_unchanged=True,closed_key_proof=proof,full_motion_screen_pending=True);(C/'key_drive_pin_correction.json').write_text(json.dumps(result,indent=2));(C/'source').mkdir(exist_ok=True)
for f in ('key40_live.py','frame36_geometry.py','hinge38_geometry.py'):shutil.copy2(P/'tools'/f,C/'source'/f)
old=bpy.context.preferences.filepaths.save_version
try:bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'chest.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
print(json.dumps(result))
