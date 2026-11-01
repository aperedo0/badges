from pathlib import Path
import subprocess,time,sys
R=Path(__file__).resolve().parent;folder=R/sys.argv[1]/'review';folder.mkdir(exist_ok=True,parents=True)
A='/Users/antonioperedo/.npm/_npx/99336612077b7094/node_modules/xcodebuildmcp/bundled/axe';U='C18E609E-6C2F-49C4-BCFE-E5D365F4E4E8'
def swipe(a,b):subprocess.run([A,'swipe','--start-x','200','--start-y',str(a),'--end-x','200','--end-y',str(b),'--duration','2','--delta','2','--udid',U],check=True,capture_output=True)
def shot(name):
 subprocess.run(['xcrun','simctl','io',U,'screenshot',str(folder/(name+'.png'))],check=True,capture_output=True)
 print(name,flush=True)
swipe(250,750);time.sleep(1);shot('front')
for name,delta in [('side_left',94),('back',133),('side_right',171)]:
 swipe(600,600-delta);time.sleep(.5);shot(name);swipe(250,750);time.sleep(.4)
