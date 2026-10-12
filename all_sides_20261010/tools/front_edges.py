from pathlib import Path
import json,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];m=json.loads((ROOT/'manifest.json').read_text());s=json.loads((ROOT/(sys.argv[sys.argv.index('--selection')+1] if '--selection' in sys.argv else 'selection.json')).read_text());f=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
for t,n in s.items():
 o=Path(m[t]['work'])/'candidates'/n;review=o/'review';review.mkdir(exist_ok=True)
 if not (o/'front.png').exists():continue
 im=Image.open(o/'front.png').convert('RGB')
 patches=[(x,y) for y in range(250,1000,150) for x in range(300,1050,150)]
 for k in range(0,len(patches),4):
  sh=Image.new('RGB',(1200,1260),'#101419');d=ImageDraw.Draw(sh)
  for i,(x,y) in enumerate(patches[k:k+4]):
   xx=i%2*600;yy=i//2*630;sh.paste(im.crop((x,y,x+150,y+150)).resize((600,600),Image.Resampling.NEAREST),(xx,yy+30));d.text((xx+8,yy+3),t+' front '+str((x,y)),font=f,fill='white')
  sh.save(review/('updated_front_edges4x_'+str(k//4+1)+'.png'))
