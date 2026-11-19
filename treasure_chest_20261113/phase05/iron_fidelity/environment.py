import bpy,math
from pathlib import Path
from mathutils import Vector

def apply_environment(sc,D,mode):
 if mode=='current':return
 neutral=mode=='neutral';sc.world=sc.world.copy();sc.world.use_nodes=True;nt=sc.world.node_tree;nt.nodes.clear();tex=nt.nodes.new('ShaderNodeTexEnvironment');tex.name='Poly Haven Studio Small 03';tex.image=bpy.data.images.load(str(D/'resources/studio_small_03_1k.hdr'),check_existing=True);tex.image.pack();coord=nt.nodes.new('ShaderNodeTexCoord');mapping=nt.nodes.new('ShaderNodeMapping');mapping.inputs['Rotation'].default_value[2]=0;nt.links.new(coord.outputs['Generated'],mapping.inputs['Vector']);nt.links.new(mapping.outputs['Vector'],tex.inputs['Vector']);bg=nt.nodes.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=.18 if mode=='studio5' else .65 if neutral else .45 if mode in ['studio3','studio3neutral','studio5'] else .55 if mode in ['studio','studio2'] else .30
 if neutral or mode in ['studio','studio2','studio3','studio3neutral','studio5']:
  for o in sc.objects:
   if o.type=='LIGHT':o.hide_render=True
  gray=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(tex.outputs['Color'],gray.inputs[0]);nt.links.new(gray.outputs[0],bg.inputs['Color'])
 else:
  multiply=nt.nodes.new('ShaderNodeMixRGB');multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=1;multiply.inputs[2].default_value=(1,.80,.60,1);nt.links.new(tex.outputs['Color'],multiply.inputs[1]);nt.links.new(multiply.outputs[0],bg.inputs['Color'])
 if mode in ['studio','studio2','studio3','studio3neutral','studio5']:
  src=sc.objects.get('Lab Chest Development Key') or next(o for o in sc.objects if o.get('source_light')=='Lab Chest Development Key');src.data=src.data.copy();src.hide_render=False;src.data.energy*=.23;src.data.color=(1,.58,.26)
 if mode in ['studio2','studio3','studio3neutral','studio5']:
  fill=sc.objects.get('Lab Chest Development Fill') or next(o for o in sc.objects if o.get('source_light')=='Lab Chest Development Fill');fill.data=fill.data.copy();fill.hide_render=False;fill.data.energy*=.18;fill.data.color=(1,.50,.18);fill.data.size=1.4
  if mode in ['studio3','studio3neutral','studio5']:
   fill.data.energy*=.50/.18;fill.location.z+=2.5;fill.rotation_euler=(Vector((.94,-1.51,-1.96))-fill.location).to_track_quat('-Z','Y').to_euler();fill.data.size=1.2
  if mode=='studio3neutral':
   src.data.color=(1,1,1);fill.data.color=(1,1,1)
 output=nt.nodes.new('ShaderNodeOutputWorld');nt.links.new(bg.outputs[0],output.inputs['Surface'])
