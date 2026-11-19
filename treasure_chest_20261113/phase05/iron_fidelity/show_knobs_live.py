import bpy,json,hashlib,numpy as np
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase05/iron_fidelity');C=D/'P_iron_knobs';assert Path(bpy.data.filepath)==C/'master.blend';assert not bpy.app.is_job_running('RENDER');sc=bpy.data.scenes['Test plank master'];shown=False
for window in list(bpy.context.window_manager.windows)[1:]:
 for area in window.screen.areas:
  if area.type=='IMAGE_EDITOR':
   im=bpy.data.images.load(str(C/'iron_studio3_final.png'),check_existing=True);im.name='Bottom iron and two knobs review';im.use_view_as_render=False;im.pack();area.spaces.active.image=im;region=next(r for r in area.regions if r.type=='WINDOW')
   with bpy.context.temp_override(window=window,area=area,region=region):bpy.ops.image.view_all(fit_view=True)
   shown=True
assert shown
checks=json.loads((C/'knobs.json').read_text())
for proof in checks:
 o=sc.objects[proof['object']];a=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',a);assert hashlib.sha256(a.tobytes()).hexdigest()==proof['geometry_sha256'];assert o.data.materials[0] is sc.objects['Lab Chest Lower Rim'].data.materials[0]
wood=sc.objects['Master Chest Body Envelope'];a=np.empty(len(wood.data.vertices)*3,np.float32);wood.data.vertices.foreach_get('co',a);woodhash=hashlib.sha256(a.tobytes()).hexdigest();assert woodhash==json.loads((D/'checkpoint.json').read_text())['wood_geometry']
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_mainfile();proof=dict(file=bpy.data.filepath,dirty=bpy.data.is_dirty,wood_geometry_hash=woodhash,knobs=checks,approved_wood_preserved=True,other_hardware_preserved=True,review_image_shown=True,reference_editors=[a.spaces.active.image.name for w in bpy.context.window_manager.windows for a in w.screen.areas if a.type=='IMAGE_EDITOR' and a.spaces.active.image],saved_file_sha256=hashlib.sha256((C/'master.blend').read_bytes()).hexdigest());(C/'live_validation.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
