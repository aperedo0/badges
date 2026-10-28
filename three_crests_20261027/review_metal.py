"""Compare the approved front and actual moving reflections in native captures."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
baseline={'crescent_ocean':'candidate06','mountain_crest':'candidate02','winged_sword':'candidate02'}
fronts=Image.new('RGB',(1080,770),(17,18,21));draw=ImageDraw.Draw(fronts)
spins=Image.new('RGB',(1440,1140),(17,18,21));sd=ImageDraw.Draw(spins)
for row,(key,old) in enumerate(baseline.items()):
 R=ROOT/key;C=R/(R/'candidate.txt').read_text().strip();name=json.loads((R/'design.json').read_text())['name']
 for i,c in enumerate([R/old,C]):
  picture=Image.open(c/'app_front.png').convert('RGB').crop((343,297,863,817)).resize((344,344),Image.Resampling.LANCZOS);fronts.paste(picture,(row*360+8,54+i*370))
 draw.text((row*360+14,12),name,fill='white');draw.text((row*360+14,34),'Approved front',fill=(180,185,194));draw.text((row*360+14,404),'Reflective front',fill=(180,185,194))
 for column,angle in enumerate([0,64,80,104]):
  picture=Image.open(C/('spin_'+str(angle)+'.png')).convert('RGB').crop((280,130,920,810)).resize((352,344),Image.Resampling.LANCZOS)
  spins.paste(picture,(column*360+4,row*380+32));sd.text((column*360+10,row*380+10),name+(' front' if angle==0 else ' turning'),fill='white')
fronts.save(ROOT/'metal_front_comparison.jpg',quality=96);spins.save(ROOT/'metal_glints.jpg',quality=96)
