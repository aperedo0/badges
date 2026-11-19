from pathlib import Path
import subprocess,sys
D=Path(__file__).resolve().parent;exe='/Applications/Blender.app/Contents/MacOS/Blender'
for key in sys.argv[1:]:
 for tag,args in [('build',['-P',str(D/'build.py'),'--',key]),('normals',[]),('pack',['-P',str(D/'pack.py'),'--',key]),('render',['-P',str(D/'render.py'),'--',key,'close','balanced'])]:
  with (D/(key+'_'+tag+'.log')).open('w') as log:p=subprocess.run((['/private/tmp/chest_wood_env/bin/python',str(D/'solve_normals.py'),key] if tag=='normals' else [exe,'-b','-t','8']+args),stdout=log,stderr=subprocess.STDOUT)
  if p.returncode:raise SystemExit(p.returncode)
  if tag=='render' and not (D.parent/key/'close_balanced.png').exists():raise RuntimeError(key+' render failed')
  print('COMPLETE',key,tag,flush=True)
