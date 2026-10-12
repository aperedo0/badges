from pathlib import Path
import sys
import json,subprocess,numpy as np,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];manifest=json.loads((ROOT/'manifest.json').read_text());selection=json.loads((ROOT/(sys.argv[sys.argv.index('--selection')+1] if '--selection' in sys.argv else 'selection.json')).read_text())
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',24)
small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
for tier,num in selection.items():
 w=Path(manifest[tier]['work']);out=w/'candidates'/num;review=out/'review';review.mkdir(exist_ok=True)
 poses=['front','right','back','left'];sheet=Image.new('RGB',(4*606,2*900+70),'#101419');draw=ImageDraw.Draw(sheet)
 for j,folder in enumerate([w/'current',out]):
  for i,pose in enumerate(poses):
   path=folder/(pose+'.png')
   if not path.exists():continue
   im=Image.open(path);crop=im.crop((300,100,906,1000));sheet.paste(crop,(i*606,j*900+70))
   draw.text((i*606+18,j*900+75),('CURRENT' if j==0 else 'UPDATED')+' '+pose.upper(),font=small,fill='#d7dee7')
   # Include the full hero region at 4x nearest-neighbor for actual pixel inspection.
   if j==1:
    region=im.crop((330,130,876,900));region.resize((region.width*4,region.height*4),Image.Resampling.NEAREST).save(review/(pose+'_4x.png'))
 draw.text((24,20),tier.upper()+': ACTUAL HOME SCROLL POSES',font=font,fill='white');sheet.save(review/'scroll_comparison.png')
 video=out/'full_turn.mp4'
 if not video.exists():continue
 movie_sha=hashlib.sha256(video.read_bytes()).hexdigest();marker=review/'turn_review_generated.json'
 if marker.exists() and json.loads(marker.read_text()).get('movie_sha256')==movie_sha:continue
 frames=review/'turn_frames';frames.mkdir(exist_ok=True)
 command=['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','error','-i',str(video),'-vf','fps=12','-y',str(frames/'%03d.png')]
 subprocess.run(command,check=True)
 images=sorted(frames.glob('*.png'))
 for k in range(0,len(images),12):
  # Every sampled pose remains at exactly four times native pixel scale.
  panel=Image.new('RGB',(4*720,3*960),'#101419');pd=ImageDraw.Draw(panel)
  for i,p in enumerate(images[k:k+12]):
   im=Image.open(p).crop((300,110,906,810));im.thumbnail((606,700))
   # Preserve native samples in tiles; full 4x frames are saved separately.
   im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(review/(p.stem+'_turn_4x.png'))
   display=im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST);display.thumbnail((720,910));x=(i%4)*720;y=(i//4)*960;panel.paste(display,(x,y+30));pd.text((x+10,y+6),'frame '+p.stem,font=small,fill='white')
  panel.save(review/('turn_sheet_'+str(k//12+1)+'.png'))
 print(tier,'review poses ready; video samples',len(images))
 marker.write_text(json.dumps({'movie_sha256':movie_sha,'samples_per_second':12,'samples':len(images),'native_size':[1206,2622],'full_4x_frames_generated':True},indent=2)+'\n')
