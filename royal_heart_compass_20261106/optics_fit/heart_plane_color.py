"""Check constant rose ruby absorption on the coordinated physical cut."""
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
import forward as f
R=Path(__file__).resolve().parent
Y,X=np.mgrid[350:835:3,360:850:3];shape=X.shape;x=X.ravel();y=Y.ravel();axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
ray=f.unit(axis[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();studio=f.Studio()
for figure,slope in enumerate([.45,.65]):
 D=np.load(R/f'heart_plane_cut_{slope}_1.7.npz');ps=[D[f'{i}_points'] for i in range(2)];hulls=[f.planes_of(p) for p in ps]
 valid,lo,_,normal,_=f.outer(hulls,eye,ray);ids=np.flatnonzero(valid&(lo>0));v=ray[ids];normal=normal[ids];p=eye[ids]+v*lo[ids,None];entry=f.fresnel(-np.sum(v*normal,1),1,1.77);surface=entry[:,None]*studio.sharp(f.reflect(v,normal));weight=1-entry;v=f.refract(v,normal,1/1.77);path=np.zeros(len(p));steps=[]
 for hit in range(6):
  ok,_,distance,_,normal=f.outer(hulls,p,v);distance=np.where(ok,distance,0);path+=distance*.99;p+=v*distance[:,None];share=f.fresnel(np.sum(v*normal,1),1.77,1);green=f.refract(v,-normal,1.77);rgb=[]
  for channel,index in enumerate([1.76,1.77,1.79]):
   bent=f.refract(v,-normal,index);bent=np.where((np.linalg.norm(bent,axis=1)==0)[:,None],green,bent);rgb.append(studio.along(bent)[:,channel])
  steps.append((path.copy(),(weight*(1-share))[:,None]*np.stack(rgb,axis=1)));weight*=share;v=f.reflect(v,normal)
 steps.append((path.copy(),weight[:,None]*studio.along(v)))
 sheet=Image.new('RGB',(1000,1060),(12,12,15));draw=ImageDraw.Draw(sheet)
 for i,blue in enumerate([.35,.65,1.1,2.8]):
  absorption=np.array([.16,9,blue])*max(.5,1/np.ptp(ps[0][:,2]));out=surface.copy()
  for travelled,energy in steps:out+=energy*np.exp(-absorption*travelled[:,None])
  frame=np.full((len(x),3),.03);frame[ids]=np.clip(f.agx(out*.434211563),0,1);ox=i%2*500;oy=i//2*530;sheet.paste(Image.fromarray(np.uint8(frame.reshape(*shape,3)*255)).resize((500,500)),(ox,oy+25));draw.text((ox+6,oy+6),f'Crown slope {slope}, uniform blue absorption {blue}',fill='white')
 sheet.save(R/f'heart_plane_color_{figure}.png')
(R/'heart_plane_color.json').write_text(json.dumps(dict(status='diagnostic_only_not_native',actual_native_density_clamp_applied=True,one_uniform_absorption_in_actual_clear_ruby=True,no_color_or_reflection_images=True),indent=2));print('Coordinated cut rose color diagnostic ready',flush=True)
