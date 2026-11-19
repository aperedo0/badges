from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json
D=Path(__file__).resolve().parent;W=D.parent;A=W/'AW_depth_hierarchy';C=W/'BC_final_polish';R=D.parents[3]/'reference.png'
try:font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',22)
except OSError:font=ImageFont.load_default()
def sheet(items,name,size):
 out=Image.new('RGB',(size[0]*len(items),size[1]+50),'#202020');dr=ImageDraw.Draw(out)
 for i,(im,label) in enumerate(items):
  im=im if isinstance(im,Image.Image) else Image.open(im).convert('RGB');im=ImageOps.contain(im,size,Image.Resampling.LANCZOS);out.paste(im,(i*size[0]+(size[0]-im.width)//2,50+(size[1]-im.height)//2));dr.text((i*size[0]+14,14),label,fill='white',font=font)
 out.save(D/name,quality=98)
def crop(p):
 im=Image.open(p).convert('RGB');s=im.width/1200;return im.crop(tuple(round(v*s) for v in (140,110,1040,550)))
close=C/'close_softwarm_final.png';right=C/'right_softwarm_final.png';context=C/'context_contact_softwarm_final.png'
if close.exists():
 sheet([(crop(A/'close_softwarm_final.png'),'Starting AW checkpoint'),(crop(close),'Selected final polish, same lighting')],'baseline_final.jpg',(1000,490))
 im=Image.open(close).convert('RGB');im.crop((390,225,1395,840)).save(D/'knot_close.jpg',quality=99)
if close.exists() and right.exists():sheet([(close,'Knot and left bay'),(right,'Right bay, hardware shadow retained')],'close_views.jpg',(1100,814))
if (C/'plank_softwarm_final.png').exists():sheet([(C/'plank_softwarm_final.png','Complete existing test plank; surrounding parts preserved')],'whole_plank.jpg',(1600,740))
if right.exists():sheet([(crop(A/'right_softwarm_final.png'),'Starting right bay'),(crop(right),'Final right bay, same light')],'right_before_after.jpg',(1000,490))
if context.exists():
 meta=json.loads((C/'context_contact_softwarm_frame.json').read_text());bounds=meta['projected_chest_bounds'];ref=Image.open(R).convert('RGB');result=Image.open(context).convert('RGB')
 def normalize(im,box):
  scale=900/(box[2]-box[0]);im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS);out=Image.new('RGB',(1000,1000),'#151315');x=round(500-(box[0]+box[2])*.5*scale);y=round(70-box[1]*scale);out.paste(im,(x,y));return out,scale,(x,y)
 refn,rs,ro=normalize(ref,[68,176,1184,1080]);newn,ns,no=normalize(result,bounds)
 sheet([(refn,'Original reference'),(newn,'Final test plank with temporary context')],'reference_final.jpg',(1000,1000))
 rc=(593*rs+ro[0],845*rs+ro[1]);kp=meta['projected_knot_center'];nc=(kp[0]*ns+no[0],kp[1]*ns+no[1]);crops=[]
 for im,p in [(refn,rc),(newn,nc)]:crops.append(im.crop((round(p[0]-170),round(p[1]-130),round(p[0]+170),round(p[1]+130))).resize((1020,780),Image.Resampling.LANCZOS))
 sheet([(crops[0],'Reference, equal whole chest scale'),(crops[1],'Final, equal whole chest scale')],'reference_close.jpg',(1020,780))
print('Updated final comparisons')
