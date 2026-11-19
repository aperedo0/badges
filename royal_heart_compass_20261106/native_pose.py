"""Wait for the actual badge screen to settle before measuring a pose."""
from pathlib import Path
import subprocess,time
import numpy as np
from PIL import Image
UDID='C18E609E-6C2F-49C4-BCFE-E5D365F4E4E8'
AXE='/Users/antonioperedo/.npm/_npx/99336612077b7094/node_modules/xcodebuildmcp/bundled/axe'
def header_y(path):
 a=np.asarray(Image.open(path).convert('RGB')).astype(int);r,g,b=a[500:2100,950:1150].transpose(2,0,1);counts=((b-r>40)&(b-g>20)&(b>120)&(r>50)&(g>80)).sum(1);ys=np.where(counts>8)[0]
 if len(ys)<=8:raise ValueError('Badge picker is not visible yet')
 return float(np.median(ys)+500)
def shot(path):
 path=Path(path);path.unlink(missing_ok=True);subprocess.run(['xcrun','simctl','io',UDID,'screenshot',str(path)],check=True,capture_output=True);return path
def stable_shot(path):
 time.sleep(1.0);previous=None;stable=0
 for _ in range(16):
  shot(path)
  try:actual=header_y(path)
  except ValueError:previous=None;stable=0;time.sleep(.35);continue
  stable=stable+1 if previous is not None and abs(actual-previous)<=1 else 0
  if stable>=2:return Path(path)
  previous=actual;time.sleep(.30)
 raise RuntimeError('Badge screen did not settle after the gesture')
def reset(path):
 subprocess.run([AXE,'swipe','--start-x','200','--start-y','250','--end-x','200','--end-y','750','--duration','1','--delta','2','--udid',UDID],check=True,capture_output=True,timeout=20)
 return stable_shot(path)
if __name__=='__main__':
 import sys
 p=reset(sys.argv[1]);print('Resting screen settled, picker Y',header_y(p))
