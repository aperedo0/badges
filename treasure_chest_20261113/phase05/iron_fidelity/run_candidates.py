import subprocess,sys
from pathlib import Path
D=Path(__file__).resolve().parent;B='/Applications/Blender.app/Contents/MacOS/Blender'
for job in sys.argv[1:]:
 key,view,env=job.split(':')
 with (D/(key+'_'+view+'_'+env+'.log')).open('w') as f:r=subprocess.run([B,'-b','-t','8','-P',str(D/'render_candidate.py'),'--',key,view,env],stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError(job)
 print('COMPLETE',job,flush=True)
