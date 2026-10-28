"""Match the gold casing in a complete copy of the finished Blender trophy."""
from pathlib import Path
import json,bpy
from mathutils import Quaternion
R=Path('/Users/antonioperedo/Desktop/badges/emerald_trophy_20261025');C=R/'candidate06'
with bpy.data.libraries.load(str(R/'candidate05/emerald_trophy.blend'),link=False) as (available,loaded):loaded.scenes=[available.scenes[0]]
scene=loaded.scenes[0];scene.name='Emerald Trophy matching gold rim';bpy.context.window.scene=scene
meta=json.loads((C/'rim_finish.json').read_text());gold=meta['gold_linear']
for ob in scene.objects:
 if ob.type!='MESH' or not ob.name.startswith('Casing___'):continue
 print('Rim materials:',[m.name for m in ob.data.materials])
 for index,slot in enumerate(ob.material_slots):
  if not slot.material:continue
  old=slot.material;m=old.copy();slot.material=m;m.name='Trophy matched rim '+str(index)
  bs=m.node_tree.nodes.get('Principled BSDF');factor=.94 if index==1 else 1
  bs.inputs['Base Color'].default_value=(*[float(x*factor) for x in gold],1);m.diffuse_color=bs.inputs['Base Color'].default_value
  for node in m.node_tree.nodes:
   if node.type!='TEX_IMAGE' or not node.image:continue
   name=Path(node.image.filepath).name
   if name in ['Rim_brushed_reference_color.png','Rim_brushed_reference_roughness.png']:
    im=bpy.data.images.load(str(C/'textures'/name),check_existing=False);im.colorspace_settings.name='sRGB' if 'color' in name else 'Non-Color';im.pack();node.image=im
  if index==0:bs.inputs['Roughness'].default_value=.205
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':a.spaces.active.region_3d.view_rotation=Quaternion((1,0,0,0))
bpy.data.libraries.write(str(C/'emerald_trophy.blend'),{scene},compress=True)
print('Complete trophy saved with warmer polished gold rim')
