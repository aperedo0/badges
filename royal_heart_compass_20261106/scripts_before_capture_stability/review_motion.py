"""Find true scroll poses inside native recordings, rather than assume timing."""
from pathlib import Path
import sys,subprocess,json,tempfile
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;key,mode=sys.argv[1:3];V=ROOT/key/('baseline' if mode=='baseline' else mode+'/review');video=V/'full_turn.mp4'
assert video.stat().st_mtime >= (V/'loaded_model.json').stat().st_mtime, 'Recording predates the verified model capture'
with tempfile.TemporaryDirectory(prefix='royal_motion_',dir='/tmp') as tmp:
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-i',str(video),'-vf','fps=6','-compression_level','1',str(Path(tmp)/'frame%04d.png')],check=True)
 records=[]
 for file in sorted(Path(tmp).glob('frame*.png')):
  a=np.asarray(Image.open(file).convert('RGB')).astype(int);r,g,b=a[500:1700,950:1150].transpose(2,0,1);counts=((b-r>40)&(b-g>20)&(b>120)&(r>50)&(g>80)).sum(1);ys=np.where(counts>8)[0]
  if len(ys)>8:records.append((file,float(np.median(ys)+500)))
 assert len(records)>10,'Insufficient native video frames'
 front=max(y for f,y in records);rows=[];sheet=Image.new('RGB',(1080,1740),(15,16,19));draw=ImageDraw.Draw(sheet);frames=[]
 for i,scroll in enumerate([0,60,68,80,94.2528,113,132.5056,151,170.7583]):
  target=front-scroll*3;file,actual=min(records,key=lambda item:abs(item[1]-target));im=Image.open(file).convert('RGB').crop((320,90,880,970));frames.append(im.tobytes());im.thumbnail((350,550));x=i%3*360;y=i//3*580;sheet.paste(im,(x,y+22));draw.text((x+8,y+4),str(round((front-actual)/3,1))+' points of scroll',fill='white');rows.append(dict(requested_scroll=scroll,actual_scroll=(front-actual)/3,video_frame=file.name))
 assert len(set(frames))>=8,'Recording repeated frames or missed the turn'
 max_scroll=(front-min(y for f,y in records))/3;assert max_scroll>209,'The full turn was not reached'
 sheet.save(V/'motion_review.png');(V/'motion_validation.json').write_text(json.dumps(dict(distinct_review_frames=len(set(frames)),maximum_actual_scroll=max_scroll,full_turn_reached=True,poses=rows),indent=2)+'\n')
 print(key,mode,'full native turn verified with',len(set(frames)),'distinct review frames')
