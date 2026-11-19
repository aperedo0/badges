import subprocess,sys
from pathlib import Path
D=Path(__file__).resolve().parent;exe='/Applications/Blender.app/Contents/MacOS/Blender'
for mode in sys.argv[1:]:
 if (D/'renders'/(mode+'.png')).exists():continue
 with (D/(mode+'.log')).open('w') as f:p=subprocess.run([exe,'-b','-t','8','-P',str(D/'render_evidence.py'),'--',mode],stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise SystemExit(p.returncode)
 if not (D/'renders'/(mode+'.png')).exists():raise RuntimeError(mode+' failed to write a render')
 print('COMPLETE',mode,flush=True)
