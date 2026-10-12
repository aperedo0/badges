"""Present actual Home captures at equal scale, including full outline crops."""
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont

OUT=Path('/Users/antonioperedo/Downloads/diamond_codex')
CROP=(280,300,926,860)
FONT=ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf",24)

def comparison(paths,labels,out,zoom=1,crop=CROP):
    pictures=[Image.open(p).convert('RGB').crop(crop) for p in paths]
    if zoom!=1:
        pictures=[p.resize((p.width*zoom,p.height*zoom),Image.Resampling.NEAREST) for p in pictures]
    width=sum(p.width for p in pictures)+20*(len(pictures)-1)
    result=Image.new('RGB',(width,pictures[0].height+45),(16,18,20))
    draw=ImageDraw.Draw(result);x=0
    for picture,label in zip(pictures,labels):
        result.paste(picture,(x,45));draw.text((x+10,10),label,font=FONT,fill='white');x+=picture.width+20
    out.parent.mkdir(parents=True,exist_ok=True);result.save(out)

def option(folder,label):
    folder=Path(folder)
    for zoom in [1,4]:
        comparison([OUT/'00_today/rest.png',folder/'rest.png'],['Today',label],folder/f'rest_comparison_{zoom}x.png',zoom)
    for pose in ['rest','right','back','left']:
        if not (folder/f'{pose}.png').exists():continue
        image=Image.open(folder/f'{pose}.png').crop(CROP if pose=='rest' else (200,90,1006,860))
        image.resize((image.width*4,image.height*4),Image.Resampling.NEAREST).save(folder/f'{pose}_outline_4x.png')
    if all((folder/f'{p}.png').exists() for p in ['right','back','left']):
        for pose in ['right','back','left']:
            comparison([OUT/f'00_today/{pose}.png',folder/f'{pose}.png'],['Today '+pose,label+' '+pose],folder/f'{pose}_comparison_1x.png',crop=(200,90,1006,860))

if __name__=='__main__':
    option(sys.argv[1],sys.argv[2])
