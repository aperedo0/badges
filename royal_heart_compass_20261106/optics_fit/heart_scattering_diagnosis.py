"""Test single scattering in the true ruby volume, without an added light tent."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
from forward import unit,planes_of,outer,reflect,refract,fresnel,Studio,agx
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate18';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose'];hulls=[planes_of(p) for p in parts]
Y,X=np.mgrid[340:850:6,350:860:6];shape=X.shape;x=X.ravel();y=Y.ravel();f=unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],f);ray=unit(f[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();native=np.asarray(Image.open(C/'review/native_front_precheck.png').convert('RGB'),float)/255;panels=[('Actual current native',native[Y,X])]
studio=Studio();n=2048;i=np.arange(n);dy=1-(i+.5)*2/n;r=np.sqrt(1-dy*dy);a=i*np.pi*(3-np.sqrt(5));dirs=np.c_[r*np.cos(a),dy,r*np.sin(a)];incoming=studio.sample(dirs,1).mean(0)
outer_planes=[]
for normal,w in hulls:
 seam=(abs(normal[:,0])>.9999)&(abs(normal[:,1])<1e-4)&(abs(w)<1e-4);outer_planes.append((normal[~seam],w[~seam]))
def nearest_depth(p):return np.maximum.reduce([np.min(w[None,:]-p@normal.T,axis=1) for normal,w in outer_planes]).clip(0)
def optical(sigma,exposure):
 valid,lo,_,normal,_=outer(hulls,eye,ray);valid&=lo>0;ids=np.flatnonzero(valid);d=ray[ids];normal=normal[ids];pos=eye[ids]+d*lo[ids,None];entry=fresnel(-np.sum(normal*d,1),1,1.77);collected=entry[:,None]*studio.sharp(reflect(d,normal));weight=np.repeat((1-entry)[:,None],3,axis=1);direction=refract(d,normal,1/1.77);absorption=np.array([.16,9,2.8])/np.ptp(parts[0][:,2]);extinction=absorption+sigma
 for hit in range(6):
  ok,_,distance,_,normal=outer(hulls,pos,direction);distance=np.where(ok,distance,0)
  for j in range(4):
   travelled=distance*(j+.5)/4;sample=pos+direction*travelled[:,None];depth=nearest_depth(sample);radiance=incoming*np.exp(-extinction*depth[:,None]);collected+=weight*np.exp(-extinction*travelled[:,None])*radiance*(sigma*distance/4)[:,None]
  pos+=direction*distance[:,None];weight*=np.exp(-extinction*distance[:,None]);share=fresnel(np.sum(normal*direction,1),1.77,1);green=refract(direction,-normal,1.77);rgb=[]
  for channel,index in enumerate([1.76,1.77,1.79]):
   bent=refract(direction,-normal,index);bent=np.where((np.linalg.norm(bent,axis=1)==0)[:,None],green,bent);rgb.append(studio.sharp(bent)[:,channel])
  collected+=weight*(1-share)[:,None]*np.stack(rgb,axis=1);weight*=share[:,None];direction=reflect(direction,normal)
 return ids,collected*exposure
for sigma in [.1,.35,.7]:
 for exposure in [.4,.8,1.2]:
  ids,lin=optical(sigma,exposure);frame=np.full((len(x),3),.03);frame[ids]=np.clip(agx(lin),0,1);panels.append((f'Volume scatter {sigma}, exposure {exposure}',frame.reshape(*shape,3)))
W=300;H=324;out=Image.new('RGB',(W*3,H*4),(12,12,15));draw=ImageDraw.Draw(out)
for i,(label,a) in enumerate(panels):
 ox=i%3*W;oy=i//3*H;im=Image.fromarray(np.uint8(np.clip(a,0,1)*255)).resize((W,300));out.paste(im,(ox,oy+24));draw.text((ox+4,oy+5),label,fill='white')
out.save(R/'heart_volume_scattering.png');(R/'heart_volume_scattering.json').write_text(json.dumps(dict(status='diagnostic_only_not_native',actual_studio_spherical_mean=incoming.tolist(),added_soft_light_tent=False,physical_single_scattering=True,incoming_attenuation_approximation='Nearest outer surface distance. No fake internal lobe interface.',no_appearance_images_in_optics=True),indent=2));print('Physical volume scattering diagnostic saved')
