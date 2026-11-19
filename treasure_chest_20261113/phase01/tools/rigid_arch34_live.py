# Move each complete end arch assembly rigidly. Do not reshape its surfaces.
assert 'Status: APPROVED' in (P/'correction34/PLAN.md').read_text()
shifted34=[]
for sx,i in [(-1,0),(1,3)]:
 names=[f'Chest Broad End Arch {sx}',f'Chest End Arch Crown Tab {sx}',f'Chest Crown Fastener Mass {i+1}']
 heads=[f'Chest End Crown Fastener {sx}']+[f'Chest End Arch Rivet {sx} {k}' for k in (0,1)]+[f'Chest Hoop Rivet {i} {k}' for k in (0,1)]
 names+=heads
 for name in names:assert name in sc.objects and sc.objects[name].get('full_form'),name
 delta=yaw@Vector((-sx*.040,0,0));delta=Vector((delta.x,-delta.z,delta.y))
 for name in names:
  ob=sc.objects[name];assert ob.get('full_form'),name
  normals=[n.vector[:] for n in ob.data.corner_normals]
  for v in ob.data.vertices:v.co+=delta
  ob.data.update();ob.data.normals_split_custom_set(normals);shifted34.append(name)
assert len(shifted34)==16
(C/'rigid_arch_parts.json').write_text(json.dumps(dict(parts=shifted34,translation_inward=.040,rigid_no_deformation=True),indent=2))
print('Moved16 end assembly parts rigidly inward0.040; surface shapes and normals preserved.')
