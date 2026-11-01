from pathlib import Path
import bpy,numpy as np
from mathutils import Vector,Quaternion
R=Path('/Users/antonioperedo/Desktop/badges/coin_standard_20261101')
scene=bpy.data.scenes.new('Emerald Sprout original complete coin');bpy.context.window.scene=scene
bpy.ops.wm.usd_import(filepath=str(R/'work/original/blender_import.usdc'),import_cameras=False,import_lights=False)
for image in bpy.data.images:
 if image.source=='FILE':
  try:image.pack()
  except RuntimeError:pass
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  s=a.spaces.active;s.region_3d.view_rotation=Quaternion((1,0,0,0));s.region_3d.view_location=Vector((0,0,0));s.region_3d.view_distance=9.7;s.region_3d.view_perspective='ORTHO';s.shading.type='MATERIAL';s.overlay.show_overlays=False
objects=[o for o in scene.objects if o.type=='MESH'];p=np.vstack([np.array([v.co[:] for v in o.data.vertices]) for o in objects])
print('Complete original imported:',len(objects),'meshes, bounds',p.min(0).tolist(),p.max(0).tolist())
for o in objects:
 assert np.allclose(np.array(o.matrix_world),np.eye(4)),o.name
 if 'Casing___' in o.name:print('Casing',o.name,'vertices',len(o.data.vertices),'max radius',float(np.linalg.norm(np.array([v.co[:] for v in o.data.vertices])[:,:2],axis=1).max()))
bpy.data.libraries.write(str(R/'original/source/emerald_sprout_original.blend'),{scene},compress=True)
