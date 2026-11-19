import sys
from pathlib import Path
D=Path(__file__).resolve().parent;OLD=D.parent/'lower_iron';env=sys.argv[sys.argv.index('--')+3];code=(OLD/'render.py').read_text();code=code.replace("D=Path(__file__).resolve().parent;",'D=Path('+repr(str(D))+');',1).replace("C=D/key;lock=","C=D/key;C.mkdir(exist_ok=True);lock=").replace("bpy.ops.wm.open_mainfile(filepath=str(C/'master.blend'))","bpy.ops.wm.open_mainfile(filepath=str(D/'baseline.blend' if key=='baseline' else C/'master.blend'))").replace("out=C/(view+('_final' if final else '')+'.png')","out=C/(view+'_'+ENV+('_final' if final else '')+'.png')");needle="if view in ['context','full','context_reflection']:frame('full')";setup=(D/'environment.py').read_text()+"\napply_environment(sc,D,ENV)\n"+'''
if view=='graze':
 for obj in sc.objects:
  if obj.type=='LIGHT':obj.hide_render=True
 keylight=sc.objects['Lab Chest Development Key'];keylight.data=keylight.data.copy();keylight.hide_render=False;keylight.location=world((-3.4,-1.9,2.2));target=world((-1.2,-1.94,1.78));keylight.rotation_euler=(target-keylight.location).to_track_quat('-Z','Y').to_euler();keylight.data.color=(1,1,1);keylight.data.energy=350;keylight.data.size=.35
 for n in sc.world.node_tree.nodes:
  if n.type=='BACKGROUND':
   for l in list(n.inputs['Color'].links):sc.world.node_tree.links.remove(l)
   n.inputs['Color'].default_value=(.08,.08,.08,1);n.inputs['Strength'].default_value=.08
 obj=sc.objects['Lab Chest Lower Rim'];obj.data=obj.data.copy();m=obj.data.materials[0].copy();obj.data.materials[0]=m
 for n in m.node_tree.nodes:
  if n.type=='BSDF_PRINCIPLED':
   for socket in ['Base Color','Metallic','Roughness']:
    for link in list(n.inputs[socket].links):m.node_tree.links.remove(link)
   n.inputs['Base Color'].default_value=(.18,.18,.18,1);n.inputs['Metallic'].default_value=0;n.inputs['Roughness'].default_value=.75
''';code=code.replace("obj.name=='Lab Chest Lower Rim':continue","(obj.name=='Lab Chest Lower Rim' or obj.get('bottom_iron_finish',False)):continue");code=code.replace(needle,setup+needle,1);exec(compile(code,'reused_candidate_renderer','exec'),dict(__name__='__main__',__file__=__file__,ENV=env))
