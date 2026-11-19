"""Inspect uniform ruby absorption through actual moving optical paths."""
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
import forward as f
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate21';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose'];hulls=[f.planes_of(p) for p in parts]
Y,X=np.mgrid[350:835:3,360:850:3];shape=X.shape;x=X.ravel();y=Y.ravel();axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
ray=f.unit(axis[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();studio=f.Studio()
valid,lo,_,normal,_=f.outer(hulls,eye,ray);ids=np.flatnonzero(valid&(lo>0));v=ray[ids];normal=normal[ids];p=eye[ids]+v*lo[ids,None];entry=f.fresnel(-np.sum(v*normal,1),1,1.77);surface=entry[:,None]*studio.sharp(f.reflect(v,normal));weight=1-entry;v=f.refract(v,normal,1/1.77);steps=[];travel=np.zeros(len(p))
for hit in range(6):
 ok,_,distance,_,normal=f.outer(hulls,p,v);distance=np.where(ok,distance,0);travel+=distance*.99;p+=v*distance[:,None];share=f.fresnel(np.sum(v*normal,1),1.77,1);green=f.refract(v,-normal,1.77);rgb=[]
 for channel,index in enumerate([1.76,1.77,1.79]):
  bent=f.refract(v,-normal,index);bent=np.where((np.linalg.norm(bent,axis=1)==0)[:,None],green,bent);rgb.append(studio.along(bent)[:,channel])
 steps.append((travel.copy(),(weight*(1-share))[:,None]*np.stack(rgb,axis=1)));weight*=share;v=f.reflect(v,normal)
steps.append((travel.copy(),weight[:,None]*studio.along(v)))
variants=[]
for red in [.16,.5,.9]:
 for blue in [.7,1.3,2,2.8]:
  absorption=np.array([red,9,blue])/np.ptp(parts[0][:,2]);out=surface.copy()
  for path,energy in steps:out+=np.exp(-absorption*path[:,None])*energy
  frame=np.full((len(x),3),.03);frame[ids]=np.clip(f.agx(out*.434211563),0,1);variants.append((f'Uniform absorption {red}, 9, {blue}',frame.reshape(*shape,3)))
for j in range(3):
 sheet=Image.new('RGB',(1000,1060),(12,12,15));draw=ImageDraw.Draw(sheet)
 for i,(title,a) in enumerate(variants[j*4:j*4+4]):
  ox=i%2*500;oy=i//2*530;sheet.paste(Image.fromarray(np.uint8(a*255)).resize((500,500)),(ox,oy+25));draw.text((ox+5,oy+6),title,fill='white')
 sheet.save(R/f'heart_color_continuity21_{j}.png')
(R/'heart_color_continuity21.json').write_text(json.dumps(dict(status='diagnostic_only_not_native',one_constant_absorption_through_whole_ruby=True,no_position_tint_or_appearance_image=True,geometry_unchanged=True),indent=2));print('Ruby material color continuity diagnostic ready',flush=True)
