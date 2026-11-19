from pathlib import Path
import subprocess,sys,os
D=Path(__file__).resolve().parent;B='/Applications/Blender.app/Contents/MacOS/Blender'
for job in sys.argv[1:]:
 key,view=job.split(':');tag='build' if view=='build' else key+'_'+view
 cmd=[B,'-b','-t','8','-P',str(D/('build.py' if view=='build' else 'render.py')),'--',key]+([] if view=='build' else [view])
 with (D/(key+'_'+tag+'.log')).open('w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError(job)
 print('COMPLETE',job,flush=True)
