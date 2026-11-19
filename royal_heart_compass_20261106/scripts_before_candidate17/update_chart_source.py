from pathlib import Path
import bpy
R=Path('/Users/antonioperedo/Desktop/badges/royal_heart_compass_20261106');C=R/'ocean_navigator/candidate16';scene=bpy.context.scene
ob=next(o for o in scene.objects if o.type=='MESH' and o.name.startswith('Double sided navy nautical chart body'));mat=ob.data.materials[0];bs=mat.node_tree.nodes.get('Principled BSDF');node=bs.inputs['Base Color'].links[0].from_node;node.image=bpy.data.images.load(str(C/'textures/chart_color.png'),check_existing=False);node.image.pack();bpy.data.libraries.write(str(C/'source/ocean_navigator.blend'),{scene},compress=True);print('Current chart texture packed into actual working compass source')
