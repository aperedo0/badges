from pathlib import Path
import sys,json,time,subprocess,hashlib,importlib.util,threading,signal
R=Path(__file__).resolve().parents[1];C=R/'candidate03';out=C/'app';out.mkdir(exist_ok=True)
p=R.parent/'ruby_heart_claude_20261107/tools/app_try.py';spec=importlib.util.spec_from_file_location('ruby_capture',p);a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
container=Path(subprocess.check_output(['xcrun','simctl','get_app_container',a.UDID,a.BUNDLE,'data'],text=True).strip());cached=container/'tmp/Badge3DPreviewRubyHeart.usdz'
for i in range(20):
 if cached.exists() and cached.read_bytes()==(C/'model.usdz').read_bytes():break
 time.sleep(1)
assert cached.read_bytes()==(C/'model.usdz').read_bytes(),'wrong model in app cache'
a.swipe(250,750);a.stable_shot(out/'front.png');rest=a.header_y(out/'front.png')
result=dict(model_sha256=hashlib.sha256(cached.read_bytes()).hexdigest(),front_header=rest)
a.POSES.update(early05=58.0,early10=60.0)
for pose,delta in a.POSES.items():
 if pose=='front':continue
 a.swipe(250,750);a.stable_shot(out/'_rest.png');target=rest-delta*3
 a.swipe(600,600-delta-10);p=a.stable_shot(out/(pose+'.png'))
 for _ in range(8):
  y=a.header_y(p)
  if abs(y-target)<=1.5:break
  c=(y-target)/3;c+=10 if c>0 else -10;a.swipe(600,600-c,1);p=a.stable_shot(out/(pose+'.png'))
 result[pose]=a.header_y(p)
a.swipe(250,750);a.stable_shot(out/'_rest.png')
(out/'capture.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
# A bounded local recording stops even if the model connection drops.
video=out/'full_turn.mp4'
with (out/'record.log').open('w') as log:
 proc=subprocess.Popen(['xcrun','simctl','io',a.UDID,'recordVideo','--codec=h264',str(video)],stdout=log,stderr=log)
 def stop():
  if proc.poll() is None:proc.send_signal(signal.SIGINT)
 timer=threading.Timer(16,stop);timer.start()
 try:
  time.sleep(.8);subprocess.run([a.AXE,'swipe','--start-x','200','--start-y','600','--end-x','200','--end-y','367','--duration','8','--delta','1','--udid',a.UDID],check=True,capture_output=True,timeout=12);time.sleep(.6)
 finally:
  stop()
  try:proc.wait(timeout=8)
  except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
  timer.cancel();a.swipe(250,750)
subprocess.run(['ffmpeg','-y','-i',str(video),'-vf','fps=2',str(out/'motion_%02d.png')],check=True,capture_output=True)
print('Native poses and full turn recorded. Front restored.')
