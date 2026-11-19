from pathlib import Path
F=Path(__file__).resolve().parent.parent/'iron_fidelity'
exec(compile((F/'environment.py').read_text(),'established_environment','exec'))
_established_apply_environment=apply_environment
def apply_environment(sc,F,mode):
 edge=mode in ['edge40','edge100','edge1000','edge100neutral','lower10','lower30','edge_slits','edge_fine','edge_balanced','edge_contrast','edge_soft','edge_level','edge_floor'];base_mode='neutral' if mode=='edge100neutral' else 'studio3' if edge or mode in ['reference','reference_lift'] else mode
 _established_apply_environment(sc,F,base_mode)
 if mode in ['reference','reference_lift','edge40','edge100','edge1000','lower10','lower30','edge_slits','edge_fine','edge_balanced','edge_contrast','edge_soft','edge_level','edge_floor']:
  nt=sc.world.node_tree;bg=next(n for n in nt.nodes if n.type=='BACKGROUND');bg.inputs['Strength'].default_value=.35 if mode in ['edge_contrast','edge_soft','edge_level','edge_floor'] else .65 if mode in ['reference_lift','edge40','edge100','edge1000','lower10','lower30','edge_slits','edge_fine','edge_balanced','edge_contrast','edge_soft','edge_level','edge_floor'] else .45;source=bg.inputs['Color'].links[0].from_socket;t=nt.nodes.new('ShaderNodeMixRGB');t.name='Restrained warm studio reflection tint';t.blend_type='MULTIPLY';t.inputs[0].default_value=1;t.inputs[2].default_value=(1,.88,.72,1);nt.links.new(source,t.inputs[1]);nt.links.new(t.outputs[0],bg.inputs['Color'])

 if edge:
  import sys
  local=Path(__file__).resolve().parent;sys.path.insert(0,str(local));from edge_reflection import add_edge_reflection
  if mode in ['edge_balanced','edge_contrast','edge_soft','edge_level','edge_floor']:
   add_edge_reflection(sc,local,250,False,'top',.01,6,True);add_edge_reflection(sc,local,12.75 if mode=='edge_floor' else 4.25,False,'bottom',.06 if mode=='edge_soft' else .01,6,True,mode in ['edge_level','edge_floor'])
  elif mode=='edge_fine':
   add_edge_reflection(sc,local,100,False,'top',.01);add_edge_reflection(sc,local,1.7,False,'bottom',.01)
  elif mode=='edge_slits':
   add_edge_reflection(sc,local,150,False,'top',.03);add_edge_reflection(sc,local,3,False,'bottom',.035)
  else:add_edge_reflection(sc,local,10 if mode=='lower10' else 30 if mode=='lower30' else 40 if mode=='edge40' else 1000 if mode=='edge1000' else 100,mode=='edge100neutral','bottom' if mode.startswith('lower') else 'top')
