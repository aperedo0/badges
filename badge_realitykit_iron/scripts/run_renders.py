import subprocess,sys
from pathlib import Path
r=Path('/Users/antonioperedo/Downloads/badge_realitykit_iron')
keys=sys.argv[1:]
for key in keys:
 for rig in ('stage','harsh'):
  for pose in (0,20):
   out=r/f'proof/renders/{key}_{rig}_{pose}.png'
   if out.exists():continue
   variant='master' if key=='master' else str(r/('mobile/iron_badge_mobile.usdz' if key=='iron' else 'source/silver_v3/silver_badge_mobile.usdz'))
   cmd=['/Applications/Blender.app/Contents/MacOS/Blender','--background',str(r/'scenes/iron_medallion_master.blend'),'--python',str(r/'scripts/render_proof.py'),'--','--variant',variant,'--rig',rig,'--pose',str(pose),'--samples','192','--out',str(out)]
   with open(r/f'logs/render_{key}_{rig}_{pose}.log','w') as log:p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
   assert p.returncode==0 and out.exists(),(key,rig,pose,p.returncode)
   print('FINISHED',key,rig,pose,flush=True)
