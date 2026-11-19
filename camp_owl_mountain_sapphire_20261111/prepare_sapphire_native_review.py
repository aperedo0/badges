"""Package actual native Sapphire captures and bounded turn frames for review."""
from pathlib import Path
from PIL import Image,ImageDraw
import sys,subprocess,shutil,json,hashlib
R=Path(__file__).resolve().parent;B=R/'sapphire_teardrop';C=B/sys.argv[1];O=C/'review';O.mkdir(exist_ok=True)
im=Image.open(C/'app/front.png').convert('RGB');im.save(O/'finish_full_size.png');crop=im.crop((410,330,800,810));crop.save(O/'front_badge.png');w,h=crop.size
for k,(x,y) in enumerate([(0,0),(w//2,0),(0,h//2),(w//2,h//2)],1):crop.crop((x,y,x+w//2,y+h//2)).resize((w,h),Image.Resampling.NEAREST).save(O/f'finish_2x_{k}.png')
crop.crop((105,20,270,160)).resize((660,560),Image.Resampling.NEAREST).save(O/'finish_4x.png');old=Image.open(B/'candidate22/app/front.png').convert('RGB').crop((410,330,800,810));canvas=Image.new('RGB',(780,505),(28,28,34));canvas.paste(old,(0,25));canvas.paste(crop,(390,25));d=ImageDraw.Draw(canvas);d.text((10,5),'BEFORE',fill='white');d.text((400,5),'CURRENT',fill='white');canvas.save(O/'before_after_native.png')
canvas=Image.new('RGB',(1500,500),(28,28,34));d=ImageDraw.Draw(canvas)
for k,p in enumerate(['front','early_turn','side_left','back','side_right']):
 im=Image.open(C/'app'/(p+'.png')).convert('RGB').crop((350,100,880,900));im.thumbnail((300,460),Image.Resampling.LANCZOS);canvas.paste(im,(k*300,30));d.text((k*300+10,5),p,fill='white')
canvas.save(O/'native_turn_strip.png');shutil.copy2(B/'candidate25/review/ruby_heart_gold_reference.jpg',O/'ruby_heart_gold_reference.jpg');video=C/'app/full_turn_bounded.mp4';assert video.exists()
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(video),'-vf','fps=2,crop=560:900:323:100,scale=224:360','-frames:v','22',str(O/'motion_%02d.png')],check=True)
files=sorted(O.glob('motion_??.png'));assert len(files)>=18;canvas=Image.new('RGB',(1120,1900),(28,28,34));d=ImageDraw.Draw(canvas);hashes=[]
for k,p in enumerate(files):
 im=Image.open(p).convert('RGB');hashes.append(hashlib.sha256(im.tobytes()).hexdigest());x=(k%5)*224;y=(k//5)*380;canvas.paste(im,(x,y+20));d.text((x+5,y+3),f'{(k+.5)*.5:.2f} sec',fill='white')
canvas.save(O/'motion_strip.png');(O/'motion_frame_validation.json').write_text(json.dumps(dict(actual_native_video_frames=True,frames=len(files),unique_frames=len(set(hashes)),full_turn_review_pending=True),indent=2)+'\n');s=(B/'candidate25/review/brief.md').read_text().replace('candidate25',sys.argv[1]);(O/'brief.md').write_text(s);print('Prepared actual native review:',O)
