import sys,subprocess,shutil
from pathlib import Path
r=Path(sys.argv[1]).resolve();blender='/Applications/Blender.app/Contents/MacOS/Blender'
for name,script in [('build','build_iron.py'),('export','export_mobile.py')]:
 with (r/f'logs/{name}.log').open('w') as log:p=subprocess.run([blender,'--background','--factory-startup','--python',str(r/'scripts'/script)],stdout=log,stderr=subprocess.STDOUT)
 assert p.returncode==0 and 'Traceback' not in (r/f'logs/{name}.log').read_text(),(name,(r/f'logs/{name}.log').read_text()[-1800:])
 print('PASS',name,flush=True)
shutil.copy2(r/'mobile/iron_badge_mobile.usdz',r/'iron_badge_mobile.usdz')
with (r/'logs/full_verification_run.txt').open('w') as log:p=subprocess.run([sys.executable,str(r/'scripts/run_verification.py')],stdout=log,stderr=subprocess.STDOUT)
assert p.returncode==0,(r/'logs/full_verification_run.txt').read_text()
print('PASS all structural checks',flush=True)
