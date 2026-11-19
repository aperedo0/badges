import bpy,json,hashlib,numpy as np
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase05/lower_iron');sc=bpy.data.scenes['Test plank master'];assert not bpy.app.is_job_running('RENDER'),'Allow active render to finish before checkpoint'
source_file=bpy.data.filepath;images=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.has_data and not im.packed_file:im.pack()
 if im.source=='FILE':images.append(dict(name=im.name,packed=bool(im.packed_file),size=list(im.size),filepath=im.filepath))
body=sc.objects['Master Chest Body Envelope'];co=np.empty(len(body.data.vertices)*3,np.float32);body.data.vertices.foreach_get('co',co)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'baseline.blend'),compress=True,copy=True)
proof=dict(source_file=source_file,baseline=str(D/'baseline.blend'),baseline_sha256=hashlib.sha256((D/'baseline.blend').read_bytes()).hexdigest(),wood_geometry_sha256=hashlib.sha256(co.tobytes()).hexdigest(),wood_material=next(m.name for m in body.data.materials if m and m.name.startswith('Wood Lab ')),images=images,render_finished=True,reference_camera=sc.camera.name,exposure=sc.view_settings.exposure,view_transform=sc.view_settings.view_transform,look=sc.view_settings.look)
(D/'checkpoint.json').write_text(json.dumps(proof,indent=2));print(json.dumps({k:v for k,v in proof.items() if k!='images'}));print('File images',len(images),'unpacked',[v['name'] for v in images if not v['packed']])
