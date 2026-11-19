from pathlib import Path
import subprocess
D=Path(__file__).resolve().parent
exe='/Applications/Blender.app/Contents/MacOS/Blender'
for script,args in [('validate_selected.py',[])]+[('render_selected.py',['--','R_layers_full',m]) for m in ['neutral_close','clay_graze','cinema_full']]:
 tag=script if not args else args[-1]
 with (D/(tag+'.log')).open('w') as log:
  subprocess.run([exe,'--background','--python',str(D/script)]+args,stdout=log,stderr=subprocess.STDOUT,check=True)
 print('SAVED',tag,flush=True)
