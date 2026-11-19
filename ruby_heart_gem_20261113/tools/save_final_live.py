import bpy
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/ruby_heart_gem_20261113');S=R/'source';sc=bpy.context.scene;ob=sc.objects['Ruby Heart gem'];script=next(n for n in ob.data.materials[0].node_tree.nodes if n.bl_idname=='ShaderNodeScript');script.filepath=str(S/'ruby_foil.osl');script.update()
for lv in (1,2,3,8):script.inputs['Mip'+str(lv)].default_value=str(S/f'studio_linear_mip{lv}.exr')
ref=sc.objects.get('Ruby Heart mockup')
if ref and ref.data and not ref.data.packed_file:ref.data.pack()
for ob in sc.objects:
 if ob.type!='MESH':continue
 for mat in ob.data.materials:
  if not mat or not mat.use_nodes:continue
  for n in mat.node_tree.nodes:
   if n.bl_idname=='ShaderNodeTexImage' and n.image and not n.image.packed_file:n.image.pack()
sc.cycles.preview_samples=16
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  sp=a.spaces.active;sp.shading.type='RENDERED';sp.overlay.show_overlays=False;r=sp.region_3d;r.view_perspective='ORTHO';r.view_location=(0,0,.27);r.view_distance=7.2;r.view_rotation=sc.camera.rotation_euler.to_quaternion()
bpy.ops.wm.save_as_mainfile(filepath=str(S/'ruby_heart.blend'));print('Saved complete final Ruby Heart with packed reference and gold texture; numeric optics beside the source file.')
