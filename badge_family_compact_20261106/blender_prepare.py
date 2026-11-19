"""Open a complete optimized badge in live Blender and save an editable copy."""
import bpy,json,math,zipfile
from pathlib import Path
ROOT=Path('/Users/antonioperedo/Desktop/badges/badge_family_compact_20261106')
slug=(ROOT/'blender_next.txt').read_text().strip();C=ROOT/'badges'/slug/'candidate01';row=next(r for r in json.loads((ROOT/'manifest.json').read_text()) if r['slug']==slug)
scene=bpy.data.scenes.new(row['title']+' compact working copy');bpy.context.window.scene=scene
unpack=C/'source/import';unpack.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(C/'model.usdz') as z:z.extractall(unpack)
bpy.ops.wm.usd_import(filepath=str(unpack/'badge.usdc'),import_cameras=False,import_lights=False,import_textures_mode='IMPORT_PACK',tex_name_collision_mode='OVERWRITE')
meshes=[o for o in scene.objects if o.type=='MESH'];expected=json.loads((C/'validation.json').read_text())['after']['meshes'];assert len(meshes)==expected,(len(meshes),expected)
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
from mathutils import Quaternion,Vector
points=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
span=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
scene["badge_y_up_geometry"]=any("Casing___" in o.name for o in meshes)
base=Quaternion((1,0,0),0 if scene["badge_y_up_geometry"] else math.pi/2)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False;r=area.spaces.active.region_3d;r.view_perspective='ORTHO';r.view_distance=9.1;r.view_location=(0,.28,0) if scene["badge_y_up_geometry"] else (0,0,.28);r.view_rotation=base
# Imported geometry is inspected here but packaging stays in USD so the original
# material graphs and protected runtime geometry cannot change on round trip.
bpy.ops.file.pack_all();(C/'source').mkdir(exist_ok=True);bpy.data.libraries.write(str(C/'source/model.blend'),{scene},fake_user=False,compress=True)
print(row['title'],len(meshes),'complete mesh objects saved')
