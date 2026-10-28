from pathlib import Path
import subprocess,time
SIM='DF439C70-9FD7-4EF7-998E-43AF5F83A588'
ROOT=Path('/Users/antonioperedo/Desktop/badges/emerald_trophy_20261025/candidate07')
AXE='/Users/antonioperedo/.npm/_npx/99336612077b7094/node_modules/xcodebuildmcp/bundled/axe'
def swipe(start,end,duration=1.5):
 subprocess.run([AXE,'swipe','--start-x','200','--start-y',str(start),'--end-x','200','--end-y',str(end),'--duration',str(duration),'--udid',SIM],check=True,capture_output=True)
def capture(label):
 time.sleep(.8);subprocess.run(['xcrun','simctl','io',SIM,'screenshot',str(ROOT/('app_'+label+'.png'))],check=True,capture_output=True)
for label,distance in [('side_left',94),('back',133),('side_right',171)]:
 swipe(250,750,2);swipe(600,600-distance,2);capture(label);print(label+' captured',flush=True)
swipe(250,750,2);capture('front');print('Front restored',flush=True)
