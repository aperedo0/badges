"""Perform one slow full turn on the dedicated preview screen."""
import subprocess,time
AXE='/Users/antonioperedo/.npm/_npx/99336612077b7094/node_modules/xcodebuildmcp/bundled/axe'
UDID='DF439C70-9FD7-4EF7-998E-43AF5F83A588'
def swipe(a,b,d):subprocess.run([AXE,'swipe','--start-x','200','--start-y',str(a),'--end-x','200','--end-y',str(b),'--duration',str(d),'--udid',UDID],check=True,capture_output=True)
swipe(250,750,2);time.sleep(.5);swipe(600,360,6);time.sleep(.5)
