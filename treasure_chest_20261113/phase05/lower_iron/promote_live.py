import bpy,json,numpy as np,hashlib
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase05/lower_iron');C=D/'09_pitted_iron';checkpoint=json.loads((D/'checkpoint.json').read_text());asset=json.loads((C/'design.json').read_text());sc=bpy.data.scenes['Test plank master'];target=sc.objects['Lab Chest Lower Rim'];wood=sc.objects['Master Chest Body Envelope'];assert not bpy.app.is_job_running('RENDER')
def meshhash(obj):
 a=np.empty(len(obj.data.vertices)*3,np.float32);obj.data.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
assert meshhash(wood)==checkpoint['wood_geometry_sha256'];expected=np.load(D/'rim_geometry.npz')['world'].astype(np.float32);assert meshhash(target)==hashlib.sha256(expected.tobytes()).hexdigest(),'Lower rim changed after checkpoint'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'live_before_iron.blend'),compress=True,copy=True);old=target.data
with bpy.data.libraries.load(str(C/'master.blend'),link=False) as (available,chosen):
 assert asset['mesh'] in available.meshes;chosen.meshes=[asset['mesh']]
target.data=chosen.meshes[0];target['iron_development']='Initial bottom rim test, awaiting owner review';assert target.data.library is None and target.data.materials[0].library is None
users=bpy.data.user_map()
for lib in list(bpy.data.libraries):
 if Path(bpy.path.abspath(lib.filepath))==C/'master.blend':
  assert not users.get(lib) and not any(x.library==lib for x in users);bpy.data.libraries.remove(lib)
# Use the existing secondary image window for the final closeup; preserve the original reference editor.
shown=False
for window in list(bpy.context.window_manager.windows)[1:]:
 for area in window.screen.areas:
  if area.type=='IMAGE_EDITOR':
   image=bpy.data.images.load(str(C/'iron_final.png'),check_existing=True);image.name='Bottom iron test review';image.use_view_as_render=False;image.pack();area.spaces.active.image=image;region=next(r for r in area.regions if r.type=='WINDOW')
   with bpy.context.temp_override(window=window,area=area,region=region):bpy.ops.image.view_all(fit_view=True)
   shown=True
bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True);asset['mesh']=target.data.name;asset['material']=target.data.materials[0].name;(C/'design.json').write_text(json.dumps(asset,indent=2));assert meshhash(wood)==checkpoint['wood_geometry_sha256'];proof=dict(file=bpy.data.filepath,target=target.name,wood_geometry_hash=meshhash(wood),only_target_data_swapped=True,reference_preserved=True,owner_main_framing_preserved=True,final_closeup_shown_in_existing_window=shown,material=target.data.materials[0].name,maps_packed=all(n.image and n.image.packed_file for n in target.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE'),dirty=bpy.data.is_dirty);(C/'live_validation.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
