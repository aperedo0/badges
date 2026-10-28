"""Make equal scale owner reference and native simulator comparisons."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;key=sys.argv[1];R=ROOT/key;C=R/((R/'candidate.txt').read_text().strip() if (R/'candidate.txt').exists() else 'candidate01')
trace=json.loads((C/'trace.json').read_text());ref=Image.open(R/'reference.png').convert('RGB');app=Image.open(C/'app_front.png').convert('RGB')
# Align the original reference to the actual projected model bounds, keeping
# one uniform scale. The reference is never distorted to hide shape differences.
data=np.load(C/'geometry.npz');p=data['points'];p=p[p[:,2]>0]
camera=np.array([0,1.8,23.]);forward=np.array([0,-.55,0])-camera;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,1,0]);up=np.cross(right,forward)
delta=p-camera;depth=delta@forward
projected=np.c_[540+2250*(delta@right)/depth,720-2250*(delta@up)/depth]*47/60+[180,70]
target_lo=projected.min(0)-[343,297];target_hi=projected.max(0)-[343,297];center=(target_lo+target_hi)/2
lo,hi=np.array(trace['reference_bounds']);source_center=(lo+hi)/2;scale=(target_hi[1]-target_lo[1])/(hi[1]-lo[1])
source=ref.transform((520,520),Image.Transform.AFFINE,(1/scale,0,source_center[0]-center[0]/scale,0,1/scale,source_center[1]-center[1]/scale),resample=Image.Resampling.BICUBIC)
screen=app.crop((343,297,863,817))
canvas=Image.new('RGB',(1064,568),(17,18,21));canvas.paste(source,(8,40));canvas.paste(screen,(536,40));draw=ImageDraw.Draw(canvas)
draw.text((16,15),'Owner reference',fill='white');draw.text((544,15),'Simulator',fill='white');canvas.save(C/'comparison.jpg',quality=95)
screen.resize((2080,2080),Image.Resampling.NEAREST).save(C/'outline_front_4x.png')
source.resize((2080,2080),Image.Resampling.NEAREST).save(C/'reference_4x.png')
poses=[]
for name in ['front','side_left','back','side_right']:
 top=260 if name=='front' else 100
 im=Image.open(C/('app_'+name+'.png')).convert('RGB').crop((290,top,920,top+740)).resize((315,370),Image.Resampling.LANCZOS);poses.append((name,im))
 if name!='front':
  Image.open(C/('app_'+name+'.png')).convert('RGB').crop((340,160,860,650)).resize((2080,1960),Image.Resampling.NEAREST).save(C/('outline_'+name+'_4x.png'))
contact=Image.new('RGB',(1284,410),(17,18,21));draw=ImageDraw.Draw(contact)
for i,(name,im) in enumerate(poses):contact.paste(im,(6+i*320,34));draw.text((10+i*320,12),name.replace('_',' '),fill='white')
contact.save(C/'every_side.jpg',quality=94)
print(C/'comparison.jpg')
