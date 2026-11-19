from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];C=R/'candidate01';A=C/'app'
im=Image.open(A/'front.png').convert('RGB');box=(385,350,825,805)
im.save(C/'finish_full_size.png');im.crop(box).resize((880,910),Image.Resampling.NEAREST).save(C/'finish_2x.png')
poses=['front','early_turn','side_left','back','side_right'];canvas=Image.new('RGB',(2000,730),'#eeeeee');draw=ImageDraw.Draw(canvas)
for i,name in enumerate(poses):
 draw.text((i*400+10,8),name,fill='black');q=Image.open(A/(name+'.png')).convert('RGB').crop((300,0,900,1050)).resize((400,700));canvas.paste(q,(i*400,30))
canvas.save(C/'poses.png')
files=sorted(A.glob('motion_*.png'));selected=files[::max(1,len(files)//10)][:10];canvas=Image.new('RGB',(len(selected)*240,524),'#eeeeee')
for i,p in enumerate(selected):canvas.paste(Image.open(p).convert('RGB').resize((240,524)),(i*240,0))
canvas.save(C/'turn_strip.png')
print('Review pictures saved')
