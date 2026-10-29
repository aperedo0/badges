"""Save early spin poses where moving metal reflections are easiest to inspect."""
from pathlib import Path
import sys,time,subprocess,os
ROOT=Path(__file__).resolve().parent;R=ROOT/sys.argv[1];C=R/(R/'candidate.txt').read_text().strip()
AXE='/Users/antonioperedo/.npm/_npx/99336612077b7094/node_modules/xcodebuildmcp/bundled/axe';UDID='DF439C70-9FD7-4EF7-998E-43AF5F83A588'
def swipe(a,b):subprocess.run([AXE,'swipe','--start-x','200','--start-y',str(a),'--end-x','200','--end-y',str(b),'--duration','2','--udid',UDID],check=True,capture_output=True)
for delta in [0,64,72,80,88,104,120]:
 swipe(250,750);time.sleep(.3)
 if delta:swipe(600,600-delta)
 time.sleep(.5);temporary=Path('/tmp')/('glint_'+str(os.getpid())+'.png')
 subprocess.run(['xcrun','simctl','io',UDID,'screenshot',str(temporary)],check=True,capture_output=True)
 (C/('spin_'+str(delta)+'.png')).write_bytes(temporary.read_bytes());temporary.unlink();print('spin',delta,flush=True)
swipe(250,750)
