from pathlib import Path
import sys, subprocess, json
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
number=sys.argv[1]
out=ROOT/'candidates'/number
review=out/'review';review.mkdir(exist_ok=True)
old=Path('/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/diamond/all_sides_20261010/candidates/04')
poses=['front','right','back','left']
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',24)
sheet=Image.new('RGB',(2424,1470),'#101419');draw=ImageDraw.Draw(sheet)
for row,folder in enumerate([old,out]):
    for col,pose in enumerate(poses):
        im=Image.open(folder/(pose+'.png')).crop((300,110,906,810))
        sheet.paste(im,(col*606,70+row*700))
        draw.text((col*606+12,76+row*700),('PREVIOUS ROUND' if row==0 else 'UPDATED')+' '+pose.upper(),fill='white',font=font)
        if row:im.resize((2424,2800),Image.Resampling.NEAREST).save(review/(pose+'_4x.png'))
draw.text((20,18),'Diamond: actual Home turn, previous and revised material',fill='white',font=font)
sheet.save(review/'scroll_comparison.png')
frames=review/'turn_frames';frames.mkdir(exist_ok=True)
subprocess.run(['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','error','-i',str(out/'full_turn.mp4'),'-vf','fps=12,crop=606:700:300:110','-y',str(frames/'%03d.png')],check=True)
images=sorted(frames.glob('*.png'))
for k in range(0,len(images),12):
    panel=Image.new('RGB',(2424,2190),'#101419');pd=ImageDraw.Draw(panel)
    for j,path in enumerate(images[k:k+12]):
        im=Image.open(path)
        im.resize((2424,2800),Image.Resampling.NEAREST).save(review/(path.stem+'_turn_4x.png'))
        x=(j%4)*606;y=(j//4)*730
        panel.paste(im,(x,y+30));pd.text((x+12,y+3),'frame '+path.stem,fill='white',font=font)
    panel.save(review/('turn_sheet_'+str(k//12+1)+'.png'))
(review/'capture.json').write_text(json.dumps({'samples_per_second':12,'samples':len(images),'native_screen_size':[1206,2622],'zoom':4,'source':'actual Home scroll video, shader-warmed simulator'},indent=2)+'\n')
if all((ROOT/'inspection'/number/pose/'front.png').exists() for pose in poses[1:]):
    sheet=Image.new('RGB',(4*606,2*600+70),'#101419');draw=ImageDraw.Draw(sheet)
    for row in range(2):
        for col,pose in enumerate(poses):
            if pose=='front':path=(old if row==0 else out)/'front.png'
            elif row==0:path=Path('/Users/antonioperedo/Desktop/badges/all_sides_20261010/inspection_models/updated/diamond')/pose/'app.png'
            else:path=ROOT/'inspection'/number/pose/'front.png'
            im=Image.open(path).crop((300,250,906,850))
            sheet.paste(im,(col*606,70+row*600))
            draw.text((col*606+12,76+row*600),('PREVIOUS ROUND' if row==0 else 'UPDATED')+' '+pose.upper(),fill='white',font=font)
            if row:im.resize((2424,2400),Image.Resampling.NEAREST).save(review/(pose+'_fullsize_4x.png'))
    draw.text((20,18),'Diamond: equal-size views under the actual app lighting',fill='white',font=font)
    sheet.save(review/'fullsize_comparison.png')
print('Prepared',len(images),'full-turn samples and four pose comparisons.')
