"""Compare true bounded internal reflection paths, without an appearance image."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
import forward as f
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate20'
D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text())
parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose'];hulls=[f.planes_of(p) for p in parts]
Y,X=np.mgrid[350:835:3,360:850:3];shape=X.shape;x=X.ravel();y=Y.ravel()
axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
ray=f.unit(axis[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up)
eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();studio=f.Studio()
def hash(p):
 q=np.sin(p@np.array([127.1,311.7,74.7]))*43758.5453
 return q-np.floor(q)
def optical(cellsize,coverage,samples):
 valid,lo,_,n,_=f.outer(hulls,eye,ray);ids=np.flatnonzero(valid&(lo>0));o=eye[ids];d=ray[ids];n=n[ids]
 p=o+d*lo[ids,None];entry=f.fresnel(-np.sum(n*d,1),1,1.77)
 out=entry[:,None]*studio.sharp(f.reflect(d,n));w=np.repeat((1-entry)[:,None],3,axis=1);v=f.refract(d,n,1/1.77)
 absorption=np.array([.16,9.,2.8])/np.ptp(parts[0][:,2])
 for hit in range(6):
  ok,_,distance,_,normal=f.outer(hulls,p,v);distance=np.where(ok,distance,0)
  if hit==0 and coverage:
   found=np.zeros(len(p),bool);last=np.full_like(p,np.inf)
   for sample in range(samples):
    cell=np.floor((p+v*distance[:,None]*(sample+.5)/samples)/cellsize)
    different=np.any(cell!=last,axis=1);last=cell
    center=(cell+.5)*cellsize
    plane=f.unit(np.stack([hash(cell),hash(cell+13),hash(cell+29)],axis=1)*2-1)
    approach=np.sum(v*plane,axis=1);travel=np.sum((center-p)*plane,axis=1)/np.where(abs(approach)>.001,approach,1)
    point=p+v*travel[:,None]
    active=(~found)&different&(abs(approach)>.001)&(travel>.001)&(travel<distance)&np.all(abs(point-center)<=cellsize*.5,axis=1)
    ii=np.flatnonzero(active)
    if not len(ii):continue
    pn=np.where((approach[ii]>0)[:,None],-plane[ii],plane[ii])
    share=coverage*f.fresnel(abs(approach[ii]),1.77,1)
    pos=point[ii];direction=f.reflect(v[ii],pn);weight=w[ii]*share[:,None]*np.exp(-absorption*travel[ii,None])
    for bounce in range(2):
     hitok,_,dist,_,exitnormal=f.outer(hulls,pos,direction)
     dist=np.where(hitok,dist,0);pos+=direction*dist[:,None];weight*=np.exp(-absorption*dist[:,None])
     reflected=f.fresnel(np.sum(direction*exitnormal,1),1.77,1)
     outside=f.refract(direction,-exitnormal,1.77)
     out[ii]+=weight*(1-reflected)[:,None]*studio.along(outside)
     weight*=reflected[:,None];direction=f.reflect(direction,exitnormal)
    w[ii]*=1-share[:,None];found[ii]=True
  p+=v*distance[:,None];w*=np.exp(-absorption*distance[:,None]*.99)
  share=f.fresnel(np.sum(v*normal,1),1.77,1);green=f.refract(v,-normal,1.77);rgb=[]
  for channel,index in enumerate([1.76,1.77,1.79]):
   bent=f.refract(v,-normal,index);bent=np.where((np.linalg.norm(bent,axis=1)==0)[:,None],green,bent);rgb.append(studio.along(bent)[:,channel])
  out+=w*(1-share)[:,None]*np.stack(rgb,axis=1);w*=share[:,None];v=f.reflect(v,normal)
 out=(out+w*studio.along(v))*.434211563
 frame=np.full((len(x),3),.03);frame[ids]=np.clip(f.agx(out),0,1)
 return frame.reshape(*shape,3)
variants=[(.16,.065,6),(.12,.20,8),(.09,.30,12),(.075,.45,16)]
sheet=Image.new('RGB',(1000,535),(12,12,15));draw=ImageDraw.Draw(sheet)
for i,(cell,coverage,count) in enumerate(variants):
 a=optical(cell,coverage,count);im=Image.fromarray(np.uint8(a*255)).resize((500,500))
 # Two separate comparison sheets preserve detail at a readable size.
 if i%2==0:
  sheet=Image.new('RGB',(1000,535),(12,12,15));draw=ImageDraw.Draw(sheet)
 sheet.paste(im,((i%2)*500,30));draw.text(((i%2)*500+8,8),f'Cell {cell}, optical reflection share {coverage}, {count} probes',fill='white')
 if i%2:sheet.save(R/f'heart_internal_reflection_{i//2}.png')
(R/'heart_internal_reflection.json').write_text(json.dumps(dict(status='diagnostic_only_not_installed',geometry_source='candidate20',no_appearance_image=True,bounded_internal_planes=True,energy_taken_from_transmission=True,variants=variants),indent=2))
print('Internal reflection comparison ready',flush=True)
