from pathlib import Path
import bpy
R=Path('/Users/antonioperedo/Desktop/badges/emerald_trophy_20261025/candidate05')
scene=bpy.context.scene
for ob in scene.objects:
 if ob.type!='MESH':continue
 for mat in ob.data.materials:
  if not mat or not mat.name.startswith('Reference_traced_relief'):continue
  nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=1.;bs.inputs['Roughness'].default_value=.55
  for node in nt.nodes:
   if node.type!='TEX_IMAGE':continue
   suffix='emission' if 'emission' in node.image.name else 'color'
   node.image=bpy.data.images.load(str(R/'textures'/('relief_'+suffix+'.png')),check_existing=False);node.image.colorspace_settings.name='sRGB';node.image.pack()
  bs.inputs['Emission Strength'].default_value=8
bpy.data.libraries.write(str(R/'emerald_trophy.blend'),{scene},compress=True)
print('Reference finish applied to the editable Blender scene')
