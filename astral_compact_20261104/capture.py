"""Capture native comparison poses for this daytime optimization."""
from pathlib import Path
import sys,subprocess,time,json,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent;mode=sys.argv[1]
assert mode in ['baseline','candidate01']
V=ROOT/'baseline' if mode=='baseline' else ROOT/'candidate01/review'
MODEL=ROOT/'baseline/astral_navigator_badge_mobile.usdz' if mode=='baseline' else ROOT/'candidate01/mobile/astral_navigator_badge_mobile.usdz'
A='/Users/antonioperedo/.npm/_npx/99336612077b7094/node_modules/xcodebuildmcp/bundled/axe';U='C18E609E-6C2F-49C4-BCFE-E5D365F4E4E8'
def swipe(a,b):subprocess.run([A,'swipe','--start-x','200','--start-y',str(a),'--end-x','200','--end-y',str(b),'--duration','2','--delta','2','--udid',U],check=True,capture_output=True)
def shot(name):
 p=V/(name+'.png');p.unlink(missing_ok=True);subprocess.run(['xcrun','simctl','io',U,'screenshot',str(p)],check=True,capture_output=True);return p
for attempt in range(20):
 p=shot('readiness');a=np.asarray(Image.open(p).convert('RGB'),float)/255
 if a[297:817,343:863].std(axis=(0,1)).max()>.025:break
 time.sleep(2)
else:raise RuntimeError('Native badge stage is not visible')
swipe(250,750);time.sleep(1);shot('front')
for pose,delta in [('early_turn',70),('side_left',94),('back',133),('side_right',171),('full_turn',209)]:
 swipe(600,600-delta);time.sleep(.5);shot(pose);swipe(250,750);time.sleep(.4)
data=Path(subprocess.check_output(['xcrun','simctl','get_app_container',U,'com.antonioperedo.badgestudio.preview','data'],text=True).strip())
assert (data/'tmp/Badge3DPreviewAstralNavigator.usdz').read_bytes()==MODEL.read_bytes()
(V/'loaded_model.json').write_text(json.dumps(dict(actual_model_verified=True,sha256=hashlib.sha256(MODEL.read_bytes()).hexdigest()),indent=2)+'\n')
print(mode,'native poses and loaded model verified')
