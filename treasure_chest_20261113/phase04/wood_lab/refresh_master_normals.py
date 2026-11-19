import bpy,numpy as np
from pathlib import Path
P=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab');m=bpy.data.scenes['Test plank master'].objects['Master Chest Body Envelope'].data;s=bpy.data.scenes['Chest Complete Form Phase 1'].objects['Chest Body Envelope'].data;n=sum(len(f.vertices) for f in s.polygons if f.index not in [354,356,357]);norm=np.zeros((len(m.loops),3),dtype=np.float32);m.corner_normals.foreach_get('vector',norm.ravel());norm[n:]=0;m.normals_split_custom_set(norm)
old=bpy.context.preferences.filepaths.save_version;bpy.context.preferences.filepaths.save_version=0
try:bpy.ops.wm.save_as_mainfile(filepath=str(P/'wood_master.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
print('Original retained normals preserved; displaced surface normals refreshed')
