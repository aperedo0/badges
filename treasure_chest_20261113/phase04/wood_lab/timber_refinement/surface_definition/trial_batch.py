from pathlib import Path
import subprocess,shutil
D=Path(__file__).resolve().parent;W=D.parent;exe='/Applications/Blender.app/Contents/MacOS/Blender'
def run(key,tag,args,python=False):
 with (D/(key+'_'+tag+'.log')).open('w') as log:p=subprocess.run((['/private/tmp/chest_wood_env/bin/python'] if python else [exe,'-b','-t','8'])+args,stdout=log,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError(key+' '+tag)
 print('COMPLETE',key,tag,flush=True)
a='AG_fiber_facets';b='AH_aged_fibers'
run(a,'build',['-P',str(D/'build.py'),'--',a]);assert (W/a/'geometry.blend').exists()
run(a,'normals',[str(D/'solve_normals.py'),a],True);run(a,'pack',['-P',str(D/'pack.py'),'--',a]);run(a,'render',['-P',str(D/'render.py'),'--',a,'close','balanced']);assert (W/a/'close_balanced.png').exists()
for name in ['geometry.blend','normal_frames.npz','normal.png','validation.json']:shutil.copy2(W/a/name,W/b/name)
run(b,'pack',['-P',str(D/'pack.py'),'--',b]);run(b,'render',['-P',str(D/'render.py'),'--',b,'close','balanced']);assert (W/b/'close_balanced.png').exists()
