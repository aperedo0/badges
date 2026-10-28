"""Compare native app captures with the reference and inspect every outline."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;C=R/'candidate04'
F=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',25)
def app(n):return Image.open(R/n/'app_front.png').convert('RGB').crop((343,297,863,817))
ref=Image.open(R/'reference.png').convert('RGB').crop((-23,-60,1277,1240)).resize((520,520),Image.Resampling.LANCZOS)
def row(images,labels,path):
 out=Image.new('RGB',(540*len(images),592),(16,17,18));d=ImageDraw.Draw(out)
 for i,(im,label) in enumerate(zip(images,labels)):
  out.paste(im,(i*540+10,53));d.text((i*540+20,15),label,font=F,fill='white')
 out.save(path,quality=95)
row([ref,app('candidate04')],['Reference','Revised in the app'],C/'comparison.jpg')
row([app('candidate03'),app('candidate04')],['Previous','Revised'],C/'before_after.jpg')
row([ref,app('candidate03'),app('candidate04')],['Reference','Previous','Revised'],C/'refinement.jpg')
app('candidate04').save(C/'app_detail.png')
# These crops contain every outer point and long edge at each app pose.
for pose,box in [('front',(366,321,840,795)),('side_left',(380,90,840,650)),('back',(380,90,840,600)),('side_right',(380,65,840,550))]:
 im=Image.open(C/('app_'+pose+'.png')).crop(box)
 im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(C/('outline_'+pose+'_4x.png'))
# Preserve larger carving details for the visual review.
im=Image.open(C/'app_front.png')
im.crop((422,410,784,748)).resize((1086,1014),Image.Resampling.NEAREST).save(C/'carving_3x.png')
print('Reference comparison, previous comparison, all outlines, and carving review saved')
