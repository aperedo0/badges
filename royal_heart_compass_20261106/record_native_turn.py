"""Bounded native simulator recording when the tool transport is unavailable."""
from pathlib import Path
import sys,subprocess,time,signal,json,os
from native_pose import reset,AXE,UDID
from native_identity import verify
R=Path(__file__).resolve().parent;slug,mode=sys.argv[1:3];V=R/slug/mode/('review_baseline' if os.environ.get('BADGE_BASELINE')=='1' else 'review');out=V/'full_turn.mp4'
subprocess.run([sys.executable,str(R/'work_guard.py'),'120','bounded native badge turn',slug],check=True)
verify(slug,V/'video_identity_before.json')
reset(V/'video_rest.png')
if out.exists():out.rename(V/('previous_turn_'+str(int(time.time()))+'.mp4'))
record=subprocess.Popen(['xcrun','simctl','io',UDID,'recordVideo','--codec=h264',str(out)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
stop_method='SIGINT'
try:
 time.sleep(1)
 if record.poll() is not None:raise RuntimeError(record.communicate())
 subprocess.run([AXE,'swipe','--start-x','200','--start-y','600','--end-x','200','--end-y','367','--duration','8','--delta','1','--udid',UDID],check=True,capture_output=True,timeout=30)
finally:
 if record.poll() is None:record.send_signal(signal.SIGINT)
 try:stdout,stderr=record.communicate(timeout=20)
 except subprocess.TimeoutExpired:
  stop_method='SIGTERM after SIGINT timeout'
  record.terminate();stdout,stderr=record.communicate(timeout=10)
 (V/'native_recorder.log').write_text(stdout+'\n'+stderr)
for flush_attempt in range(20):
 if out.exists() and out.stat().st_size>10000:break
 time.sleep(.5)
assert out.exists() and out.stat().st_size>10000
verify(slug,V/'video_identity_after.json')
probe=subprocess.run(['/opt/homebrew/bin/ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,width,height','-of','json',str(out)],capture_output=True,text=True,check=True)
info=json.loads(probe.stdout);assert float(info['format']['duration'])>7
(V/'native_recorder.json').write_text(json.dumps(dict(method='native simulator recorder',reason='XcodeBuildMCP transport closed',gesture_seconds=8,recorder_pid=record.pid,all_recording_processes_awaited=True,stop_method=stop_method,validated_video=info),indent=2));print(slug,mode,'bounded native turn saved')
