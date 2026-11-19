from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
R=Path(__file__).resolve().parents[1];C=R/'candidate03';A=C/'app'
poses=['front','early05','early10','early_turn','side_left','back','side_right'];W=350;H=613
canvas=Image.new('RGB',(len(poses)*W,H+30),'#eeeeee');d=ImageDraw.Draw(canvas)
for i,n in enumerate(poses):
 d.text((W*i+10,5),n,fill='black');canvas.paste(Image.open(A/(n+'.png')).convert('RGB').crop((300,0,900,1050)).resize((W,H)),(W*i,30))
canvas.save(C/'poses.png')
files=sorted(A.glob('motion_*.png'));selected=[files[i] for i in np.linspace(0,len(files)-1,min(12,len(files))).round().astype(int)];canvas=Image.new('RGB',(len(selected)*240,524),'#eeeeee')
for i,p in enumerate(selected):canvas.paste(Image.open(p).convert('RGB').resize((240,524)),(i*240,0))
canvas.save(C/'turn_strip.png')
# Keep nearby early frames large enough to inspect facet flashes and outline motion.
canvas=Image.new('RGB',(1800,650),'#eeeeee');d=ImageDraw.Draw(canvas)
for i,n in enumerate(['early05','early10','early_turn']):
 d.text((i*600+10,5),n,fill='black');canvas.paste(Image.open(A/(n+'.png')).convert('RGB').crop((300,150,900,770)),(i*600,30))
canvas.save(C/'early_turn_close.png')
print('Saved native pose and motion review pictures')
