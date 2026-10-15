"""One compact owner picture from unretouched current Home crops."""
from pathlib import Path
import sys
from PIL import Image,ImageDraw,ImageFont

TEMP=Path('/tmp/coin_rims_20261014')
items=[('Water','clean'),('Teal hourglass','hourglass_teal'),('Gold hourglass','hourglass_gold'),('Sunrise','sunrise'),('Emerald sprout','sprout')]
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf',20)
small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',17)
out=Image.new('RGB',(1560,440),'#101114');draw=ImageDraw.Draw(out)
for i,(label,name) in enumerate(items):
    x=10+i*312
    crop=Image.open(TEMP/(name+'_rim.png')).convert('RGB').crop((368,363,840,963)).resize((300,381),Image.Resampling.LANCZOS)
    out.paste(crop,(x,37));draw.text((x+150,17),label,font=font,fill='white',anchor='mm')
draw.text((15,420),'Actual Home renders  /  brushed rims with real lighting',font=small,fill='#b6b8bd')
out.save(sys.argv[1] if len(sys.argv)>1 else '/Users/antonioperedo/Downloads/Coin badge previews.png')
