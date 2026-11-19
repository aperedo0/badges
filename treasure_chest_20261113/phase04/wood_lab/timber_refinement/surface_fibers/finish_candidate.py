from pathlib import Path
import subprocess
D=Path(__file__).resolve().parent;exe='/Applications/Blender.app/Contents/MacOS/Blender';key='U_scan_fibers'
for tag,cmd in [('validate',[exe,'--background','--python',str(D/'validate_one.py'),'--',key])]+[(m,[exe,'--background','--python',str(D/'render_diagnostics.py'),'--',key,m]) for m in ['neutral_close','clay_graze','cinema_full']]:
 with (D/(tag+'.log')).open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
 print('SAVED',tag,flush=True)
