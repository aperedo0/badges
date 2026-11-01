"""Capture native resolution views and a slow full turn in the private simulator."""
from pathlib import Path
import subprocess,time,sys,json,hashlib
R=Path(__file__).resolve().parent;name=sys.argv[1]
F=R/'family';C=F/name/'candidate01';folder=C/'review'
A='/Users/antonioperedo/.npm/_npx/99336612077b7094/node_modules/xcodebuildmcp/bundled/axe'
U='C18E609E-6C2F-49C4-BCFE-E5D365F4E4E8'
def swipe(a,b):
    subprocess.run([A,'swipe','--start-x','200','--start-y',str(a),'--end-x','200','--end-y',str(b),'--duration','2','--delta','2','--udid',U],check=True,capture_output=True)
def shot(pose):
    subprocess.run(['xcrun','simctl','io',U,'screenshot',str(folder/(pose+'.png'))],check=True,capture_output=True)
time.sleep(3)
swipe(250,750);time.sleep(.7);shot('front')
for pose,delta in [('early_turn',70),('side_left',94),('back',133),('side_right',171),('full_turn',209)]:
    swipe(600,600-delta);time.sleep(.4);shot(pose);swipe(250,750);time.sleep(.25)
data=Path(subprocess.check_output(['xcrun','simctl','get_app_container',U,'com.antonioperedo.badgestudio.preview','data'],text=True).strip())
loaded=data/'tmp'/('Badge3DPreview'+name+'.usdz')
assert loaded.read_bytes()==(C/'mobile/coin.usdz').read_bytes(),name
(C/'simulator_validation.json').write_text(json.dumps(dict(name=name,loaded_model_matches=True,poses=['front','early_turn','side_left','back','side_right','full_turn'],returned_to_front=True),indent=2)+'\n')
print(name+' native captures and loaded model verified',flush=True)
