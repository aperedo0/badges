import bpy,json,hashlib,numpy as np
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab/timber_refinement/surface_definition');o=bpy.data.scenes['Test plank master'].objects['Master Chest Body Envelope'];a=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',a)
proof=dict(source=bpy.data.filepath,source_file_sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),geometry_sha256=hashlib.sha256(a.tobytes()).hexdigest(),material=[m.name for m in o.data.materials],reference_camera=bpy.data.scenes['Test plank master'].camera.name,live_dirty=bpy.data.is_dirty)
assert not (D/'baseline.blend').exists()
old=bpy.context.preferences.filepaths.save_version;bpy.context.preferences.filepaths.save_version=0
try:bpy.ops.wm.save_as_mainfile(filepath=str(D/'baseline.blend'),compress=True,copy=True)
finally:bpy.context.preferences.filepaths.save_version=old
(D/'checkpoint.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
