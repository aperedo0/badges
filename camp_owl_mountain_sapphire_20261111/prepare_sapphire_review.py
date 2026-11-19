"""Package actual complete Blender renders and the original reference for visual review."""
from pathlib import Path
from PIL import Image,ImageDraw
import sys,shutil
R=Path(__file__).resolve().parent;C=R/'sapphire_teardrop'/sys.argv[1];F=C/'blender/optics';O=C/'blender/review';O.mkdir(exist_ok=True,parents=True)
def rgb(p):
 im=Image.open(p).convert('RGBA');bg=Image.new('RGBA',im.size,(28,28,34,255));return Image.alpha_composite(bg,im).convert('RGB')
im=rgb(F/'front.png');im.save(O/'full.png');w,h=im.size
for k,(x,y) in enumerate([(0,0),(w//2,0),(0,h//2),(w//2,h//2)],1):im.crop((x,y,x+w//2,y+h//2)).resize((w,h),Image.Resampling.NEAREST).save(O/f'tile_{k}.png')
regions=[(.37,.05,.63,.25),(.32,.36,.68,.60),(.32,.72,.68,.93)];strips=[]
for x0,y0,x1,y1 in regions:
 crop=im.crop(tuple(int(a*b) for a,b in zip([x0,y0,x1,y1],[w,h,w,h])));strips.append(crop.resize((crop.width*4,crop.height*4),Image.Resampling.NEAREST))
canvas=Image.new('RGB',(max(i.width for i in strips),sum(i.height for i in strips)),(28,28,34));offset=0
for i in strips:canvas.paste(i,(0,offset));offset+=i.height
canvas.save(O/'detail_4x.png')
ref=rgb(C.parent/'reference.png');a=ref.crop((260,140,992,1025));b=im.crop((int(w*.145),int(h*.06),int(w*.855),int(h*.932)));target_h=800
panels=[i.resize((round(i.width*target_h/i.height),target_h),Image.Resampling.LANCZOS) for i in [a,b]]
canvas=Image.new('RGB',(sum(i.width for i in panels)+60,840),(28,28,34));draw=ImageDraw.Draw(canvas);offset=20
for i,label in zip(panels,['OWNER REFERENCE','ACTUAL BLENDER RENDER']):draw.text((offset,8),label,fill='white');canvas.paste(i,(offset,30));offset+=i.width+20
canvas.save(O/'comparison.png');canvas.resize((round(canvas.width/3),280),Image.Resampling.LANCZOS).save(O/'phone_comparison.png')
poses=['front','early_turn','side_left','back','side_right'];canvas=Image.new('RGB',(300*len(poses),330),(28,28,34));draw=ImageDraw.Draw(canvas)
for k,p in enumerate(poses):canvas.paste(rgb(F/(p+'.png')).resize((300,300),Image.Resampling.LANCZOS),(300*k,30));draw.text((300*k+5,10),p,fill='white')
canvas.save(O/'turn_strip.png')
paths=[O/f for f in ['full.png','tile_1.png','tile_2.png','tile_3.png','tile_4.png','detail_4x.png','comparison.png','phone_comparison.png','turn_strip.png']]+[C.parent/'reference.png']
(O/'finish_brief.md').write_text('Read only this brief and its pictures. No edits. These are actual Blender development renders, not app captures. First list every visible surface or outline defect. Then judge whether the design is ready for final app validation and compare the shapes, proportions, cut, materials and color with the owner reference. Actual 3D highlights and internal reflections can naturally differ from a painted mockup. Do not assert final app or full motion acceptance from Blender stills. Give a readiness verdict and a reference design closeness score out of 100.\n\n'+'\n'.join(str(p) for p in paths)+'\n');print(O)
