"""Test light scattered inside the actual ruby volume with energy attenuation."""
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
import forward as f
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate21'
D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose'];hulls=[f.planes_of(p) for p in parts]
Y,X=np.mgrid[350:835:4,360:850:4];shape=X.shape;x=X.ravel();y=Y.ravel();axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
ray=f.unit(axis[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();studio=f.Studio()
n=2048;i=np.arange(n);dy=1-(i+.5)*2/n;r=np.sqrt(1-dy*dy);a=i*np.pi*(3-np.sqrt(5));dirs=np.c_[r*np.cos(a),dy,r*np.sin(a)];incoming=studio.sample(dirs,1).mean(0)
outer=[]
for normal,w in hulls:
 seam=(abs(normal[:,0])>.9999)&(abs(normal[:,1])<1e-4)&(abs(w)<1e-4);outer.append((normal[~seam],w[~seam]))
def nearest(p):return np.maximum.reduce([np.min(w[None,:]-p@normal.T,axis=1) for normal,w in outer]).clip(0)
def optical(sigma):
 ok,lo,_,n,_=f.outer(hulls,eye,ray);ids=np.flatnonzero(ok&(lo>0));p=eye[ids]+ray[ids]*lo[ids,None];v=ray[ids];n=n[ids]
 entry=f.fresnel(-np.sum(n*v,1),1,1.77);out=entry[:,None]*studio.sharp(f.reflect(v,n));weight=np.repeat((1-entry)[:,None],3,axis=1);v=f.refract(v,n,1/1.77)
 absorption=np.array([.16,9.,2.8])/np.ptp(parts[0][:,2]);extinction=absorption+sigma
 for hit in range(6):
  ok,_,distance,_,normal=f.outer(hulls,p,v);distance=np.where(ok,distance,0)
  for j in range(4):
   travelled=distance*(j+.5)/4;sample=p+v*travelled[:,None];depth=nearest(sample);radiance=incoming*np.exp(-extinction*depth[:,None])
   out+=weight*np.exp(-extinction*travelled[:,None])*radiance*(sigma*distance/4)[:,None]
  p+=v*distance[:,None];weight*=np.exp(-extinction*distance[:,None]);share=f.fresnel(np.sum(v*normal,1),1.77,1);green=f.refract(v,-normal,1.77);rgb=[]
  for channel,index in enumerate([1.76,1.77,1.79]):
   bent=f.refract(v,-normal,index);bent=np.where((np.linalg.norm(bent,axis=1)==0)[:,None],green,bent);rgb.append(studio.along(bent)[:,channel])
  out+=weight*(1-share)[:,None]*np.stack(rgb,axis=1);weight*=share[:,None];v=f.reflect(v,normal)
 out=(out+weight*studio.along(v))*.434211563
 frame=np.full((len(x),3),.03);frame[ids]=np.clip(f.agx(out),0,1);return frame.reshape(*shape,3)
sheet=Image.new('RGB',(1500,1060),(12,12,15));draw=ImageDraw.Draw(sheet)
for i,sigma in enumerate([0,.15,.35,.7,1.5,3.]):
 a=optical(sigma);ox=i%3*500;oy=i//3*530;sheet.paste(Image.fromarray(np.uint8(a*255)).resize((500,500)),(ox,oy+25));draw.text((ox+6,oy+6),f'Homogeneous volume scatter {sigma}',fill='white')
sheet.save(R/'heart_volume21.png');(R/'heart_volume21.json').write_text(json.dumps(dict(status='diagnostic_only_not_native',reference_image_not_used_by_material=True,studio_radiance_mean=incoming.tolist(),single_scatter_with_extinction=True),indent=2));print('Homogeneous volume diagnostic ready',flush=True)
