import bpy,shutil
from pathlib import Path
from mathutils import Vector
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');sc=bpy.context.scene
for o in sc.objects:
 if o.type in ('LIGHT','CAMERA') or o.name=='Development floor':o.hide_set(True)
 if o.type=='MESH' and o.get('full_form'):o.hide_set(False);o.select_set(False)
ref=sc.objects.get('First chest owner reference')
if ref:ref.hide_set(False);ref.empty_display_size=7.4;ref.location=(-8,0,.14)
bpy.context.view_layer.objects.active=None
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=True;sp.overlay.show_floor=False;sp.overlay.show_axis_x=False;sp.overlay.show_axis_y=False;sp.overlay.show_cursor=False;sp.overlay.show_extras=True
   reg=sp.region_3d;reg.view_perspective='ORTHO';reg.view_location=Vector((-4.1,0,.14));reg.view_distance=19;reg.view_rotation=sc.camera.rotation_euler.to_quaternion()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'treasure_chest.blend'),compress=True);shutil.copy2(R/'treasure_chest.blend',R/'phase01/candidate25/chest.blend')
print('Saved the complete chest beside its reference in the open Blender')
