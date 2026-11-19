from pathlib import Path
import subprocess,sys
D=Path(__file__).resolve().parent;S=D.parent/'surface_definition';B='/Applications/Blender.app/Contents/MacOS/Blender';key=sys.argv[1]
jobs=[('build',[B,'-b','-t','8','-P',str(S/'build.py'),'--',key]),('normals',['/private/tmp/chest_wood_env/bin/python',str(D/'solve_normals.py'),key]),('pack',[B,'-b','-t','8','-P',str(S/'pack.py'),'--',key]),('close',[B,'-b','-t','8','-P',str(S/'render.py'),'--',key,'close','softwarm']),('right',[B,'-b','-t','8','-P',str(S/'render.py'),'--',key,'right','softwarm'])]
for tag,cmd in jobs:
 if tag=='build' and (D.parent/key/'normal_frames.npz').exists():continue
 with (D/(key+'_'+tag+'.log')).open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError(tag)
 print('COMPLETE',key,tag,flush=True)
