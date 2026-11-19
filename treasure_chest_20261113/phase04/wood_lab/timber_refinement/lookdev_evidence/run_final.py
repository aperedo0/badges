import subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;C=D.parent/'V_lookdev_refinement';exe='/Applications/Blender.app/Contents/MacOS/Blender'
for view in ['full','plank','right','close']:
 if (C/(view+'.png')).exists():continue
 with (D/(view+'_final.log')).open('w') as f:p=subprocess.run([exe,'-b','-t','8','-P',str(D/'render_final.py'),'--',view],stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise SystemExit(p.returncode)
 if not (C/(view+'.png')).exists():raise RuntimeError(view+' render did not complete')
 print('COMPLETE',view,flush=True)
