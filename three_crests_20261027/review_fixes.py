"""Compare the two requested fixes at identical native app poses."""
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
canvas=Image.new('RGB',(1680,940),(17,18,21));draw=ImageDraw.Draw(canvas)
for row,(key,previous) in enumerate([('winged_sword','candidate04'),('crescent_ocean','candidate08')]):
 R=ROOT/key;C=R/(R/'candidate.txt').read_text().strip()
 for column,(folder,pose,title) in enumerate([(R/previous,'0','Before at rest'),(C,'0','After at rest'),(R/previous,'80','Before turning'),(C,'80','After turning')]):
  picture=Image.open(folder/('spin_'+pose+'.png')).convert('RGB').crop((315,245 if pose=='0' else 120,890,820 if pose=='0' else 695)).resize((410,410),Image.Resampling.LANCZOS)
  x=column*420+5;y=row*470+50
  canvas.paste(picture,(x,y));draw.text((x+8,y-26),key.replace('_',' ').title()+': '+title,fill='white')
canvas.save(ROOT/'sword_moon_fixes.jpg',quality=96)
R=ROOT/'crescent_ocean';C=R/(R/'candidate.txt').read_text().strip()
details=Image.new('RGB',(1080,810),(17,18,21));d=ImageDraw.Draw(details)
for col,folder in enumerate([R/'candidate08',C]):
 im=Image.open(folder/'spin_80.png').convert('RGB').crop((380,300,650,690)).resize((540,780),Image.Resampling.NEAREST)
 details.paste(im,(col*540,30));d.text((col*540+12,9),'Before' if col==0 else 'After',fill='white')
details.save(ROOT/'moon_surface_detail.jpg',quality=96)
