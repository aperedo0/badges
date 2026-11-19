import bpy,numpy as np,json,hashlib,shutil
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');S=R/'phase03/stylized_wood45';B=R/'phase03/wood_sample44/candidate03';C=S/'candidate01';D=json.loads((C/'design.json').read_text());sc=bpy.context.scene
assert bpy.data.filepath==str(B/'chest.blend') and sc.frame_current==0,'Unexpected source file or pose'
# Save current window changes in the same source file before any file switch.
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
# Saving keeps all current window state. No existing scene is loaded or discarded.
exec(compile((R/'phase01/tools/frame36_geometry.py').read_text(),'g36','exec'));exec(compile((R/'phase01/tools/hinge38_geometry.py').read_text(),'g38','exec'));model=[o for o in sc.objects if o.type=='MESH' and o.get('full_form')];before={o.name:capture36(o) for o in model};assert len(model)==155
ob=sc.objects[D['part']];me=ob.data;oldmat=bpy.data.materials['Chest Wood Sample44 v3'];assert oldmat.users==1;gray=[m for m in me.materials if m is not oldmat];gray_states={m.name:m.node_tree.as_pointer() for m in gray};old_indices=[f.material_index for f in me.polygons];expected=json.loads((R/'phase03/wood_sample44/selection_preflight.json').read_text())['faces'];slot=list(me.materials).index(oldmat);assert [f.index for f in me.polygons if f.material_index==slot]==expected
frozen={str(f.relative_to(B)):hashlib.sha256(f.read_bytes()).hexdigest() for f in B.rglob('*') if f.is_file()};(C/'baseline03_hashes.json').write_text(json.dumps(frozen,indent=2))
local=local38(before[ob.name]['v']);uv=me.uv_layers[D['uv']];b=D['bounds'];W=D['texture_width'];H=D['texture_height'];pad=D['padding']
for li,l in enumerate(me.loops):
 q=local[l.vertex_index];uv.data[li].uv=(pad/W+(q[0]-b['xmin'])/(b['xmax']-b['xmin'])*(W-2*pad)/W,pad/H+(q[1]-b['ymin'])/(b['ymax']-b['ymin'])*(H-2*pad)/H)
oldmat.name=D['material'];mat=oldmat;bsdf=mat.node_tree.nodes['Principled BSDF'];bsdf.inputs['Specular IOR Level'].default_value=D['specular_level'];bsdf.inputs['Metallic'].default_value=0;bsdf.inputs['Emission Strength'].default_value=0;bsdf.inputs['Coat Weight'].default_value=0;images={}
for role,file,space in [('albedo','wood_albedo.png','sRGB'),('roughness','wood_roughness.png','Non-Color'),('normal','wood_normal.png','Non-Color')]:
 img=bpy.data.images.load(str(C/'textures'/file),check_existing=False);img.colorspace_settings.name=space;img.pack();mat.node_tree.nodes['Single plank '+role].image=img;images[role]=img.name
for o in model:
 d=capture36(o)
 for k in ('vertex_hash','triangle_hash','normal_hash'):assert d[k]==before[o.name][k],(o.name,k)
 if o is not ob:assert d['materials']==before[o.name]['materials']
assert [f.material_index for f in me.polygons]==old_indices;assert all(m.node_tree.as_pointer()==gray_states[m.name] for m in gray)
for rel,sha in frozen.items():assert hashlib.sha256((B/rel).read_bytes()).hexdigest()==sha
for rel,sha in json.loads((B/'baseline43_hashes.json').read_text()).items():assert hashlib.sha256((R/'phase01/candidate43'/rel).read_bytes()).hexdigest()==sha
report=json.loads((B/'isolation_proof.json').read_text());report.update(material=mat.name,images=images,all_images_packed=True,texture_canvas=[W,H],one_plank_continues=True);(C/'isolation_proof.json').write_text(json.dumps(report,indent=2));shutil.copy2(B/'before_geometry_manifest.json',C/'before_geometry_manifest.json');shutil.copy2(B/'baseline43_hashes.json',C/'baseline43_hashes.json');(C/'source').mkdir(exist_ok=True)
for f in ('prepare_maps.py','apply_live.py'):shutil.copy2(S/f,C/'source'/f)
old=bpy.context.preferences.filepaths.save_version
try:bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'chest.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
print('Saved stylized one plank sample; all155 geometries and all other wood and metal materials unchanged.')
