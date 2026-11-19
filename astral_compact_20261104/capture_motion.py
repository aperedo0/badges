"""Record a native slow turn and sample nearby gem angles."""
from pathlib import Path
import subprocess,time,signal,sys,io
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;C=ROOT/'candidate01';V=C/'review'
A='/Users/antonioperedo/.npm/_npx/99336612077b7094/node_modules/xcodebuildmcp/bundled/axe';U='C18E609E-6C2F-49C4-BCFE-E5D365F4E4E8'
def swipe(a,b,duration=2,delta=2):
 subprocess.run([A,'swipe','--start-x','200','--start-y',str(a),'--end-x','200','--end-y',str(b),'--duration',str(duration),'--delta',str(delta),'--udid',U],check=True,capture_output=True)
swipe(250,750);time.sleep(.5)
video=V/'full_turn.mp4';video.unlink(missing_ok=True)
recorder=subprocess.Popen(['xcrun','simctl','io',U,'recordVideo','--codec=h264',str(video)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
try:
 time.sleep(1.2);swipe(600,389,8,1);time.sleep(1)
finally:
 recorder.send_signal(signal.SIGINT);recorder.communicate(timeout=20);swipe(250,750)
sheet=Image.new('RGB',(1440,780),(16,17,20));draw=ImageDraw.Draw(sheet);frames=[]
for i,t in enumerate([1.1,2.5,3.,3.5,4.4,5.6,6.8,8.4]):
 data=subprocess.check_output(['/opt/homebrew/bin/ffmpeg','-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-f','image2pipe','-vcodec','png','-'])
 image=Image.open(io.BytesIO(data)).convert('RGB').crop((320,90,880,800));frames.append(image.tobytes())
 image.thumbnail((350,355));x=i%4*360;y=i//4*390;sheet.paste(image,(x,y+22));draw.text((x+8,y+5),str(t)+' seconds',fill='white')
assert len(set(frames))>=6,'Recorder repeated its frames'
sheet.save(V/'motion_review.png')
print('Recorded slow turn with distinct frames and returned badge to front.')
