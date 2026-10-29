"""Save native simulator views using slow badge turns."""
from pathlib import Path
import sys,time,subprocess,json,os
ROOT=Path(__file__).resolve().parent;key=sys.argv[1];R=ROOT/key;C=R/((R/'candidate.txt').read_text().strip() if (R/'candidate.txt').exists() else 'candidate01')
UDID='DF439C70-9FD7-4EF7-998E-43AF5F83A588'
AXE='/Users/antonioperedo/.npm/_npx/99336612077b7094/node_modules/xcodebuildmcp/bundled/axe'
def swipe(a,b,duration=2):subprocess.run([AXE,'swipe','--start-x','200','--start-y',str(a),'--end-x','200','--end-y',str(b),'--duration',str(duration),'--udid',UDID],check=True,capture_output=True)
def shot(name):
 temporary=Path('/tmp')/('crest_'+key+'_'+name+'_'+str(os.getpid())+'.png')
 result=subprocess.run(['xcrun','simctl','io',UDID,'screenshot',str(temporary)],capture_output=True,text=True)
 if result.returncode:raise RuntimeError(result.stdout+result.stderr)
 (C/('app_'+name+'.png')).write_bytes(temporary.read_bytes());temporary.unlink();print(name,flush=True)
swipe(250,750);time.sleep(1);shot('front')
for name,delta in [('side_left',94),('back',133),('side_right',171)]:
 swipe(600,600-delta);time.sleep(1);shot(name);swipe(250,750);time.sleep(1)
shot('front')
