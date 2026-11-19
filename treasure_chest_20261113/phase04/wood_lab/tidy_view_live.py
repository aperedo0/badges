import bpy
from pathlib import Path
P=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab');sc=bpy.data.scenes['Test plank master'];source=bpy.data.scenes['Chest Complete Form Phase 1'];bpy.context.window.scene=sc
for o in source.objects:
 q=sc.objects.get('Lab '+o.name)
 if q and o.type in {'CAMERA','LIGHT'}:q.hide_set(o.hide_get(view_layer=source.view_layers[0]))
for o in sc.objects:
 if o.type=='CAMERA':o.hide_set(True)
for o in bpy.context.selected_objects:o.select_set(False)
old=bpy.context.preferences.filepaths.save_version;bpy.context.preferences.filepaths.save_version=0
try:bpy.ops.wm.save_as_mainfile(filepath=str(P/'wood_master.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
print('Saved clean master viewport with the existing reference visible')
