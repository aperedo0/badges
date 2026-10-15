"""One compact owner comparison. Home crops receive no appearance edits."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent.parent
TEMP=Path('/tmp/achievement_coins_20261014')
items=[
 ('Water','water_match_20261014','clean','water_standard_refined'),
 ('Teal hourglass','hourglass_match_20261014','hourglass_teal','hourglass_teal_matched_final'),
 ('Gold hourglass','hourglass_match_20261014','hourglass_gold','hourglass_gold_matched_final'),
 ('Sunrise','botanical_match_20261014','sunrise','sunrise_matched_final'),
 ('Emerald sprout','botanical_match_20261014','sprout','sprout_matched_final')]
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf',20)
small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',17)
out=Image.new('RGB',(1560,820),'#101114');d=ImageDraw.Draw(out)
d.text((16,43),'REFERENCE',font=small,fill='#b6b8bd')
d.text((16,392),'HOME APP  /  raised rims, recessed faces',font=small,fill='#b6b8bd')
for i,(label,folder,name,shot) in enumerate(items):
 x=10+i*312;meta=json.loads((R/folder/name/'design.json').read_text());cx,cy,r=meta['circle'];pad=r*.065
 ref=Image.open(meta['reference']).convert('RGB').crop((round(cx-r-pad),round(cy-r-pad),round(cx+r+pad),round(cy+r+pad))).resize((300,300),Image.Resampling.LANCZOS)
 app=Image.open(TEMP/(shot+'.png')).convert('RGB').crop((368,363,840,963)).resize((300,381),Image.Resampling.LANCZOS)
 out.paste(ref,(x,65));out.paste(app,(x,420));d.text((x+150,17),label,font=font,fill='white',anchor='mm')
out.save('/Users/antonioperedo/Downloads/Coin badge previews.png')
