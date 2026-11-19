import bpy,json
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab/timber_refinement/grain_hierarchy')
assert not bpy.data.is_dirty
area=max((a for a in bpy.context.screen.areas if a.type=='VIEW_3D'),key=lambda a:a.width*a.height)
area.spaces.active.shading.use_scene_lights=False;area.spaces.active.shading.use_scene_world=False
area.type='IMAGE_EDITOR'
im=bpy.data.images.load(str(D/'owner_comparison.jpg'),check_existing=True);area.spaces.active.image=im
region=next(r for r in area.regions if r.type=='WINDOW')
with bpy.context.temp_override(area=area,region=region):bpy.ops.image.view_all(fit_view=True)
old=bpy.context.preferences.filepaths.save_version
try:
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
print(json.dumps(dict(filepath=bpy.data.filepath,dirty=bpy.data.is_dirty,review=im.filepath)))
