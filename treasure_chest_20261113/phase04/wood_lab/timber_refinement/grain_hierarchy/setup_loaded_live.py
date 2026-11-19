import bpy,json
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab/timber_refinement/grain_hierarchy');C=D.parent/'R_layers_full'
assert not bpy.data.is_dirty,'Preserve new unsaved owner changes before switching'
assert Path(bpy.data.filepath)==C/'master.blend'
bpy.context.window.scene=bpy.data.scenes['Test plank master']
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  space=area.spaces.active;space.shading.type='MATERIAL';space.shading.use_scene_lights=True;space.shading.use_scene_world=True
  space.region_3d.view_perspective='CAMERA'
review=bpy.data.images.load(str(C/'cinema_close.png'),check_existing=True)
review.name='Saved test plank Cycles review'
oldpref=bpy.context.preferences.filepaths.save_version
try:
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=oldpref
print(json.dumps(dict(filepath=bpy.data.filepath,scene=bpy.context.scene.name,dirty=bpy.data.is_dirty,review_image=review.name)))
