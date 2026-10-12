import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];r=Path(sys.argv[1]).resolve();assert 1<=int(r.name)<=8
with (r/'build_and_checks.txt').open('w') as f:p=subprocess.run([sys.executable,str(root/'scripts/build_iteration.py'),str(r)],stdout=f,stderr=subprocess.STDOUT)
assert p.returncode==0,(r/'build_and_checks.txt').read_text()[-2400:]
print('BUILD and structural checks PASS',flush=True)
jobs=[]
for script,log in [('test_in_app.py','app_test_protocol.txt'),('render_iteration.py','render_and_metrics.txt')]:
 f=(r/log).open('w');p=subprocess.Popen([sys.executable,str(root/'scripts'/script),str(r)],stdout=f,stderr=subprocess.STDOUT);p.wait();jobs.append((p,f,script,log))
failed=[]
for p,f,script,log in jobs:
 code=p.wait();f.close();print(script,'exit',code,flush=True)
 if code:failed.append((script,(r/log).read_text()[-2500:]))
assert not failed,failed
print('Iteration exported, measured in Blender and tested in real app; repo asset restored.',flush=True)
