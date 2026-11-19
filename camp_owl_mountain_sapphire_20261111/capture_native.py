"""Capture real phone pixels and measured poses after an official MCP launch."""
from pathlib import Path
import json,sys,subprocess,time,hashlib
import numpy as np
from PIL import Image
from native_identity import verify,AXE,UDID
R=Path(__file__).resolve().parent
slug,candidate=sys.argv[1:3];C=R/slug/candidate;out=C/'app';out.mkdir(exist_ok=True)
row=next(r for r in json.loads((R/'gallery.json').read_text()) if r['slug']==slug)
POSES=dict(front=0,early_turn=68,turn45=75.1,side_left=94.2528,turn135=113.4,back=132.5056,turn225=151.6,side_right=170.7583,turn315=189.9,full_turn=210)
poses=list(POSES)
if '--poses' in sys.argv:poses=sys.argv[sys.argv.index('--poses')+1].split(',')
def guard():
 state=json.loads((R/'progress.json').read_text())
 assert state['status']=='working','Badge work is paused or scheduled for later'
 if (R/'schedule.json').exists():
  schedule=json.loads((R/'schedule.json').read_text())
  assert schedule['status']=='active','Badge work is not active'
  assert not schedule['badges'][slug].get('owner_hold',False),'Owner put this badge on hold'
  if schedule['phase']=='work':
   assert time.time()<schedule['work_until_epoch'],'The work block ended; save and take the scheduled break'
  else:
   assert schedule['phase']=='continuous' and schedule.get('pacing_mode')=='continuous','No authorized active work mode'
def shot(path):
 guard();subprocess.run(['xcrun','simctl','io',UDID,'screenshot',str(path)],check=True,capture_output=True,timeout=20)
 return Image.open(path).convert('RGB')
def header(path):
 a=np.asarray(Image.open(path).convert('RGB')).astype(int);r,g,b=a[500:2100,950:1150].transpose(2,0,1)
 ys=np.where(((b-r>40)&(b-g>20)&(b>120)&(r>50)&(g>80)).sum(1)>8)[0]
 assert len(ys)>8,'Actual badge picker is not visible'
 return float(np.median(ys)+500)
def stable(path):
 previous=None;count=0
 for i in range(15):
  shot(path);current=header(path)
  count=count+1 if previous is not None and abs(current-previous)<=1 else 0
  if count>=2:return current
  previous=current;time.sleep(.2)
 raise RuntimeError('Native pose did not settle')
def swipe(y0,y1,duration=1):
 guard();subprocess.run([AXE,'swipe','--start-x','200','--start-y',str(y0),'--end-x','200','--end-y',str(y1),'--duration',str(duration),'--delta','1','--udid',UDID],check=True,capture_output=True,timeout=30)
def reset():
 swipe(250,750);return stable(out/'_rest.png')
verify(slug,out/'visible_identity_before.json')
container=Path(subprocess.check_output(['xcrun','simctl','get_app_container',UDID,'com.antonioperedo.badgestudio.preview','data'],text=True).strip())
cached=container/'tmp'/(row['dataset']+'.usdz');model=C/'model.usdz'
assert cached.exists() and cached.read_bytes()==model.read_bytes(),'The actual simulator loaded a different model'
rest=reset();proof=dict(loaded=True,model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),actual_cached_model=str(cached),front_header_y=rest,native_image_size=[1206,2622],capture_method='Native PNG because MCP screenshot is compressed to 368 by 800 JPEG',gesture_method='Precise local coordinates because MCP root swipe starts on the badge picker',poses={})
for pose in poses:
 guard()
 if pose!='front':
  reset();target=rest-POSES[pose]*3;swipe(600,600-POSES[pose]-10);time.sleep(.35)
 else:target=rest
 file=out/(pose+'.png');actual=stable(file)
 for correction in range(7):
  if abs(actual-target)<=1.5:break
  delta=(actual-target)/3
  delta+=10 if delta>0 else -10
  swipe(600,600-delta);actual=stable(file)
 assert abs(actual-target)<=2.5,(pose,actual,target)
 verify(slug,out/(pose+'_identity.json'))
 proof['poses'][pose]=dict(target_scroll_points=POSES[pose],actual_scroll_points=(rest-actual)/3,header_y=actual)
 (out/'capture.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(slug,pose,'actual scroll',round((rest-actual)/3,2),flush=True)
reset();verify(slug,out/'visible_identity_after.json')
print('Native measured poses complete:',slug,flush=True)
