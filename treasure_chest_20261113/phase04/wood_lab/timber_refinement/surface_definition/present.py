from pathlib import Path
import json
from PIL import Image,ImageOps,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;W=D.parent;selection=json.loads((D/'selection.json').read_text());C=W/selection['selected'];light=selection['light']
try:font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',20)
except OSError:font=ImageFont.load_default()
def row(items,name,size=(900,666)):
 out=Image.new('RGB',(size[0]*len(items),size[1]+44),'#202020');dr=ImageDraw.Draw(out)
 for i,(value,label) in enumerate(items):
  im=value if isinstance(value,Image.Image) else Image.open(value).convert('RGB');im=ImageOps.contain(im,size,Image.Resampling.LANCZOS);out.paste(im,(i*size[0]+(size[0]-im.width)//2,44+(size[1]-im.height)//2));dr.text((i*size[0]+12,12),label,fill='white',font=font)
 out.save(D/name,quality=97)
def wood(path):
 im=Image.open(path).convert('RGB');s=im.width/1200;return im.crop(tuple(round(v*s) for v in (140,110,1040,550)))
close=C/('close_'+light+'_final.png');right=C/('right_'+light+'_final.png');plank=C/('plank_'+light+'_final.png');context=C/('context_'+light+'_final.png')
if close.exists():
 row([(wood(D/'close_balanced.png'),'Starting checkpoint, warm fill control'),(wood(close),'Selected result, final warm lighting')],'owner_before_after.jpg',(1000,500))
 row([(wood(W/'AI_core_definition/close_softwarm_final.png'),'Before organization, same light'),(wood(close),'Final organization, same light')],'controlled_organization.jpg',(1000,500))
 im=Image.open(close).convert('RGB');s=im.width/1200;im.crop(tuple(round(v*s) for v in (260,150,930,560))).save(D/'knot_native.jpg',quality=99)
if close.exists() and right.exists():row([(close,'Knot and left region'),(right,'Right region with actual hardware shadow')],'owner_close_views.jpg',(1100,814))
if plank.exists():
 row([(plank,'Whole existing test plank; surrounding parts unchanged')],'owner_plank.jpg',(1600,740))
context_view='context'
contact=C/('context_contact_'+light+'_final.png')
if contact.exists():context=contact;context_view='context_contact'
if context.exists():
 meta=json.loads((C/(context_view+'_'+light+'_frame.json')).read_text());bounds=meta['projected_chest_bounds'];ref=Image.open(D.parents[3]/'reference.png').convert('RGB');result=Image.open(context).convert('RGB')
 def normalize(im,box):
  scale=900/(box[2]-box[0]);im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS);out=Image.new('RGB',(1000,1000),'#151315');x=round(500-(box[0]+box[2])*.5*scale);y=round(70-box[1]*scale);out.paste(im,(x,y));return out,scale,(x,y)
 refn,rs,ro=normalize(ref,[68,176,1184,1080]);newn,ns,no=normalize(result,bounds)
 row([(refn,'Original reference'),(newn,'Temporary context; only test plank refined')],'owner_reference.jpg',(1000,1000))
 rc=(593*rs+ro[0],845*rs+ro[1]);kp=meta['projected_knot_center'];nc=(kp[0]*ns+no[0],kp[1]*ns+no[1])
 crops=[]
 for im,p in [(refn,rc),(newn,nc)]:crops.append(im.crop((round(p[0]-170),round(p[1]-130),round(p[0]+170),round(p[1]+130))).resize((1020,780),Image.Resampling.LANCZOS))
 row([(crops[0],'Reference crop at equal whole chest scale'),(crops[1],'Result crop at equal whole chest scale')],'equivalent_scale_knot.jpg',(1020,780))
print('Updated available owner comparisons',flush=True)
