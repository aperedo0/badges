"""Native captures use full resolution for exact outline comparisons."""
from pathlib import Path
import sys,subprocess,time,json,hashlib,signal,io
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;slug,mode=sys.argv[1:3];row=next(r for r in json.loads((ROOT/'manifest.json').read_text()) if r['slug']==slug)
V=ROOT/'badges'/slug/('baseline' if mode=='baseline' else 'candidate01/review');V.mkdir(parents=True,exist_ok=True)
MODEL=ROOT/'badges'/slug/('baseline/model.usdz' if mode=='baseline' else 'candidate01/model.usdz')
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
 a=np.asarray(Image.open(path).convert('RGB')).astype(int);r,g,b=a[500:1700,750:1150].transpose(2,0,1);counts=((b-r>40)&(b-g>20)&(b>120)&(r>50)&(g>80)).sum(1);ys=np.where(counts>8)[0]
 assert len(ys)>8,'Badge picker label is not visible'
 return float(np.median(ys)+500)
reference_mode=sys.argv[3] if len(sys.argv)>3 else ('baseline' if mode!='baseline' else None)
reference_dir=ROOT/'badges'/slug/('baseline' if reference_mode=='baseline' else 'candidate01/review') if reference_mode else None
poses=[('front',0),('early_turn',70),('side_left',94),('back',133),('side_right',171),('full_turn',209)];pose_checks={}
for pose,delta in poses:
 swipe(250,750);time.sleep(.5)
 if delta:swipe(600,600-delta);time.sleep(.5)
 p=shot(pose)
 if reference_dir is not None:
  target=header_y(reference_dir/(pose+'.png'));history=[]
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
data=Path(subprocess.check_output(['xcrun','simctl','get_app_container',U,'com.antonioperedo.badgestudio.preview','data'],text=True).strip());loaded=data/'tmp'/(row['dataset']+'.usdz')
assert loaded.read_bytes()==MODEL.read_bytes(),('Wrong cached model',str(loaded))
(V/'loaded_model.json').write_text(json.dumps(dict(actual_model_verified=True,capture_version=2,sha256=hashlib.sha256(MODEL.read_bytes()).hexdigest()),indent=2)+'\n')
if mode!='baseline':
 video=V/'full_turn.mp4';video.unlink(missing_ok=True);recorder=subprocess.Popen(['xcrun','simctl','io',U,'recordVideo','--codec=h264',str(video)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 try:time.sleep(1.2);swipe(600,367,8,1);time.sleep(.5)
 finally:recorder.send_signal(signal.SIGINT);recorder.communicate(timeout=20);swipe(250,750)
 sheet=Image.new('RGB',(1440,780),(16,17,20));draw=ImageDraw.Draw(sheet);frames=[]
 for i,t in enumerate([1.1,2.5,3.,3.5,4.4,5.6,6.8,8.4]):
  raw=subprocess.check_output(['/opt/homebrew/bin/ffmpeg','-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-f','image2pipe','-vcodec','png','-']);im=Image.open(io.BytesIO(raw)).convert('RGB').crop((320,90,880,800));frames.append(im.tobytes());im.thumbnail((350,355));x=i%4*360;y=i//4*390;sheet.paste(im,(x,y+22));draw.text((x+8,y+5),str(t)+' seconds',fill='white')
 assert len(set(frames))>=6,'Recorder repeated frames'
 sheet.save(V/'motion_review.png')
print(slug,mode,'all six poses verified',flush=True)
