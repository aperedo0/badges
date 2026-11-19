"""Native captures use full resolution for exact outline comparisons."""
from pathlib import Path
import sys,subprocess,time,json,hashlib,signal,io
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;slug,mode=sys.argv[1:3];row=next(r for r in json.loads((ROOT/'gallery.json').read_text()) if r['slug']==slug)
V=ROOT/slug/('baseline' if mode=='baseline' else mode+'/review');V.mkdir(parents=True,exist_ok=True)
MODEL=ROOT/slug/('baseline/model.usdz' if mode=='baseline' else mode+'/model.usdz')
A='/Users/antonioperedo/.npm/_npx/99336612077b7094/node_modules/xcodebuildmcp/bundled/axe';U='C18E609E-6C2F-49C4-BCFE-E5D365F4E4E8'
def swipe(a,b,duration=1,delta=2):subprocess.run([A,'swipe','--start-x','200','--start-y',str(a),'--end-x','200','--end-y',str(b),'--duration',str(duration),'--delta',str(delta),'--udid',U],check=True,capture_output=True)
def shot(name):
 p=V/(name+'.png');p.unlink(missing_ok=True);subprocess.run(['xcrun','simctl','io',U,'screenshot',str(p)],check=True,capture_output=True);return p
swipe(250,750);time.sleep(.6)
for attempt in range(20):
 p=shot('readiness');a=np.asarray(Image.open(p).convert('RGB'),float)/255
 if a[297:817,343:863].std(axis=(0,1)).max()>.025:break
 time.sleep(2)
else:raise RuntimeError('Badge stage is not visible')
def header_y(path):
 a=np.asarray(Image.open(path).convert('RGB')).astype(int);r,g,b=a[500:1700,950:1150].transpose(2,0,1);counts=((b-r>40)&(b-g>20)&(b>120)&(r>50)&(g>80)).sum(1);ys=np.where(counts>8)[0]
 assert len(ys)>8,'Badge picker label is not visible'
 return float(np.median(ys)+500)
reference_mode=sys.argv[3] if len(sys.argv)>3 else ('baseline' if mode!='baseline' else None)
if reference_mode=='independent':reference_mode=None
reference_dir=ROOT/slug/('baseline' if reference_mode=='baseline' else mode+'/review') if reference_mode else None
poses=[('front',0),('early_turn',68),('side_left',94.2528),('back',132.5056),('side_right',170.7583),('full_turn',200)];pose_checks={};front_header=header_y(V/'readiness.png')
for pose,delta in poses:
 swipe(250,750);time.sleep(.5)
 if delta:swipe(600,600-delta-10);time.sleep(.5)
 p=shot(pose)
 if pose=='front':pose_checks['front']=dict(actual_header_y=header_y(p),reference_header_y=header_y(reference_dir/'front.png') if reference_dir else header_y(p))
 if delta:
  target=header_y(reference_dir/(pose+'.png')) if reference_dir is not None else front_header-delta*3;history=[]
  for retry in range(8):
   actual=header_y(p);history.append(actual)
   if abs(actual-target)<=1.5:break
   correction=(actual-target)/3
   correction+=10 if correction>0 else -10
   swipe(600,600-correction,duration=1,delta=1);time.sleep(.7);p=shot(pose)
  else:raise RuntimeError(('Could not match actual scroll pose',pose,target,history))
  pose_checks[pose]=dict(target_header_y=target,actual_header_y=actual,history=history)
swipe(250,750);time.sleep(.5)
(V/'pose_alignment.json').write_text(json.dumps(pose_checks,indent=2)+'\n')
data=Path(subprocess.check_output(['xcrun','simctl','get_app_container',U,'com.antonioperedo.badgestudio.preview','data'],text=True).strip());loaded=data/'tmp'/(row['dataset']+('Baseline' if mode=='baseline' else '')+'.usdz')
assert loaded.read_bytes()==MODEL.read_bytes(),('Wrong cached model',str(loaded))
(V/'loaded_model.json').write_text(json.dumps(dict(actual_model_verified=True,capture_version=3,sha256=hashlib.sha256(MODEL.read_bytes()).hexdigest()),indent=2)+'\n')
print(slug,mode,'all six measured poses and cached model verified',flush=True)
