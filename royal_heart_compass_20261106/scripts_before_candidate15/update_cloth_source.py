from pathlib import Path
import bpy
R=Path('/Users/antonioperedo/Desktop/badges/royal_heart_compass_20261106');key=(R/'active.txt').read_text().strip();C=R/key/'candidate14';scene=bpy.context.scene
ob=next(o for o in scene.objects if o.type=='MESH' and 'velvet cushion' in o.name);mat=ob.data.materials[0];bs=mat.node_tree.nodes.get('Principled BSDF');node=bs.inputs['Base Color'].links[0].from_node
image=bpy.data.images.load(str(C/'textures/velvet_fold_color.png'),check_existing=False);image.pack();node.image=image
bpy.data.libraries.write(str(C/'source'/(key+'.blend')),{scene},compress=True)
print(key,'current cloth image packed in the complete live Blender source')
