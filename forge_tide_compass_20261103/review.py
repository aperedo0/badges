"""Equal scale comparison and nearest neighbor outline views from native captures."""
from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;R=ROOT/sys.argv[1];C=R/(R/'candidate.txt').read_text().strip();V=C/'review';cfg=json.loads((R/'design.json').read_text())
D=np.load(C/'blender_geometry.npz');groups=json.loads((C/'groups.json').read_text());points=np.vstack([D[str(i)+'_points'] for i in range(len(groups))]);points=points[points[:,2]>=0]
camera=np.array([0,1.8,23.]);forward=np.array([0,-.55,0])-camera;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,1,0]);up=np.cross(right,forward)
delta=points-camera;depth=delta@forward;projected=np.c_[540+2250*(delta@right)/depth,720-2250*(delta@up)/depth]*47/60+[180,70]
target_lo=projected.min(0)-[343,297];target_hi=projected.max(0)-[343,297];center=(target_lo+target_hi)/2
lo=np.array(cfg['bounds'][:2]);hi=np.array(cfg['bounds'][2:]);source_center=(lo+hi)/2;scale=(target_hi[1]-target_lo[1])/(hi[1]-lo[1])
ref=Image.open(R/'reference.png').convert('RGB')
source=ref.transform((520,520),Image.Transform.AFFINE,(1/scale,0,source_center[0]-center[0]/scale,0,1/scale,source_center[1]-center[1]/scale),resample=Image.Resampling.BICUBIC)
screen=Image.open(V/'front.png').convert('RGB').crop((343,297,863,817))
assert (np.asarray(screen,float)/255).std(axis=(0,1)).max()>.025,'A launch capture is not a badge comparison'
comparison=Image.new('RGB',(1064,568),(16,17,20));comparison.paste(source,(8,40));comparison.paste(screen,(536,40));draw=ImageDraw.Draw(comparison);draw.text((16,15),'Reference',fill='white');draw.text((544,15),'Simulator',fill='white');comparison.save(V/'comparison.png')
source.resize((2080,2080),Image.Resampling.NEAREST).save(V/'reference_4x.png')
poses=['front','early_turn','side_left','back','side_right','full_turn']
sheet=Image.new('RGB',(1260,820),(16,17,20));draw=ImageDraw.Draw(sheet)
for i,pose in enumerate(poses):
 image=Image.open(V/(pose+'.png')).convert('RGB');box=(343,297,863,817) if pose=='front' else (340,100,860,660)
 image.crop(box).resize((2080,2240 if pose!='front' else 2080),Image.Resampling.NEAREST).save(V/('outline_'+pose+'_4x.png'))
 small=image.crop(box);small.thumbnail((410,375));x=(i%3)*420;y=(i//3)*410;sheet.paste(small,(x,y+25));draw.text((x+8,y+5),pose.replace('_',' '),fill='white')
sheet.save(V/'all_sides.png')
print(V/'comparison.png')
