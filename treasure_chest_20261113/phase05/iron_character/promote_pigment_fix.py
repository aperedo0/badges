import bpy,json,numpy as np,hashlib
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase05/iron_character');A=D/'10_defined_scale';C=D/'11_restored_pigment';assert Path(bpy.data.filepath)==A/'master.blend';sc=bpy.data.scenes['Test plank master'];assert not bpy.app.is_job_running('RENDER');a=json.loads((C/'design.json').read_text());previous=json.loads((A/'live_validation.json').read_text())
def mh(o):
 v=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',v);return hashlib.sha256(v.tobytes()).hexdigest()
assert mh(sc.objects['Lab Chest Lower Rim'])==previous['iron_geometry'];assert mh(sc.objects['Master Chest Body Envelope'])==previous['wood_geometry'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'live_before_pigment_fix.blend'),compress=True,copy=True)
with bpy.data.libraries.load(str(C/'master.blend'),link=False) as (src,data):
 assert a['material'] in src.materials;data.materials=[a['material']]
mat=data.materials[0]
for name in previous['scope']:
 obj=sc.objects[name]
 if obj.data.users>1:obj.data=obj.data.copy()
 obj.data.materials[0]=mat
users=bpy.data.user_map()
for lib in list(bpy.data.libraries):
 if Path(bpy.path.abspath(lib.filepath))==C/'master.blend':
  assert not users.get(lib) and not any(x.library==lib for x in users);bpy.data.libraries.remove(lib)
assert not any(n.bl_idname=='ShaderNodeOutputAOV' for n in mat.node_tree.nodes);assert not any(a.name.startswith('Iron_') for layer in sc.view_layers for a in layer.aovs)
shown=False
for window in list(bpy.context.window_manager.windows)[1:]:
 for area in window.screen.areas:
  if area.type=='IMAGE_EDITOR':
   im=bpy.data.images.load(str(D/'aov/after/beauty.png'),check_existing=True);im.name='Iron corrected pigmentation review';im.use_view_as_render=False;im.pack();area.spaces.active.image=im;region=next(r for r in area.regions if r.type=='WINDOW')
   with bpy.context.temp_override(window=window,area=area,region=region):bpy.ops.image.view_all(fit_view=True)
   shown=True
assert shown;assert mh(sc.objects['Lab Chest Lower Rim'])==previous['iron_geometry'];assert mh(sc.objects['Master Chest Body Envelope'])==previous['wood_geometry'];a.update(mesh=sc.objects['Lab Chest Lower Rim'].data.name,material=mat.name);(C/'design.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True);proof=dict(file=bpy.data.filepath,dirty=bpy.data.is_dirty,wood_geometry=previous['wood_geometry'],iron_geometry=previous['iron_geometry'],scope=previous['scope'],review_image_shown=shown,review_stage='AOV verified correction crop',production_diagnostic_nodes_absent=True,production_aov_passes_absent=True,material=mat.name,all_target_maps_packed=all(n.image and n.image.packed_file for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'),file_sha256=hashlib.sha256((C/'master.blend').read_bytes()).hexdigest());(C/'live_validation.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
