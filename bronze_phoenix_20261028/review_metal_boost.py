"""Show the requested bronze increase at identical native viewing poses."""
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;R=ROOT/'phoenix';C=R/(R/'candidate.txt').read_text().strip()
out=Image.new('RGB',(1040,1100),(17,18,21));draw=ImageDraw.Draw(out)
for row,pose in enumerate([0,80]):
 for column,folder in enumerate([R/'candidate03',C]):
  top=297 if pose==0 else 180
  image=Image.open(folder/('spin_'+str(pose)+'.png')).convert('RGB').crop((343,top,863,top+520))
  out.paste(image,(column*520,row*550+28))
  draw.text((column*520+10,row*550+9),('Before' if column==0 else 'Bronze reflections increased 15 percent')+(' at rest' if pose==0 else ' turning'),fill='white')
out.save(ROOT/'metal15_comparison.jpg',quality=96)
