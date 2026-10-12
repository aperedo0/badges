"""Extract continuous actual app frames, then inspect the moving interval."""
from pathlib import Path
import subprocess,sys,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
folder=Path(sys.argv[1]); frames=ROOT/'video_frames'/folder.parent.name/folder.name;frames.mkdir(parents=True,exist_ok=True)
subprocess.run(['/opt/homebrew/bin/ffmpeg','-y','-v','error','-i',str(folder/'full_turn.mp4'),'-t','30','-vf','fps=8',str(frames/'%04d.png')],check=True)
records=[]
for i,p in enumerate(sorted(frames.glob('*.png'))):
    im=Image.open(p).convert('RGB').resize((1206,2622),Image.Resampling.BILINEAR)
    a=np.array(im);roi=a[130:900,300:900].astype(float)
    blue=(roi[:,:,2]>40)&(roi[:,:,2]>roi[:,:,0]*1.12)&(roi[:,:,2]>roi[:,:,1]*1.005)
    centerRows=np.nonzero(blue[:,250:355].sum(1)>2)[0]
    if len(centerRows):
        blue[centerRows[0]+450:,:]=False
        yy,xx=np.nonzero(blue);width=int(xx.max()-xx.min()+1) if len(xx)>3 else 0
    else: width=0
    records.append({'path':str(p),'time':i/8,'width':width})
# The later UI labels can widen the crude blue mask. Calibrate only the
# resting opening, then use this as a capture proxy, never as an angle measure.
opening=[r['width'] for r in records[:16] if r['width']>100]
full=float(np.median(opening)) if opening else max(r['width'] for r in records)
moving=[x for x in records if 4<x['width']<full*.975]
if not moving: raise RuntimeError('No turn recorded')
start=max(0,moving[0]['time']-1)
first_moving = moving[0]['time']
hidden = [r for r in records if r['time'] > first_moving and r['width'] < 5]
end = min(records[-1]['time'], hidden[0]['time'] + 1) if hidden else records[-1]['time']
complete = bool(hidden)
moving = [r for r in moving if r['time'] <= end]
facts={'initial_width':full,'last_width':records[-1]['width'],'moving_start_seconds':moving[0]['time'],'complete_to_hidden':complete,'frames_reviewed':len(records),'first_hidden_seconds':hidden[0]['time'] if hidden else None,'review_clip_seconds':end-start}
(folder/'video_evidence.json').write_text(json.dumps(facts,indent=2))
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',20)
indices=np.linspace(0,len(moving)-1,16).round().astype(int)
selected=[moving[i] for i in indices]
sheet=Image.new('RGB',(480*4,475*4),(15,18,20));draw=ImageDraw.Draw(sheet)
for i,r in enumerate(selected):
    image=Image.open(r['path']).resize((1206,2622)).crop((200,130,1006,840));image.thumbnail((480,430))
    x=i%4*480;y=i//4*475;sheet.paste(image,(x,y+35));draw.text((x+8,y+5),f"{r['time']:.2f}s",font=font,fill='white')
sheet.save(folder/'spin_sheet.png')
# Every original-size outline, at quarter-second intervals, in separate 4x files.
edge=ROOT/'outline_review'/folder.parent.name/folder.name;edge.mkdir(parents=True,exist_ok=True)
for i,r in enumerate(moving[::2]):
    image=Image.open(r['path']).resize((1206,2622)).crop((280,170,926,780));image.resize((image.width*4,image.height*4),Image.Resampling.NEAREST).save(edge/f'{i:03d}_{r["time"]:.2f}s.png')
subprocess.run(['/opt/homebrew/bin/ffmpeg','-y','-v','error','-ss',str(start),'-i',str(folder/'full_turn.mp4'),'-t',str(end-start),'-c','copy',str(folder/'slow_turn_review.mp4')],check=True)
print(folder.name,json.dumps(facts))
