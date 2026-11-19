from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;slug=sys.argv[1];base=ROOT/slug;v=base/'candidate16/review';stats={};sheet=Image.new('RGB',(1040,6*580),(16,17,20));draw=ImageDraw.Draw(sheet)
def registered(path,pose):
 im=Image.open(path).convert('RGB')
 if pose=='front':
  info=json.loads((v/'pose_alignment.json').read_text())['front'];offset=info['actual_header_y']-info['reference_header_y']
  if abs(offset)>.1:im=im.transform(im.size,Image.Transform.AFFINE,(1,0,0,0,1,offset),Image.Resampling.BICUBIC)
 return im
alignment=json.loads((v/'pose_alignment.json').read_text())
def bottom_of_stage(pose):
 if pose=='front':return 1030
 return 1030-(alignment['front']['reference_header_y']-alignment[pose]['actual_header_y'])
for i,pose in enumerate(['front','early_turn','side_left','back','side_right','full_turn']):
 box=(250,90,956,1030)
 a=Image.open(base/'baseline'/(pose+'.png')).convert('RGB').crop(box);b=registered(v/(pose+'.png'),pose).crop(box)
 pair=Image.new('RGB',(1412,940));pair.paste(a,(0,0));pair.paste(b,(706,0));pair.save(v/('comparison_'+pose+'.png'));pair.resize((5648,3760),Image.Resampling.NEAREST).save(v/('outline_pair_'+pose+'_4x.png'))
 pair.thumbnail((1040,550));sheet.paste(pair,(0,i*580+25));draw.text((10,i*580+6),pose+'    Before                                     After',fill='white')
 diff=np.abs(np.asarray(a).astype(float)-np.asarray(b).astype(float));yy,xx=np.mgrid[:diff.shape[0],:diff.shape[1]];ignore=((yy+90<255)&((xx+250<400)|(xx+250>850)))|(yy+90<180)|(yy+90>bottom_of_stage(pose));diff[ignore]=0;stats[pose]=dict(mean_absolute_pixel_difference=float(diff.mean()),max_difference=float(diff.max()),fraction_above_3=float((diff.max(2)>3).mean()))
sheet.save(v/'all_sides_comparison.png');(v/'pixel_comparison.json').write_text(json.dumps(stats,indent=2)+'\n');print(slug,stats['front'])
# Show the largest local rendering differences at four times native size.
from scipy.ndimage import maximum_filter
panel=Image.new('RGB',(1024,6*158),(18,18,22));d=ImageDraw.Draw(panel)
for i,pose in enumerate(['front','early_turn','side_left','back','side_right','full_turn']):
 a=Image.open(base/'baseline'/(pose+'.png')).convert('RGB').crop((250,90,956,1030));b=registered(v/(pose+'.png'),pose).crop((250,90,956,1030));diff=np.abs(np.asarray(a).astype(float)-np.asarray(b).astype(float)).max(2);yy,xx=np.mgrid[:diff.shape[0],:diff.shape[1]];ignore=((yy+90<255)&((xx+250<400)|(xx+250>850)))|(yy+90<180)|(yy+90>bottom_of_stage(pose));diff[ignore]=0;local=diff.copy()
 for j in range(4):
  yy,xx=np.unravel_index(local.argmax(),local.shape);box=(int(xx)-16,int(yy)-16,int(xx)+16,int(yy)+16);aa=a.crop(box).resize((128,128),Image.Resampling.NEAREST);bb=b.crop(box).resize((128,128),Image.Resampling.NEAREST);panel.paste(aa,(j*256,i*158+24));panel.paste(bb,(j*256+128,i*158+24));d.text((j*256+4,i*158+5),pose+' before    after',fill='white');local[max(0,yy-24):yy+25,max(0,xx-24):xx+25]=0
panel.save(v/'difference_details_4x.png')
