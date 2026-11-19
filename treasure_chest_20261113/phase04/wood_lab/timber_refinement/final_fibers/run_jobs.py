from pathlib import Path
import subprocess,sys,os
D=Path(__file__).resolve().parent;exe='/Applications/Blender.app/Contents/MacOS/Blender'
for job in sys.argv[1:]:
 key,view,light=job.split(':');F=D if key=='baseline' else D.parent/key;out=F/(view+'_'+light+('_final' if os.environ.get('WOOD_FINAL')=='1' else '')+'.png')
 if out.exists():continue
 with (D/(key+'_'+view+'_'+light+'.log')).open('w') as log:p=subprocess.run([exe,'-b','-t','8','-P',str(D/'render.py'),'--',key,view,light],stdout=log,stderr=subprocess.STDOUT)
 if p.returncode or not out.exists():raise RuntimeError(job+' failed')
 print('COMPLETE',job,flush=True)
