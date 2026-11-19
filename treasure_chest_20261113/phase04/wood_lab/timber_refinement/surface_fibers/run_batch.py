from pathlib import Path
import subprocess
D=Path(__file__).resolve().parent;W=D.parent
exe='/Applications/Blender.app/Contents/MacOS/Blender'
for key in ['S_fiber_structure','T_fiber_material']:
 for step,cmd in [('build',[exe,'--background',str(W/'R_layers_full/master.blend'),'--python',str(D/'build_one.py'),'--',key]),('render',[exe,'--background','--python',str(W/'grain_hierarchy/render_one.py'),'--',key])]:
  with (D/(key+'_'+step+'.log')).open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
  print('SAVED',key,step,flush=True)
