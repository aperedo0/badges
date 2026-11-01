"""Record native simulator video because screenshot recording misses gesture frames."""
from pathlib import Path
import sys,subprocess,time,signal
ROOT=Path(__file__).resolve().parent;R=ROOT/sys.argv[1];C=R/(R/'candidate.txt').read_text().strip();UDID='DF439C70-9FD7-4EF7-998E-43AF5F83A588';out=C/'full_turn.mp4'
AXE='/Users/antonioperedo/.npm/_npx/99336612077b7094/node_modules/xcodebuildmcp/bundled/axe'
def swipe(a,b,d):subprocess.run([AXE,'swipe','--start-x','200','--start-y',str(a),'--end-x','200','--end-y',str(b),'--duration',str(d),'--delta','2','--udid',UDID],check=True,capture_output=True)
swipe(250,750,2);time.sleep(1)
if out.exists():out.rename(C/'full_turn_capture_stream.mp4')
p=subprocess.Popen(['xcrun','simctl','io',UDID,'recordVideo','--codec=h264',str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
try:
 time.sleep(1.5);swipe(600,390,8);time.sleep(1)
finally:
 p.send_signal(signal.SIGINT);_,err=p.communicate(timeout=20)
 if p.returncode:raise RuntimeError(err.decode())
print(out)
swipe(250,750,2)
