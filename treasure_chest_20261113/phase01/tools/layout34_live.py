# Apply only rigid placement corrections requested by the owner.
assert 'Status: APPROVED' in (P/'correction34/PLAN.md').read_text()
layout34=json.loads((C/'layout_changes.json').read_text());changes34=layout34['translations']
# Check the complete existing manifest before touching either side.
for name in list(changes34)+layout34['hide']:
 assert name in sc.objects and sc.objects[name].get('full_form'),name
for name,d in changes34.items():
 ob=sc.objects[name];normals=[n.vector[:] for n in ob.data.corner_normals];q=yaw@Vector(d);delta=Vector((q.x,-q.z,q.y))
 for v in ob.data.vertices:v.co+=delta
 ob.data.update();ob.data.normals_split_custom_set(normals)
for name in layout34['hide']:hide_part(sc.objects[name])
dome(layout34['new_front_small'],[-1.802,.735,1.845],[0,0,1],.043)
(C/'layout_stage.json').write_text(json.dumps(dict(moved=len(changes34),hidden=layout34['hide'],added=layout34['new_front_small'],geometry_not_deformed=True),indent=2))
print('Centered43 existing parts rigidly, replaced one obscured rear rivet with the missing mirrored front rivet. End arches unchanged.')
