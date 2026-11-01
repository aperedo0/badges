"""Run inside live Blender, with badge_name supplied by the driver."""
from pathlib import Path
import bpy, numpy as np, sys, importlib, re
from mathutils import Vector, Quaternion
R=Path('/Users/antonioperedo/Desktop/badges/coin_standard_20261101')
sys.path.insert(0,str(R))
import geometry
importlib.reload(geometry)
F=R/'family'; C=F/badge_name/'candidate01'
scene=bpy.data.scenes.new(badge_name+' approved coin dimensions')
bpy.context.window.scene=scene
bpy.ops.wm.usd_import(filepath=str(F/'work'/badge_name/'blender_import.usdc'),import_cameras=False,import_lights=False)
objects=[o for o in scene.objects if o.type=='MESH']
arrays={}
for ob in objects:
    assert np.allclose(np.asarray(ob.matrix_world),np.eye(4)),ob.name
    me=ob.data
    p=np.array([v.co[:] for v in me.vertices],float)
    n=np.array([v.vector[:] for v in me.corner_normals])
    q=geometry.points_after(p)
    new_n=geometry.normals_after(p[[l.vertex_index for l in me.loops]],n)
    for v,point in zip(me.vertices,q):v.co=point
    me.update();me.normals_split_custom_set(new_n.tolist());me.update()
    arrays[re.sub(r'(?:\.\d{3})+$','',ob.name)]=np.array([v.co[:] for v in me.vertices],np.float32)
for image in bpy.data.images:
    if image.source=='FILE' and not image.packed_file:
        try:image.pack()
        except RuntimeError:pass
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        s=area.spaces.active;s.region_3d.view_rotation=Quaternion((1,0,0,0));s.region_3d.view_location=Vector((0,0,0));s.region_3d.view_distance=9.7;s.region_3d.view_perspective='ORTHO';s.shading.type='MATERIAL';s.overlay.show_overlays=False
np.savez_compressed(C/'inspected_points.npz',**arrays)
bpy.data.libraries.write(str(C/'source'/('coin.blend')),{scene},compress=True)
print(badge_name,len(objects),'complete meshes; rim 20 percent narrower; depth 30 percent thinner.')
