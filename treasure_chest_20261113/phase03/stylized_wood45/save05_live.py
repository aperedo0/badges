import bpy,json,hashlib
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');S=R/'phase03/stylized_wood45';C=S/'candidate05';sc=bpy.context.scene
assert bpy.data.filepath==str(C/'chest.blend') and sc.frame_current==0
exec(compile((R/'phase01/tools/frame36_geometry.py').read_text(),'g36','exec'))
baseline=json.loads((C/'before_geometry_manifest.json').read_text());models=[o for o in sc.objects if o.type=='MESH' and o.get('full_form')];assert len(models)==155
for ob in models:
 d=capture36(ob)
 for key in ('vertex_hash','triangle_hash','normal_hash'):assert d[key]==baseline[ob.name][key],(ob.name,key)
 if ob.name!='Chest Body Envelope':assert d['materials']==baseline[ob.name]['materials'],ob.name
body=sc.objects['Chest Body Envelope'];mat=bpy.data.materials['Chest Wood Stylized Sample45 v5'];slot=list(body.data.materials).index(mat);expected=json.loads((C/'isolation_proof.json').read_text())['faces'];assert [f.index for f in body.data.polygons if f.material_index==slot]==expected
assert mat.node_tree.nodes['Single plank physical tangent normal'].inputs['Strength'].default_value==1
assert all(mat.node_tree.nodes['Single plank '+role].image.packed_file is not None for role in ('albedo','roughness','normal'))
for relative,digest in json.loads((C/'baseline43_hashes.json').read_text()).items():assert hashlib.sha256((R/'phase01/candidate43'/relative).read_bytes()).hexdigest()==digest
for relative,digest in json.loads((C/'baseline04_hashes.json').read_text()).items():assert hashlib.sha256((S/'candidate04'/relative).read_bytes()).hexdigest()==digest
# Save existing window state without loading or discarding anyone's changes.
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
print(json.dumps(dict(saved=bpy.data.filepath,geometry_preserved=True,other_planks_and_metal_unchanged=True,images_packed=True)))
