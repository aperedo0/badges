"""Capture a native front frame after restoring the preview to its top pose."""
from pathlib import Path
import sys,subprocess,time,os
ROOT=Path(__file__).resolve().parent;R=ROOT/sys.argv[1];C=R/(R/'candidate.txt').read_text().strip();name=sys.argv[2] if len(sys.argv)>2 else 'app_calibration'
AXE='/Users/antonioperedo/.npm/_npx/99336612077b7094/node_modules/xcodebuildmcp/bundled/axe';UDID='DF439C70-9FD7-4EF7-998E-43AF5F83A588'
subprocess.run([AXE,'swipe','--start-x','200','--start-y','250','--end-x','200','--end-y','750','--duration','2','--udid',UDID],check=True,capture_output=True);time.sleep(2)
temporary=Path('/tmp')/('metal_front_'+str(os.getpid())+'.png')
subprocess.run(['xcrun','simctl','io',UDID,'screenshot',str(temporary)],check=True,capture_output=True)
(C/(name+'.png')).write_bytes(temporary.read_bytes());temporary.unlink();print(C/(name+'.png'))
