from pathlib import Path
import bpy
R=Path('/Users/antonioperedo/Desktop/badges/royal_heart_compass_20261106');C=R/'ruby_crown/candidate15';B=R/'ruby_crown/candidate14/source/ruby_crown.blend'
with bpy.data.libraries.load(str(B),link=False) as (src,dst):dst.scenes=[src.scenes[0]]
scene=dst.scenes[0];bpy.context.window.scene=scene;ob=next(o for o in scene.objects if o.type=='MESH' and 'velvet cushion' in o.name);mat=ob.data.materials[0];bs=mat.node_tree.nodes.get('Principled BSDF');node=bs.inputs['Base Color'].links[0].from_node;image=bpy.data.images.load(str(C/'textures/velvet_fold_color.png'),check_existing=False);image.pack();node.image=image;ob['cloth_appearance_fit']='Reference calibrated cloth tones. Actual geometry, normal map, metal and optical stones preserved. Native motion review pending.'
bpy.data.libraries.write(str(C/'source/ruby_crown.blend'),{scene},compress=True);print('Complete Ruby15 source saved with packed trial cloth tones')
