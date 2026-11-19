from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;R=P.parents[1];out=P/'review';out.mkdir(exist_ok=True)
try:font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',21)
except OSError:font=ImageFont.load_default()
def row(items,wh):
 W,H=wh;im=Image.new('RGB',(W*len(items),H+42),'#191919');d=ImageDraw.Draw(im)
 for i,(p,label) in enumerate(items):
  q=ImageOps.contain(Image.open(p).convert('RGB'),wh);im.paste(q,(i*W+(W-q.width)//2,42+(H-q.height)//2));d.text((i*W+12,10),label,font=font,fill='white')
 return im
F=P/'final_renders'
for name in ['baseline_cinema_close','master_cinema_close']:
 Image.open(F/(name+'.png')).crop((200,100,1380,750)).save(out/(name+'_crop.png'))
# Build available rows immediately, and add diagnostics when their renders finish.
row([(R/'phase03/wood_sample44/reference_wood_close.png','Owner reference'),(out/'baseline_cinema_close_crop.png','Before: normal maps only'),(out/'master_cinema_close_crop.png','Current: real relief and fine normals')],(680,510)).save(out/'wood_review.jpg',quality=95)
row([(R/'reference.png','Owner reference'),(F/'master_cinema_full.png','Current test plank only'),(F/'master_context_full.png','Temporary color context only')],(680,680)).save(out/'whole_chest_review.jpg',quality=95)
if (F/'master_opposed_close.png').exists() and (F/'master_clay_graze.png').exists():
 row([(F/'master_neutral_close.png','Neutral studio'),(F/'master_clay_graze.png','Gray clay: actual geometry'),(F/'master_opposed_close.png','Opposite key light')],(680,510)).save(out/'relief_diagnostics.jpg',quality=95)
row([(F/'baseline_neutral_close.png','Baseline, identical neutral light'),(F/'master_neutral_close.png','Current, identical neutral light')],(800,592)).save(out/'neutral_before_after.jpg',quality=95)
