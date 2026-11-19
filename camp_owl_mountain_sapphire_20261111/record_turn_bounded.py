"""Native full turn with a local stop watchdog, independent of model connectivity."""
from pathlib import Path
import json,sys,time,subprocess,signal,threading,hashlib
from PIL import Image
import numpy as np
from native_identity import verify,AXE,UDID
R=Path(__file__).resolve().parent;slug,candidate=sys.argv[1:3];C=R/slug/candidate;out=C/'app';out.mkdir(exist_ok=True)
def guard():
 state=json.loads((R/'schedule.json').read_text());assert state['status']=='active'
 assert not state['badges'][slug].get('owner_hold',False),'Owner put this badge on hold'
 if state['phase']=='work':assert time.time()+25<state['work_until_epoch']
 else:assert state['phase']=='continuous' and state.get('pacing_mode')=='continuous'
 assert json.loads((R/'progress.json').read_text())['status']=='working'
guard();verify(slug,out/'video_identity_before.json')
row=next(q for q in json.loads((R/'gallery.json').read_text()) if q['slug']==slug)
container=Path(subprocess.check_output(['xcrun','simctl','get_app_container',UDID,'com.antonioperedo.badgestudio.preview','data'],text=True).strip());cached=container/'tmp'/(row['dataset']+'.usdz');assert cached.read_bytes()==(C/'model.usdz').read_bytes()
subprocess.run([AXE,'swipe','--start-x','200','--start-y','250','--end-x','200','--end-y','750','--duration','1','--delta','1','--udid',UDID],check=True,capture_output=True,timeout=20);time.sleep(.6)
rest=out/'video_rest.png';subprocess.run(['xcrun','simctl','io',UDID,'screenshot',str(rest)],check=True,capture_output=True,timeout=20)
a=np.asarray(Image.open(rest).convert('RGB')).astype(int);red,green,blue=a[500:2100,950:1150].transpose(2,0,1);ys=np.where(((blue-red>40)&(blue-green>20)&(blue>120)&(red>50)&(green>80)).sum(1)>8)[0];assert len(ys)>8
header=float(np.median(ys)+500);expected=json.loads((out/'capture.json').read_text())['front_header_y'];assert abs(header-expected)<2.5,(header,expected)
guard();output=out/'full_turn_bounded.mp4';assert not output.exists()
with (out/'record_turn.log').open('w') as log:
 process=subprocess.Popen(['xcrun','simctl','io',UDID,'recordVideo','--codec=h264',str(output)],stdin=subprocess.DEVNULL,stdout=log,stderr=log)
 def stop():
  if process.poll() is None:process.send_signal(signal.SIGINT)
 watchdog=threading.Timer(16,stop);watchdog.daemon=True;watchdog.start();began=time.time();gesture_began=None
 try:
  time.sleep(.8);gesture_began=time.time();subprocess.run([AXE,'swipe','--start-x','200','--start-y','600','--end-x','200','--end-y','367','--duration','8','--delta','1','--udid',UDID],capture_output=True,check=True,timeout=12);time.sleep(.6)
 finally:
  stop()
  try:process.wait(timeout=8)
  except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=5)
  watchdog.cancel()
assert output.exists() and output.stat().st_size>100000
metadata=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,duration,nb_frames','-of','json',str(output)],text=True))
stream=metadata['streams'][0];assert stream['width']==1206 and stream['height']==2622;assert 8<float(stream['duration'])<20
subprocess.run([AXE,'swipe','--start-x','200','--start-y','250','--end-x','200','--end-y','750','--duration','1','--delta','1','--udid',UDID],check=True,capture_output=True,timeout=20)
verify(slug,out/'video_identity_after.json')
proof=dict(native_recording=True,model_sha256=hashlib.sha256((C/'model.usdz').read_bytes()).hexdigest(),local_watchdog_seconds=16,process_pid=process.pid,recording_began_epoch=began,gesture_began_epoch=gesture_began,verified_rest_header_y=header,video=stream,recording_stopped=True,motion_review_pending=True,reason='Native local fallback gives a duration limit that separate MCP start and stop calls cannot guarantee during a connection or tool failure')
(out/'video_validation.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2),flush=True)
