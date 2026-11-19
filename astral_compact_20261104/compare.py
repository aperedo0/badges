"""Make native before and after evidence at equal size."""
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;V=ROOT/'candidate01/review';metrics={}
sheet=Image.new('RGB',(1320,960),(16,17,20));draw=ImageDraw.Draw(sheet)
for i,pose in enumerate(['front','early_turn','side_left','back','side_right','full_turn']):
 before=Image.open(ROOT/'baseline'/(pose+'.png')).convert('RGB');after=Image.open(V/(pose+'.png')).convert('RGB')
 box=(343,297,863,817) if pose=='front' else (340,100,860,660)
 b=before.crop(box);a=after.crop(box);difference=abs(np.asarray(a,float)-np.asarray(b,float))
 metrics[pose]=dict(mean_absolute_channel_difference=float(difference.mean()),maximum_channel_difference=int(difference.max()),fraction_pixels_with_channel_difference_over_3=float((difference.max(2)>3).mean()))
 pair=Image.new('RGB',(1040,600 if pose!='front' else 560),(16,17,20));pd=ImageDraw.Draw(pair)
 pair.paste(b,(0,40));pair.paste(a,(520,40));pd.text((12,14),'Before: 352 meshes',fill='white');pd.text((532,14),'After: 23 meshes',fill='white');pair.save(V/('comparison_'+pose+'.png'))
 pair.resize((pair.width*4,pair.height*4),Image.Resampling.NEAREST).save(V/('outline_pair_'+pose+'_4x.png'))
 a.resize((a.width*4,a.height*4),Image.Resampling.NEAREST).save(V/('outline_'+pose+'_4x.png'))
 small=pair.copy();small.thumbnail((650,300));x=i%2*660;y=i//2*320;sheet.paste(small,(x,y+20));draw.text((x+12,y+4),pose.replace('_',' '),fill='white')
sheet.save(V/'all_sides_comparison.png');(V/'native_pixel_comparison.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps(metrics,indent=2))
