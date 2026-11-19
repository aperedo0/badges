import bpy,numpy as np,json,math,hashlib,shutil
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';B=P/'candidate38';C=P/'candidate39';sc=bpy.context.scene
assert 'Status: APPROVED' in (P/'hinge38/PLAN.md').read_text();assert bpy.data.filepath==str(B/'chest.blend') and sc.frame_current==0
policy=json.loads((R/'work_mode.json').read_text());assert policy['manual_work_authorized'] and not policy['owner_paused_badge_work'];C.mkdir(exist_ok=True)
exec(compile((P/'tools/frame36_geometry.py').read_text(),'helpers36','exec'));exec(compile((P/'tools/hinge38_geometry.py').read_text(),'helpers38','exec'))
roles=json.loads((B/'inspection_ownership.json').read_text())['parts'];meta=json.loads((B/'validation.json').read_text());base=np.load(B/'geometry.npz');before={}
for i,row in enumerate(meta['checks']):
 ob=sc.objects[row['name']];d=capture36(ob);assert np.array_equal(np.c_[d['v'][:,0],d['v'][:,2],-d['v'][:,1]],base[f'part{i}_v']),(ob.name,'not38');assert np.max(abs(np.array(ob.matrix_world)-np.eye(4)))<1e-7;before[ob.name]=d

def graphs39():
 rows=[]
 for owner in list(bpy.data.objects)+list(bpy.data.shape_keys):
  if owner.animation_data:
   for fc in owner.animation_data.drivers:rows.append(dict(owner=owner.name,path=fc.data_path,index=fc.array_index,expression=fc.driver.expression,variables=[dict(name=v.name,type=v.type,id=v.targets[0].id.name,path=v.targets[0].data_path) for v in fc.driver.variables],simple=fc.driver.is_simple_expression,valid=fc.driver.is_valid))
 return sorted(rows,key=lambda x:(x['owner'],x['path'],x['index']))
old_graphs=graphs39();assert len(old_graphs)==14 and all(g['simple'] and g['valid'] for g in old_graphs)
frames=[0,115,130,230,240,250,270,280,290,340,380,490];oldbody={};haspctrl=sc.objects['Chest Rig HaspRelease'];master=sc.objects['Chest Rig Master'];axis=Vector(world38([[1,0,0]])[0]).normalized();pivot=Vector(world38([[0,.36175,-1.93]])[0]);hp=Vector(world38([[0,.48525,2]])[0]);hasp_old=(haspctrl.location.copy(),tuple(haspctrl.rotation_axis_angle),haspctrl.scale.copy());assert haspctrl.parent is None
try:
 for frame in frames:
  sc.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();dg.update();oldbody[frame]={n:np.array(sc.objects[n].evaluated_get(dg).matrix_world) for n,r in roles.items() if r=='body'}
finally:sc.frame_set(0);bpy.context.view_layer.update()
# Center new rear fasteners on the exposed flat lands, clear of the sleeve silhouette.
headproof=[]
for record in json.loads((B/'hinge_stage.json').read_text())['heads']:
 ob=sc.objects[record['name']];role=record['role'];old_y=.167 if role=='body' else .57125;new_y=.1345 if role=='body' else .59875
 for v in ob.data.vertices:v.co.z+=new_y-old_y
 ob.data.update();headproof.append(dict(name=ob.name,old_center_y=old_y,new_center_y=new_y,reason='Centered between plate flat edge and actual barrel silhouette'))
lid=sc.objects.get('Chest Rig LidOpen');assert lid is None,'Unexpected existing lid control'
lid=bpy.data.objects.new('Chest Rig LidOpen',None);sc.collection.objects.link(lid);lid['chest_mechanism_controller']=True;lid.empty_display_type='ARROWS';lid.empty_display_size=.20;lid.location=pivot;lid.rotation_mode='AXIS_ANGLE';lid.rotation_axis_angle=(0,*axis);lid.hide_set(True);bpy.context.view_layer.update();inverse=lid.matrix_world.inverted()
for name,role in roles.items():
 if role=='lid':
  ob=sc.objects[name];assert ob.parent is None,(name,'already parented');ob.parent=lid;ob.matrix_parent_inverse=inverse;ob.matrix_basis=Matrix.Identity(4)
