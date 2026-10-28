"""Put the reference and actual Home badge at equal visible diameters."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent;TEMP=Path('/tmp/emerald_archer_20261023')
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
font=ImageFont.truetype(FONT,25)
ref=Image.open(ROOT/'reference.png').convert('RGB').crop((7,-54,1247,1186)).resize((520,520),Image.Resampling.LANCZOS)
def crop(file):return Image.open(file).convert('RGB').crop((343,297,863,817))
def pair(left,right,labels,path):
    out=Image.new('RGB',(1080,592),(16,17,18));d=ImageDraw.Draw(out)
    for x,im,label in zip([10,550],[left,right],labels):
        out.paste(im,(x,53));d.text((x+12,15),label,font=font,fill=(239,239,235))
    out.save(path,quality=94)
for name in ['candidate01','candidate02']:
    front=ROOT/name/'app_front.png'
    if front.exists():pair(ref,crop(front),['Reference','In the app'],ROOT/name/'comparison.jpg')
if (ROOT/'candidate02/app_front.png').exists():
    pair(ref,crop(ROOT/'candidate02/app_front.png'),['Reference','In the app'],ROOT/'comparison.jpg')
    pair(crop(ROOT/'candidate01/app_front.png'),crop(ROOT/'candidate02/app_front.png'),['First finish','Final finish'],ROOT/'finish_options.jpg')
    Image.open(ROOT/'candidate02/app_front.png').crop((295,240,915,980)).save(ROOT/'app_detail.png')
    Image.open(ROOT/'candidate02/app_front.png').crop((369,324,837,790)).resize((1872,1864),Image.Resampling.NEAREST).save(ROOT/'candidate02/outline_front_4x.png')
print('Same diameter comparisons saved')
