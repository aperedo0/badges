import subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;B='/Applications/Blender.app/Contents/MacOS/Blender'
for key in ['A_current','B_neutral','B_neutral_rot90','C_clean_r32','C_clean_r50','C_clean_current','D_warm_environment']:
 with (D/(key+'.log')).open('w') as f:r=subprocess.run([B,'-b','-t','8','-P',str(D/'render_control.py'),'--',key,'iron'],stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError(key)
 print('COMPLETE',key,flush=True)
