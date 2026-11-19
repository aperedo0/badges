"""Compare continuous ruby transport with bounded volume and rough internal exits."""
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
import forward as f
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate21';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose'];hulls=[f.planes_of(p) for p in parts]
Y,X=np.mgrid[350:835:4,360:850:4];shape=X.shape;x=X.ravel();y=Y.ravel();axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
ray=f.unit(axis[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();studio=f.Studio();incoming=np.load(R/'studio.npz')['rgb'].mean((0,1))*.92
def optical(sigma,tent,roughness,exposure):
 studio.along=lambda d:studio.sharp(d)+np.minimum(studio.sample(d,8),3)*tent
 ok,lo,_,n,_=f.outer(hulls,eye,ray);ids=np.flatnonzero(ok&(lo>0));p=eye[ids]+ray[ids]*lo[ids,None];v=ray[ids];n=n[ids]
 entry=f.fresnel(-np.sum(n*v,1),1,1.77);out=entry[:,None]*studio.sharp(f.reflect(v,n));weight=np.repeat((1-entry)[:,None],3,axis=1);v=f.refract(v,n,1/1.77);previous=n.copy();absorption=np.array([.16,9.,2.8])/np.ptp(parts[0][:,2]);extinction=absorption+sigma
 for hit in range(6):
  ok,_,distance,_,normal=f.outer(hulls,p,v);distance=np.where(ok,distance,0)
  for j in range(4):
   travelled=distance*(j+.5)/4;depth=np.minimum(abs(np.sum(v*previous,1))*travelled,abs(np.sum(v*normal,1))*(distance-travelled));radiance=incoming*np.exp(-extinction*depth[:,None]);out+=weight*np.exp(-extinction*travelled[:,None])*radiance*(sigma*distance/4)[:,None]
  p+=v*distance[:,None];weight*=np.exp(-extinction*distance[:,None]);previous=normal.copy();reference=np.tile([0,1.,0],(len(p),1));reference[abs(normal[:,1])>.9]=[1.,0,0];u=f.unit(np.cross(normal,reference));w=np.cross(normal,u);mean=np.zeros(len(p));escaped=np.zeros_like(out)
  for offset in [u,-u,w,-w]:
   micro=f.unit(normal+roughness*offset);share=f.fresnel(np.clip(np.sum(v*micro,1),0,1),1.77,1);direction=f.refract(v,-micro,1.77);escaped+=(1-share)[:,None]*studio.along(direction)/4;mean+=share/4
  out+=weight*escaped;weight*=mean[:,None];v=f.reflect(v,normal)
 out=(out+weight*studio.along(v))*exposure
 frame=np.full((len(x),3),.03);frame[ids]=np.clip(f.agx(out),0,1);return frame.reshape(*shape,3)
variants=[('Current native22 approximation',.65/np.ptp(parts[0][:,2]),.9,0,.434211563),('Actual volume only',.12,0,.16,1.2),('Subtle soft transmission',.25,.15,.16,.8),('Rough internal exits',.20,.35,.24,.8),('Clearer body',.15,.25,.32,.9),('Stronger volume only',.40,0,.10,1.2)]
for j in range(3):
 sheet=Image.new('RGB',(1000,535),(12,12,15));draw=ImageDraw.Draw(sheet)
 for i,(title,sigma,tent,rough,exposure) in enumerate(variants[j*2:j*2+2]):
  a=optical(sigma,tent,rough,exposure);sheet.paste(Image.fromarray(np.uint8(a*255)).resize((500,500)),(i*500,30));draw.text((i*500+5,8),title,fill='white')
 sheet.save(R/f'heart_balanced_volume21_{j}.png')
(R/'heart_balanced_volume21.json').write_text(json.dumps(dict(status='diagnostic_only_not_native',actual_geometry_and_light_unchanged=True,homogeneous_medium_and_microfacet_exit_integral=True,no_reference_color_map=True,variants=variants),indent=2));print('Balanced ruby transport diagnostic ready',flush=True)
