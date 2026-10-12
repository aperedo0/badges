"""The user's exact build/relaunch/shot protocol; always restores the ONE asset."""
import sys,json,subprocess,shutil,time,re,hashlib,signal
from pathlib import Path
root=Path(__file__).resolve().parents[1];directory=Path(sys.argv[1]).resolve()
repo=Path('/Users/antonioperedo/Desktop/screen_time');relative='ScreenTime/SupportingFiles/Assets.xcassets/TestBadge3DModel.dataset/silver_badge_mobile.usdz'
sim='69A29DD2-C91E-487A-81B9-3B146DF8F07B';bundle='com.antonioperedo.screentime.uidev'
def run(args,name,check=True):
 result=subprocess.run(args,cwd=repo,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 (directory/name).write_text(result.stdout)
 print(name,'exit',result.returncode,flush=True)
 if check:assert result.returncode==0,(name,result.stdout[-2000:])
 return result.stdout
status=subprocess.check_output(['git','status','--porcelain','--',relative],cwd=repo,text=True)
assert not status,'STOP: app asset has pre-existing changes. Ask user before proceeding: '+status
before=hashlib.sha256((repo/relative).read_bytes()).hexdigest()
(directory/'repo_status_before.txt').write_text(subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True))
def parse(text):
 m=re.search(r'loaded_3d=(True|False) rim_top=([0-9.]+) emblem_clip=(\d+) emblem_mean=([0-9.]+)',text);assert m,text
 return {'loaded_3d':m[1]=='True','rim_top':float(m[2]),'emblem_clip':int(m[3]),'emblem_mean':float(m[4])}
try:
 shutil.copyfile(directory/'mobile/iron_badge_mobile.usdz',repo/relative)
 run(['tools/sim/app','build'],'app_build.txt')
 run(['tools/sim/app','launch'],'app_launch.txt');time.sleep(15)
 for i in [1,2]:
  run(['xcrun','simctl','terminate',sim,bundle],f'app_terminate_{i}.txt',check=False);time.sleep(1)
  run(['xcrun','simctl','launch',sim,bundle],f'app_relaunch_{i}.txt');time.sleep(15)
 run(['tools/sim/shot',str(directory/'app_rest.png')],'app_shot.txt')
 measurement=run(['/usr/local/bin/python3',str(root/'app_reference/measure_app_shot.py'),str(directory/'app_rest.png')],'measure_app_output.txt')
 data=parse(measurement)
 if not data['loaded_3d']:
  shutil.copy2(directory/'app_rest.png',directory/'app_fallback_before_retry.png')
  run(['xcrun','simctl','terminate',sim,bundle],'app_terminate_retry.txt',check=False);time.sleep(1)
  run(['xcrun','simctl','launch',sim,bundle],'app_relaunch_retry.txt');time.sleep(20)
  run(['tools/sim/shot',str(directory/'app_rest.png')],'app_shot_retry.txt')
  measurement=run(['/usr/local/bin/python3',str(root/'app_reference/measure_app_shot.py'),str(directory/'app_rest.png')],'measure_app_output.txt');data=parse(measurement)
 data.update(candidate_sha256=hashlib.sha256((directory/'mobile/iron_badge_mobile.usdz').read_bytes()).hexdigest(),passes_numeric_app_checks=data['loaded_3d'] and data['emblem_clip']<=800 and 142<=data['rim_top']<=152)
 (directory/'app_metrics.json').write_text(json.dumps(data,indent=2));print(json.dumps(data),flush=True)
finally:
 restored=subprocess.run(['git','checkout','--',relative],cwd=repo,capture_output=True,text=True)
 assert restored.returncode==0,restored.stderr
 after=subprocess.check_output(['git','status','--porcelain','--',relative],cwd=repo,text=True)
 allstatus=subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True)
 (directory/'repo_status_after.txt').write_text(allstatus)
 assert not after,after
 assert hashlib.sha256((repo/relative).read_bytes()).hexdigest()==before,'Restore bytes mismatch'
 print('RESTORED app asset; full git status:',repr(allstatus),flush=True)