haspctrl.parent=lid;haspctrl.matrix_parent_inverse=inverse;haspctrl.location=hasp_old[0];haspctrl.rotation_mode='AXIS_ANGLE';haspctrl.rotation_axis_angle=hasp_old[1];haspctrl.scale=hasp_old[2]
master['lid_degrees']=0.;master.id_properties_ui('lid_degrees').update(min=0.,max=110.,description='Main lid angle after the front hasp has been released')
fc=lid.driver_add('rotation_axis_angle',0);driver=fc.driver;driver.type='SCRIPTED';driver.expression='-0.017453292519943295*a';var=driver.variables.new();var.name='a';var.type='SINGLE_PROP';var.targets[0].id=master;var.targets[0].data_path='["lid_degrees"]';driver.expression='-a*0.017453292519943295'
for frame,value in [(0,0.),(230,0.),(250,95.),(270,95.),(290,0.),(490,0.)]:master['lid_degrees']=value;master.keyframe_insert(data_path='["lid_degrees"]',frame=frame)
action=master.animation_data.action;curves=list(action.fcurves) if hasattr(action,'fcurves') else [fc for layer in action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
for fc in curves:
 if fc.data_path=='["lid_degrees"]':
  fc.update_autoflags(master)
  for k in fc.keyframe_points:k.interpolation='LINEAR'
action.name='Chest Key Catch Hasp And Lid Construction Test'
master.update_tag(refresh={'TIME','OBJECT'});action.update_tag(refresh={'TIME'});lid.update_tag(refresh={'OBJECT','TIME'})
for frame,label in [(230,'Lid test ready'),(250,'Lid test95degrees'),(290,'Lid test closed')]:sc.timeline_markers.new(label,frame=frame)
endpoint=[]
try:
 for frame in frames:
  sc.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();dg.update();degrees=float(master['lid_degrees']);angle=math.radians(degrees);delta=Matrix.Translation(pivot)@Matrix.Rotation(-angle,4,axis)@Matrix.Translation(-pivot);hasp=float(master['hasp']);expected_hasp=delta@Matrix.Translation(hp)@Matrix.Rotation(-hasp,4,axis)@Matrix.Translation(-hp);liderr=bodyerr=hasperr=0.
  for name,role in roles.items():
   actual=np.array(sc.objects[name].evaluated_get(dg).matrix_world)
   if role=='lid':liderr=max(liderr,float(abs(actual-np.array(delta)).max()))
   elif role=='body':bodyerr=max(bodyerr,float(abs(actual-oldbody[frame][name]).max()))
   else:hasperr=max(hasperr,float(abs(actual-np.array(expected_hasp)).max()))
  assert max(liderr,bodyerr,hasperr)<1e-5,(frame,liderr,bodyerr,hasperr)
  if frame in (250,270):assert abs(degrees-95)<1e-5
  if frame in (0,230,290,490):assert abs(degrees)<1e-5
  endpoint.append(dict(frame=frame,lid_degrees=degrees,hasp_degrees=math.degrees(hasp),lid_world_error=liderr,body_world_error=bodyerr,compound_hasp_error=hasperr))
finally:sc.frame_set(0);bpy.context.view_layer.update()
new_graphs=graphs39();assert len(new_graphs)==15 and all(g['simple'] and g['valid'] for g in new_graphs);assert [g for g in new_graphs if g['owner']!='Chest Rig LidOpen']==old_graphs,'Original driver graphs changed'
packed={};headnames={h['name'] for h in headproof}
for i,row in enumerate(meta['checks']):
 ob=sc.objects[row['name']];d=capture36(ob);old=before[ob.name];assert np.array_equal(d['t'],old['t']);assert d['materials']==old['materials'];assert np.max(abs(np.array(ob.matrix_world)-np.eye(4)))<1e-7,(ob.name,'closed rest not identity')
 if ob.name not in headnames:
  for k in ('vertex_hash','triangle_hash','normal_hash'):assert d[k]==old[k],(ob.name,'rig changed mesh',k)
 else:
  delta=d['v']-old['v'];h=next(h for h in headproof if h['name']==ob.name);assert np.max(abs(delta-[0,0,h['new_center_y']-h['old_center_y']]))<2e-7
 packed[f'part{i}_v']=np.c_[d['v'][:,0],d['v'][:,2],-d['v'][:,1]];packed[f'part{i}_t']=d['t']
for rel,sha in json.loads((C/'baseline38_hashes.json').read_text()).items():assert hashlib.sha256((B/rel).read_bytes()).hexdigest()==sha,rel
np.savez_compressed(C/'geometry.npz',**packed);shutil.copy2(B/'inspection_ownership.json',C/'inspection_ownership.json');(C/'rig_stage.json').write_text(json.dumps(dict(master=master.name,lid_control=lid.name,local_pivot=[0,.36175,-1.93],world_axis=list(axis),head_centering=headproof,original_driver_graphs=old_graphs,drivers=new_graphs,endpoint_checks=endpoint,hasp_parent=haspctrl.parent.name,rest_frame=0,full_travel_collision_checks_complete=False,final_animation=False),indent=2));meta.update(stage='Working main lid control, motion clearance pending',rigged=True,head_rows_centered=True);(C/'validation.json').write_text(json.dumps(meta,indent=2))
(C/'source').mkdir(exist_ok=True)
for name in ('rig39_live.py','hinge38_geometry.py','frame36_geometry.py'):shutil.copy2(P/'tools'/name,C/'source'/name)
old=bpy.context.preferences.filepaths.save_version
try:bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'chest.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
print(json.dumps(dict(saved=str(C/'chest.blend'),drivers=15,rest_frame=0,ownership_tests=len(endpoint),full_motion_clearance_pending=True)))
