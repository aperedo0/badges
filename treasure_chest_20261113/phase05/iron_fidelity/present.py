from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,sys
D=Path(__file__).resolve().parent;key=sys.argv[1];C=D/key;R=D.parents[1]/'reference.png'
try:font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',21)
except OSError:font=ImageFont.load_default()
def sheet(items,name,cols,size):
 out=Image.new('RGB',(size[0]*cols,(size[1]+48)*((len(items)+cols-1)//cols)),'#202020');dr=ImageDraw.Draw(out)
 for i,(im,label) in enumerate(items):
  x=i%cols*size[0];y=i//cols*(size[1]+48);im=im if isinstance(im,Image.Image) else Image.open(im).convert('RGB');im=ImageOps.contain(im,size,Image.Resampling.LANCZOS);out.paste(im,(x+(size[0]-im.width)//2,y+48+(size[1]-im.height)//2));dr.text((x+12,y+12),label,fill='white',font=font)
 out.save(D/name,quality=97)
def rail(p):
 im=Image.open(p).convert('RGB');s=im.width/1200;return im.crop(tuple(round(v*s) for v in (295,215,960,466)))
ref=Image.open(R).convert('RGB').crop((465,923,737,1019));left=C/'iron_studio3_final.png';right=C/'right_studio3_final.png';context=C/'context_studio3_final.png'
sheet([(ref,'Original reference'),(rail(left),'Selected bottom iron, reflection study')],'reference_comparison.jpg',2,(900,360))
sheet([(rail(D/'baseline/iron_current_final.png'),'Starting iron, original lighting'),(rail(C/'iron_current_final.png'),'Selected iron, original lighting'),(rail(D/'baseline/iron_studio3_final.png'),'Starting iron, reflection study'),(rail(left),'Selected iron, same reflection study')],'baseline_comparison.jpg',2,(900,360))
sheet([(left,'Selected iron: left bay'),(right,'Selected iron: right bay')],'close_views.jpg',1,(1400,700))
bounds=json.loads((C/'context_frame.json').read_text())['projected_chest_bounds']
def normalize(im,b):
 scale=760/(b[2]-b[0]);im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS);out=Image.new('RGB',(850,850),'#151315');out.paste(im,(round(425-(b[0]+b[2])*.5*scale),round(65-b[1]*scale)));return out
sheet([(normalize(Image.open(R).convert('RGB'),[68,176,1184,1080]),'Original reference'),(normalize(Image.open(context).convert('RGB'),bounds),'Bottom iron test; other finishes temporary')],'chest_comparison.jpg',2,(850,850))
print('Created four review comparisons',key)
