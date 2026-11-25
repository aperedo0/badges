from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import sys
r=Path(__file__).resolve().parents[1]
c=r/sys.argv[1]
ref=Image.open(Path.home()/'Downloads/Faceted ruby hourglass with side rails.png').convert('RGBA')
hero=Image.open(c/'studio_front.png').convert('RGBA')
bx=hero.getchannel('A').getbbox()
app=Image.open(c/'app/front.png').convert('RGB')
bg=(23,22,25);w,h=520,720
sheet=Image.new('RGB',(w*3+4,h),bg)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',21)
for i,(label,im,cx,top,bottom) in enumerate([
    ('Reference',ref,558,87,1332),
    ('Blender render',hero,(bx[0]+bx[2])/2,bx[1],bx[3]),
    ('iPhone preview',app,603,359,779)]):
    scale=604/(bottom-top)
    half_width=w/(2*scale)
    # Same apparent object size and centered position in all three panels.
    crop=im.crop((round(cx-half_width),round(top-31/scale),round(cx+half_width),round(top+635/scale)))
    crop=crop.resize((w,666),Image.Resampling.LANCZOS)
    sheet.paste(crop,(i*(w+2),54),crop if crop.mode=='RGBA' else None)
    draw=ImageDraw.Draw(sheet)
    draw.text((i*(w+2)+24,18),label,font=font,fill=(232,228,224))
    if i:draw.line((i*(w+2)-1,0,i*(w+2)-1,h),fill=(59,55,56),width=1)
hero=hero.crop(bx)
sheet.save(r/'Ruby Hourglass Comparison.png',optimize=True)
bgim=Image.new('RGB',(780,900),bg)
hero.thumbnail((694,790),Image.Resampling.LANCZOS)
bgim.paste(hero,((780-hero.width)//2,(900-hero.height)//2),hero)
bgim.save(r/'Ruby Hourglass.png',optimize=True)
