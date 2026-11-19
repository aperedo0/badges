from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json
D=Path(__file__).resolve().parent;C=D/'09_pitted_iron';R=D.parents[1]/'reference.png'
try:font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',22)
except OSError:font=ImageFont.load_default()
def row(items,name,size):
 out=Image.new('RGB',(size[0]*len(items),size[1]+52),'#202020');dr=ImageDraw.Draw(out)
 for i,(im,label) in enumerate(items):
  im=im if isinstance(im,Image.Image) else Image.open(im).convert('RGB');im=ImageOps.contain(im,size,Image.Resampling.LANCZOS);out.paste(im,(i*size[0]+(size[0]-im.width)//2,52+(size[1]-im.height)//2));dr.text((i*size[0]+14,15),label,fill='white',font=font)
 out.save(D/name,quality=98)
def rail(p):
 im=Image.open(p).convert('RGB');s=im.width/1200;return im.crop(tuple(round(v*s) for v in (295,215,960,466)))
left=C/'iron_final.png';right=C/'right_final.png';context=C/'context_final.png'
if left.exists():
 ref=Image.open(R).convert('RGB').crop((465,923,737,1019));row([(ref,'Original lower iron'),(rail(left),'Selected lower rim, original lighting')],'reference_comparison.jpg',(1000,440))
 old=D/'00_flat/iron_final.png'
 if old.exists():row([(rail(old),'Flat iron control, same lighting'),(rail(left),'Forged lower rim test')],'baseline_comparison.jpg',(1000,440))
 Image.open(left).convert('RGB').save(D/'iron_close.jpg',quality=99)
if left.exists() and right.exists():row([(left,'Left bay and approved wood'),(right,'Right bay and approved wood')],'close_views.jpg',(1100,550))
if context.exists():
 bounds=json.loads((C/'context_frame.json').read_text())['projected_chest_bounds']
 def normalize(im,b):
  scale=900/(b[2]-b[0]);im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS);out=Image.new('RGB',(1000,1000),'#151315');out.paste(im,(round(500-(b[0]+b[2])*.5*scale),round(65-b[1]*scale)));return out
 ref=normalize(Image.open(R).convert('RGB'),[68,176,1184,1080]);new=normalize(Image.open(context).convert('RGB'),bounds);row([(ref,'Original reference'),(new,'Only bottom rim developed; temporary context')],'chest_comparison.jpg',(1000,1000));Image.open(context).convert('RGB').save(D/'context.jpg',quality=98)
print('Updated available final comparisons')
