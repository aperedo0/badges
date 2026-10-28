"""Save enlarged side finish comparisons using native app captures."""
from pathlib import Path
import sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
for key,previous in [('crescent_ocean','candidate04'),('mountain_crest','candidate01'),('winged_sword','candidate01')]:
 R=ROOT/key;C=R/(R/'candidate.txt').read_text().strip()
 comparison=Image.new('RGB',(2024,1634),(17,18,21));draw=ImageDraw.Draw(comparison)
 for i,candidate in enumerate([R/previous,C]):
  picture=Image.open(candidate/'app_side_left.png').convert('RGB').crop((480,165,730,565)).resize((1000,1600),Image.Resampling.NEAREST)
  comparison.paste(picture,(i*1012,34));draw.text((i*1012+8,10),'Previous side' if i==0 else 'Smooth side',fill='white')
 comparison.save(C/'side_finish_comparison.jpg',quality=97)
 contact=Image.new('RGB',(3300,1640),(17,18,21));draw=ImageDraw.Draw(contact)
 for i,(name,bbox) in enumerate([('side_left',(480,165,730,565)),('back',(400,150,800,480)),('side_right',(510,160,700,370))]):
  picture=Image.open(C/('app_'+name+'.png')).convert('RGB').crop(bbox);picture=picture.resize((picture.width*4,picture.height*4),Image.Resampling.NEAREST)
  contact.paste(picture,(i*1100,35));draw.text((i*1100+10,10),name.replace('_',' '),fill='white')
 contact.save(C/'outline_sides_4x.jpg',quality=97)
