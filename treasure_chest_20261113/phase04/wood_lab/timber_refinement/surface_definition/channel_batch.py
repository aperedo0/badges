from pathlib import Path
import subprocess
D=Path(__file__).resolve().parent;W=D.parent;exe='/Applications/Blender.app/Contents/MacOS/Blender';key='AV_channel_shoulders'
for tag,cmd in [('build',[exe,'-b','-t','8','-P',str(D/'build.py'),'--',key]),('normals',['/private/tmp/chest_wood_env/bin/python',str(D/'solve_local_normals.py'),key]),('pack',[exe,'-b','-t','8','-P',str(D/'pack.py'),'--',key]),('render',[exe,'-b','-t','8','-P',str(D/'render.py'),'--',key,'close','softwarm'])]:
 with (D/(key+'_'+tag+'.log')).open('w') as log:p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError(tag)
 print('COMPLETE',tag,flush=True)
assert (W/key/'close_softwarm.png').exists()
