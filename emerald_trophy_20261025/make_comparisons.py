"""Compare the reference with actual Home captures at equal coin diameters."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',25)
reference=Image.open(ROOT/'reference.png').convert('RGB').crop((-23,-60,1277,1240)).resize((520,520),Image.Resampling.LANCZOS)
def crop(path):return Image.open(path).convert('RGB').crop((343,297,863,817))
def pair(a,b,labels,file):
    out=Image.new('RGB',(1080,592),(16,17,18));d=ImageDraw.Draw(out)
    for x,im,label in zip([10,550],[a,b],labels):
        out.paste(im,(x,53));d.text((x+12,15),label,font=font,fill=(240,240,235))
    out.save(file,quality=95)
for name in ['candidate01','candidate02','candidate03']:
    p=ROOT/name/'app_front.png'
    if p.exists():pair(reference,crop(p),['Reference','In the app'],ROOT/name/'comparison.jpg')
final=ROOT/'candidate03/app_front.png'
if final.exists():
    pair(reference,crop(final),['Reference','In the app'],ROOT/'comparison.jpg')
    pair(crop(ROOT/'candidate01/app_front.png'),crop(final),['First pass','Refined ribbon and emeralds'],ROOT/'refinement.jpg')
    pair(crop(ROOT/'candidate02/app_front.png'),crop(final),['Softer green field','Deeper emerald field'],ROOT/'field_options.jpg')
    crop(final).save(ROOT/'app_detail.png')
print('Reference comparisons saved')
