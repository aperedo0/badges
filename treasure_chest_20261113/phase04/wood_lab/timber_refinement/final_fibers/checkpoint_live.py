import bpy,json,hashlib,numpy as np
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab/timber_refinement/final_fibers');sc=bpy.context.scene;assert sc.name=='Test plank master';o=sc.objects['Master Chest Body Envelope'];p=Path(bpy.data.filepath)
a=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',a);d=dict(source_file=str(p),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),live_dirty=bpy.data.is_dirty,geometry_sha256=hashlib.sha256(a.tobytes()).hexdigest(),material=[m.name for m in o.data.materials],layout=[a.type for a in bpy.context.screen.areas],lights={q.name:dict(matrix=[list(r) for r in q.matrix_world],color=list(q.data.color),energy=q.data.energy,size=q.data.size) for q in sc.objects if q.type=='LIGHT'})
(D/'checkpoint.json').write_text(json.dumps(d,indent=2));old=bpy.context.preferences.filepaths.save_version;bpy.context.preferences.filepaths.save_version=0
try:bpy.ops.wm.save_as_mainfile(filepath=str(D/'baseline.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
print(json.dumps({k:d[k] for k in ['source_file','live_dirty','geometry_sha256','layout']}))
