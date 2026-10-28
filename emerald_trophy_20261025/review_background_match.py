"""Compare native app captures with the reference and inspect every outline."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;C=R/'candidate07'
F=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',25)
def app(n):return Image.open(R/n/'app_front.png').convert('RGB').crop((343,297,863,817))
ref=Image.open(R/'reference.png').convert('RGB').crop((-23,-60,1277,1240)).resize((520,520),Image.Resampling.LANCZOS)
def row(images,labels,path):
 out=Image.new('RGB',(540*len(images),592),(16,17,18));d=ImageDraw.Draw(out)
 for i,(im,label) in enumerate(zip(images,labels)):
  out.paste(im,(i*540+10,53));d.text((i*540+20,15),label,font=F,fill='white')
 out.save(path,quality=95)
row([ref,app('candidate07')],['Reference','Revised in the app'],C/'comparison.jpg')
row([app('candidate06'),app('candidate07')],['Previous background','Arrow background'],C/'before_after.jpg')
row([ref,app('candidate06'),app('candidate07')],['Reference','Previous','Revised'],C/'refinement.jpg')
app('candidate07').save(C/'app_detail.png')
# Full native resolution outline review at each pose.
for pose,box in [('front',(366,321,840,795)),('side_left',(380,90,840,650)),('back',(380,90,840,600)),('side_right',(380,65,840,550))]:
 p=C/('app_'+pose+'.png')
 if not p.exists():continue
 im=Image.open(p).crop(box);im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(C/('outline_'+pose+'_4x.png'))
im=Image.open(C/'app_front.png');im.crop((422,392,784,748)).resize((1086,1068),Image.Resampling.NEAREST).save(C/'carving_3x.png')
