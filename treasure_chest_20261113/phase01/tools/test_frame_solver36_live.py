import bpy,bmesh,numpy as np,json,time
from pathlib import Path
from mathutils import Vector
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate36';sc=bpy.context.scene
exec(compile((P/'tools/frame36_geometry.py').read_text().replace("assert areas.min()>1e-10","assert areas.min()>=0"),'engine measurement only','exec'))
groups=json.loads((C/'groups.json').read_text());report={};oldsel=list(bpy.context.selected_objects);active=bpy.context.view_layer.objects.active
objects=[]
for name in ('Chest Frame Solver Test36','Chest Frame Solver Operand36'):
 ob=sc.objects.get(name)
 if ob is None:
  me=bpy.data.meshes.new(name);ob=bpy.data.objects.new(name,me);sc.collection.objects.link(ob)
 ob['full_form']=False;ob['development_only']=True;ob.hide_render=True;ob.hide_set(False);objects.append(ob)
target,operand=objects
try:
 for ob in sc.objects:ob.select_set(False)
 for g in groups:
  names=[g['target']]+g['operands'];source=[capture36(sc.objects[n]) for n in names];material=sc.objects[g['target']].data.materials[0];field=source_field36(source);mesh36(target,source[0],material);stages=[]
  for n,data in zip(g['operands'],source[1:]):
   mesh36(operand,data,material);target.select_set(True);bpy.context.view_layer.objects.active=target;bpy.context.view_layer.update();mod=target.modifiers.new('Test closed solid solver36','BOOLEAN');mod.operation='UNION';mod.solver='MANIFOLD';mod.object=operand;bpy.ops.object.modifier_apply(modifier=mod.name);target.select_set(False)
   repairs=[];stages.append(dict(operand=n,repairs=repairs,**topology36(target)))
  d=capture36(target);pts=np.vstack([d['v'],d['v'][d['t']].mean(1)]);dist=np.array([field['tree'].find_nearest(Vector(p))[3] for p in pts]);report[g['target']]=dict(stages=stages,minimum_triangle_area=float((np.linalg.norm(np.cross(d['v'][d['t'][:,1]]-d['v'][d['t'][:,0]],d['v'][d['t'][:,2]]-d['v'][d['t'][:,0]]),axis=1)/2).min()),maximum_surface_error=float(dist.max()),over_original_gate=int((dist>.0008).sum()))
  np.savez_compressed(C/('solver_test_'+('body' if 'Body' in g['target'] else 'lid')+'.npz'),v=d['v'],t=d['t'])
  (C/'solver_test.json').write_text(json.dumps(report,indent=2));print(json.dumps({g['target']:report[g['target']]}))
finally:
 for ob in objects:ob.hide_set(True)
 for ob in sc.objects:ob.select_set(ob in oldsel)
 bpy.context.view_layer.objects.active=active
print('Engine test only. Saved and visible chest geometry unchanged.')
