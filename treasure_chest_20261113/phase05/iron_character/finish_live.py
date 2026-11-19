import bpy,json,numpy as np,hashlib
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase05/iron_character');choice=json.loads((D/'selection.json').read_text());C=D/choice['candidate'];assert Path(bpy.data.filepath)==C/'master.blend';F=D.parent/'iron_fidelity';text=(F/'validate.py').read_text();exec(compile(text[text.index('def digest'):text.index('def mesh')],'existing_material_graph_hash','exec'))
def mh(o):
 a=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
sc=bpy.data.scenes['Test plank master'];mat=sc.objects['Lab Chest Lower Rim'].data.materials[0];before=(mh(sc.objects['Lab Chest Lower Rim']),mh(sc.objects['Master Chest Body Envelope']),graph(mat));shown=False
final_image=bpy.data.images.load(str(C/('iron_'+choice['environment']+'_final.png')),check_existing=True);final_image.name='Weathered bottom iron final review';final_image.use_view_as_render=False;final_image.use_fake_user=True;final_image.pack()
for window in list(bpy.context.window_manager.windows):
 for area in window.screen.areas:
  if area.type=='IMAGE_EDITOR' and not (area.spaces.active.image and area.spaces.active.image.name=='reference.png'):
   im=bpy.data.images.load(str(C/('iron_'+choice['environment']+'_final.png')),check_existing=True);im.name='Weathered bottom iron final review';im.use_view_as_render=False;im.pack();area.spaces.active.image=im;region=next(r for r in area.regions if r.type=='WINDOW')
   with bpy.context.temp_override(window=window,area=area,region=region):bpy.ops.image.view_all(fit_view=True)
   shown=True
assert before==(mh(sc.objects['Lab Chest Lower Rim']),mh(sc.objects['Master Chest Body Envelope']),graph(mat));bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_mainfile();proof=json.loads((C/'live_validation.json').read_text());proof.pop('review_window_closed_by_owner',None);proof.update(dirty=bpy.data.is_dirty,review_quality='Final 128 sample Cycles image saved and packed',review_image_shown=shown,material_graph=graph(mat),iron_geometry=before[0],wood_geometry=before[1],file_sha256=hashlib.sha256((C/'master.blend').read_bytes()).hexdigest());(C/'live_validation.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
