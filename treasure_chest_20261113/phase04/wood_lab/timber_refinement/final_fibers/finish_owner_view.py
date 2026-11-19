import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab/timber_refinement/final_fibers');C=D.parent/'AE_controlled_fibers'
old=bpy.context.preferences.filepaths.save_version;bpy.context.preferences.filepaths.save_version=0
try:
 if bpy.data.is_dirty:bpy.ops.wm.save_as_mainfile(filepath=str(D/'live_before_review.blend'),compress=True)
 # The selected file has already loaded; finish in a fresh live context.
 assert Path(bpy.data.filepath)==C/'master.blend'
 sc=bpy.data.scenes['Test plank master'];win=bpy.context.window_manager.windows[0];win.scene=sc;sc.frame_set(0)
 R=Matrix.Rotation(math.radians(32),3,'Y')
 def world(q):
  a=R@Vector(q);return Vector((a.x,-a.z,a.y))
 fill=sc.objects['Lab Chest Development Fill'];fill.location=(4,-5.5,4.5);fill.rotation_euler=(world((.4,-1.3,1.6))-fill.location).to_track_quat('-Z','Y').to_euler();fill.data.energy=800;fill.data.color=(1,.80,.62);fill.data.size=3.5
 for area in win.screen.areas:
  if area.type=='VIEW_3D':
   space=area.spaces.active;space.shading.type='RENDERED';space.overlay.show_overlays=False;space.region_3d.view_perspective='ORTHO';space.region_3d.view_rotation=sc.camera.matrix_world.to_quaternion();space.region_3d.view_location=world((-.15,-1.45,1.6));space.region_3d.view_distance=6.6
 sc.cycles.samples=128;sc.cycles.preview_samples=64;sc.cycles.seed=17;sc.cycles.use_denoising=True
 body=sc.objects['Master Chest Body Envelope'];win.view_layer.objects.active=body
 for o in sc.objects:o.select_set(False,view_layer=win.view_layer)
 body.select_set(True,view_layer=win.view_layer)
 bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True)
 print(json.dumps(dict(file=bpy.data.filepath,scene=sc.name,material=[m.name for m in body.data.materials],reference_shared=sc.objects['First chest owner reference'] is bpy.data.scenes['Chest Complete Form Phase 1'].objects['First chest owner reference'],layout=[a.type for a in win.screen.areas],owner_review_pending=True)))
finally:bpy.context.preferences.filepaths.save_version=old
