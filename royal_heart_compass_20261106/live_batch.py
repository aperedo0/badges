import os
from pathlib import Path
import sys,json,time,subprocess
sys.path.insert(0,'/Users/antonioperedo/Desktop/badges/water_match_20261014')
from blender_live import command
root=Path('/Users/antonioperedo/Desktop/badges/royal_heart_compass_20261106')
for key in sys.argv[1:]:
 subprocess.run([sys.executable,str(root/'work_guard.py'),'180','live Blender badge modeling',key],check=True)
 (root/'active.txt').write_text(key)
 print(key,command('execute_code',{'code':"import os\nos.environ['BADGE_CANDIDATE']="+repr(os.environ.get('BADGE_CANDIDATE','candidate21'))+"\n"+(root/'build_live.py').read_text()}),flush=True)
 print(command('get_viewport_screenshot',{'filepath':str(root/key/os.environ.get('BADGE_CANDIDATE','candidate21')/'review/viewport.png'),'max_size':1400}),flush=True)
 (root/'progress.json').write_text(json.dumps(dict(last_blender_checkpoint=key,stage='Blender inspection',complete=False),indent=2))
