import bpy,json
from pathlib import Path
P=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab');sc=bpy.data.scenes['Test plank master'];bpy.context.window.scene=sc;sc.frame_set(0)
# All draft variants remain in comparisons.blend. The final file keeps the original and master scenes.
lab=bpy.data.scenes.get('Wood surface comparison')
if lab:bpy.data.scenes.remove(lab)
removed=[]
for o in list(bpy.data.objects):
 if (o.name.startswith('Lab body ') or o.name.startswith('Lab relief ')) and not o.users_scene:
  data=o.data;removed.append(o.name);bpy.data.objects.remove(o)
  if data.users==0:bpy.data.meshes.remove(data)
for m in list(bpy.data.materials):
 if m.name.startswith('Wood Lab ') and m.name!='Wood Lab H' and m.users==0:bpy.data.materials.remove(m)
for im in list(bpy.data.images):
 if im.users==0 and im.filepath and '/phase04/wood_lab/' in bpy.path.abspath(im.filepath):bpy.data.images.remove(im)
old=bpy.context.preferences.filepaths.save_version;bpy.context.preferences.filepaths.save_version=0
try:bpy.ops.wm.save_as_mainfile(filepath=str(P/'wood_master.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
print(json.dumps(dict(scenes=[s.name for s in bpy.data.scenes],draft_objects_retained_in_separate_comparison_file=removed)))
