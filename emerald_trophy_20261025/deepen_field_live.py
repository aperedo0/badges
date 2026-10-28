from pathlib import Path
import bpy
ROOT=Path('/Users/antonioperedo/Desktop/badges/emerald_trophy_20261025')
scene=bpy.data.scenes['emerald_trophy'];bpy.context.window.scene=scene
for ob in scene.objects:
 if ob.type!='MESH' or not ob.get('new_emblem'):continue
 for m in ob.data.materials:
  if not m or not m.name.startswith('Trophy_field'):continue
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=1.
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE' and n.image and Path(n.image.filepath).name=='field_color.png':
    n.image=bpy.data.images.load(str(ROOT/'candidate03/textures/field_color.png'),check_existing=False);n.image.pack()
bpy.data.libraries.write(str(ROOT/'candidate03/emerald_trophy.blend'),{scene},compress=True)
print('Deep emerald field saved in complete scene')
