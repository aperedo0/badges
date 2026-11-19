from pathlib import Path
D=Path(__file__).resolve().parent;OLD=D.parent/'lower_iron';code=(OLD/'render.py').read_text();code=code.replace("D=Path(__file__).resolve().parent;",'D=Path('+repr(str(D))+');',1).replace("C=D/key;lock=","C=D/key;C.mkdir(exist_ok=True);lock=")
code=code.replace("bpy.ops.wm.open_mainfile(filepath=str(C/'master.blend'))","bpy.ops.wm.open_mainfile(filepath=str(D/'baseline.blend'))")
insert="""
import math
mode=key
if 'noFill' in mode:sc.objects['Lab Chest Development Fill'].hide_render=True
if 'noRear' in mode:sc.objects['Lab Chest Development Rear'].hide_render=True
if mode.startswith('C'):
 obj=sc.objects['Lab Chest Lower Rim'];obj.data=obj.data.copy();mat=obj.data.materials[0].copy();obj.data.materials[0]=mat;bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 for name in ['Base Color','Roughness','Metallic']:
  for link in list(bs.inputs[name].links):mat.node_tree.links.remove(link)
 rgb=[196/255,198/255,198/255];linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb];bs.inputs['Base Color'].default_value=(*linear,1);bs.inputs['Metallic'].default_value=1;bs.inputs['Roughness'].default_value=.32 if 'r32' in mode else .50 if 'r50' in mode else .45
 (C/'clean_iron.json').write_text(json.dumps(dict(source='Google Filament Materials common metals table',srgb='#C4C6C6',linear=linear,roughness=bs.inputs['Roughness'].default_value,existing_geometry_and_bump_retained=True),indent=2))
if mode.startswith(('B','D')) or mode.startswith('C') and 'current' not in mode:
 neutral=not mode.startswith('D')
 if neutral:
  for obj in sc.objects:
   if obj.type=='LIGHT':obj.hide_render=True
 sc.world=sc.world.copy();sc.world.use_nodes=True;nt=sc.world.node_tree;nt.nodes.clear();env=nt.nodes.new('ShaderNodeTexEnvironment');env.image=bpy.data.images.load(str(D/'resources/studio_small_03_1k.hdr'));env.image.pack();coord=nt.nodes.new('ShaderNodeTexCoord');mapping=nt.nodes.new('ShaderNodeMapping');mapping.inputs['Rotation'].default_value[2]=math.radians(90 if 'rot90' in mode else 0);nt.links.new(coord.outputs['Generated'],mapping.inputs['Vector']);nt.links.new(mapping.outputs['Vector'],env.inputs['Vector']);bg=nt.nodes.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=.65 if neutral else .30
 if neutral:
  gray=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(env.outputs['Color'],gray.inputs[0]);nt.links.new(gray.outputs[0],bg.inputs['Color'])
 else:
  color=nt.nodes.new('ShaderNodeMixRGB');color.blend_type='MULTIPLY';color.inputs[0].default_value=1;color.inputs[2].default_value=(1,.80,.60,1);nt.links.new(env.outputs['Color'],color.inputs[1]);nt.links.new(color.outputs[0],bg.inputs['Color'])
 output=nt.nodes.new('ShaderNodeOutputWorld');nt.links.new(bg.outputs[0],output.inputs['Surface'])
 (C/'environment.json').write_text(json.dumps(dict(hdri='Poly Haven Studio Small 03',neutral=neutral,rotation=90 if 'rot90' in mode else 0,strength=bg.inputs['Strength'].default_value,existing_lights_retained=not neutral),indent=2))
"""
needle="if view in ['context','full','context_reflection']:frame('full')";assert needle in code;code=code.replace(needle,insert+'\n'+needle,1);exec(compile(code,'reused_diagnostic_renderer','exec'))
