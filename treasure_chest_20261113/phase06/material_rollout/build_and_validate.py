from pathlib import Path
import subprocess,json,hashlib
D=Path(__file__).resolve().parent;B='/Applications/Blender.app/Contents/MacOS/Blender'
for step in ['build_rollout','validate']:
 log=D/(step+'.log')
 with log.open('w') as f:result=subprocess.run([B,'-b','-t','4','-P',str(D/(step+'.py'))],stdout=f,stderr=subprocess.STDOUT)
 assert result.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(),str(log)
v=json.loads((D/'validation.json').read_text());assert not v['uv_issues'];assert v['file_sha256']==hashlib.sha256((D/'master.blend').read_bytes()).hexdigest();print('Complete rollout validated with no collapsed large UV triangles',flush=True)
