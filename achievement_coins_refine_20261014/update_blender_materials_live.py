from pathlib import Path
import bpy,json
R=Path('/Users/antonioperedo/Desktop/badges/achievement_coins_refine_20261014')
rough={'background':.90,'emerald_background':.42,'glass':.32,'water':.32,'silver':.36,'gold':.36,'bronze':.38,'emerald':.34,'soil':.48,'sand':.52}
for name in ['clean','hourglass_teal','hourglass_gold','sunrise','sprout']:
 scene=bpy.data.scenes[name];meta=json.loads((R/name/'design.json').read_text());materials={}
 for role in {f['role'] for f in meta['features']}:
  mat=bpy.data.materials.new('Fitted_'+name+'_'+role);mat.use_nodes=True;nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF')
  p.inputs['Metallic'].default_value=1.;p.inputs['Roughness'].default_value=rough[role]
  # Explicit world XY UVs match the packaged CoinReliefUV atlas.
  color=nodes.new('ShaderNodeTexImage');color.image=bpy.data.images.load(str(R/name/'textures'/(role+'_color.png')),check_existing=True)
  emission=nodes.new('ShaderNodeTexImage');emission.image=bpy.data.images.load(str(R/name/'textures'/(role+'_emission.png')),check_existing=True)
  color.image.colorspace_settings.name='sRGB';emission.image.colorspace_settings.name='sRGB'
  if role=='background':
   mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.03125,.03125,.03125,1);links.new(color.outputs['Color'],mix.inputs[1]);links.new(mix.outputs[0],p.inputs['Base Color'])
  else:links.new(color.outputs['Color'],p.inputs['Base Color'])
  links.new(emission.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=1.;materials[role]=mat
 for i,f in enumerate(meta['features']):
  for side in ['Front','Back']:
   obj=next(o for o in scene.objects if o.name.startswith(f'Relief{side}_{i}_{f["role"]}'))
   obj.data.materials.clear();obj.data.materials.append(materials[f['role']]);uv=obj.data.uv_layers.get('CoinReliefUV') or obj.data.uv_layers.new(name='CoinReliefUV')
   for loop in obj.data.loops:
    q=obj.data.vertices[loop.vertex_index].co;xx=q.x if side=='Front' else -q.x;uv.data[loop.index].uv=((xx+3.015)/6.03,(q.y+3.015)/6.03)
 bpy.context.window.scene=scene
bpy.ops.wm.save_as_mainfile(filepath=str(R/'coins.blend'),compress=True)
print('Fitted material maps saved in editable Blender scenes.')
