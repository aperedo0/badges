import bpy,json
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/water_match_20261014');scene=bpy.data.scenes.get('clean_physical_rim') or bpy.data.scenes['water_match'];bpy.context.window.scene=scene
rough={'water':.32,'silver':.36,'background':.90}
mats={}
for role,r in rough.items():
 mat=bpy.data.materials.new('Water_candidate_'+role);mat.use_nodes=True;nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF');p.inputs['Metallic'].default_value=1;p.inputs['Roughness'].default_value=r
 tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'clean/textures'/(role+'_color.png')),check_existing=True);tex.image.reload()
 if role=='background':
  mult=nodes.new('ShaderNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;mult.inputs[2].default_value=(.03125,.03125,.03125,1);links.new(tex.outputs['Color'],mult.inputs[1]);links.new(mult.outputs[0],p.inputs['Base Color'])
 else:links.new(tex.outputs['Color'],p.inputs['Base Color'])
 glow=nodes.new('ShaderNodeTexImage');glow.image=bpy.data.images.load(str(R/'clean/textures'/(role+'_emission.png')),check_existing=True);glow.image.reload();links.new(glow.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=16;mats[role]=mat
meta=json.loads((R/'clean/design.json').read_text())
for i,f in enumerate(meta['features']):
 for side in ['Front','Back']:
  obj=next(o for o in scene.objects if o.name.startswith(f'Relief{side}_{i}_{f["role"]}'));obj.data.materials.clear();obj.data.materials.append(mats[f['role']])
import sys
sys.path.insert(0,str(R.parent))
import coin_rim,importlib
importlib.reload(coin_rim)
coin_rim.apply_blender(scene,'clean')
bpy.data.libraries.write(str(R/'water.blend'),{scene},compress=True)
print('Water candidate material maps saved with the editable scene.')
