import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
win=bpy.context.window_manager.windows[0];sc=win.scene
assert sc.name=='Test plank master'
R=Matrix.Rotation(math.radians(32),3,'Y');a=R@Vector((-.15,-1.45,1.6));target=Vector((a.x,-a.z,a.y))
for area in win.screen.areas:
 if area.type=='VIEW_3D':
  rv=area.spaces.active.region_3d;rv.view_perspective='ORTHO';rv.view_rotation=sc.camera.matrix_world.to_quaternion();rv.view_location=target;rv.view_distance=3.9
old=bpy.context.preferences.filepaths.save_version;bpy.context.preferences.filepaths.save_version=0
try:bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
print(json.dumps(dict(restored_view=True,saved=bpy.data.filepath)))
