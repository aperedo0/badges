import bpy,bmesh,numpy as np,json,hashlib,math
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate36';sc=bpy.context.scene
exec(compile((P/'tools/frame36_geometry.py').read_text(),'frame36_geometry.py','exec'))
assert 'Status: APPROVED' in (P/'frame36/PLAN.md').read_text();policy=json.loads((R/'work_mode.json').read_text());assert policy['manual_work_authorized'] and policy['mode']=='manual';assert sc.frame_current==0
meta36=json.loads((P/'candidate35/validation.json').read_text());base36=np.load(P/'candidate35/geometry.npz');before36={}
for i,row in enumerate(meta36['checks']):
 ob=sc.objects[row['name']];d=capture36(ob);a=d['v'];assert np.array_equal(np.c_[a[:,0],a[:,2],-a[:,1]],base36[f'part{i}_v']),(ob.name,'not accepted35');before36[ob.name]=d
(C/'before_manifest.json').write_text(json.dumps({k:{f:d[f] for f in ('vertex_hash','triangle_hash','normal_hash','uv_layers','materials')} for k,d in before36.items()},indent=2)+'\n')
groups36=json.loads((C/'groups.json').read_text());group_members36=[n for g in groups36 for n in [g['target']]+g['operands']];assert len(group_members36)==14 and len(set(group_members36))==14
for name in group_members36:
 ob=sc.objects[name];d=before36[name];assert d['uv_layers']==0 and {a['material'] for a in d['attrs']}=={0};assert ob.parent is None and ob.animation_data is None,(name,'moving part cannot be welded')
scenesel36=[o.name for o in bpy.context.selected_objects];active36=bpy.context.view_layer.objects.active
operand36=sc.objects.get('Chest Frame Union Operand Tool 36')
if operand36 is None:
 me=bpy.data.meshes.new('Chest Frame Union Operand Tool 36');operand36=bpy.data.objects.new(me.name,me);sc.collection.objects.link(operand36)
operand36['full_form']=False;operand36['development_only']=True;operand36.hide_render=True;operand36.hide_set(False)
field_data36={g['target']:source_field36([before36[n] for n in [g['target']]+g['operands']]) for g in groups36};reports36={};normal_targets36={}
initial_fields36={}
for name,d in field_data36.items():
 for key in ('v','t','tn'):initial_fields36[name+' '+key]=d[key]
np.savez_compressed(C/'source_fields.npz',**initial_fields36);(C/'source_field_attrs.json').write_text(json.dumps({name:d['attrs'] for name,d in field_data36.items()}))
try:
 for o in sc.objects:o.select_set(False)
 for g in groups36:
  target=sc.objects[g['target']];material=target.data.materials[0];names=[g['target']]+g['operands'];assert all(sc.objects[n].data.materials[0]==material for n in names),(g['target'],'different material cannot be welded')
  field=field_data36[g['target']];mesh36(target,before36[g['target']],material);stages=[]
  for name in g['operands']:
   mesh36(operand36,before36[name],material);operand36.hide_set(False);target.hide_set(False);target.select_set(True);bpy.context.view_layer.objects.active=target;bpy.context.view_layer.update();mod=target.modifiers.new('Continuous frame joint36','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=operand36
   if hasattr(mod,'use_hole_tolerant'):mod.use_hole_tolerant=True
   bpy.ops.object.modifier_apply(modifier=mod.name);target.select_set(False)
   repairs=clean36(target.data);proof=topology36(target);stages.append(dict(operand=name,sliver_diagonal_repairs=repairs,**proof));(C/'build_progress.json').write_text(json.dumps(dict(group=g['target'],completed_operands=stages),indent=2))
  assert stages[-1]['euler']==g['expected_euler'],(g['target'],'wrong designed openings',stages[-1]['euler'],g['expected_euler'])
  target.data.materials.clear();target.data.materials.append(material);result=transfer36(target,field);normal_targets36[g['target']]=result.pop('loop_targets');reports36[g['target']]=dict(stages=stages,**result)
  for name in g['operands']:
   ob=sc.objects[name];ob['full_form']=False;ob.hide_render=True;ob.hide_set(True)
finally:
 operand36.hide_set(True)
 for o in sc.objects:o.select_set(o.name in scenesel36)
 bpy.context.view_layer.objects.active=active36
fields={}
for name,d in field_data36.items():
 for key in ('v','t','tn'):fields[name+' '+key]=d[key]
np.savez_compressed(C/'source_fields.npz',**fields);np.savez_compressed(C/'normal_targets.npz',**normal_targets36);(C/'frame_stage.json').write_text(json.dumps(reports36,indent=2)+'\n');print('Built continuous body upper and complete lid metal frames. Original parts kept hidden; no save before checks.')
