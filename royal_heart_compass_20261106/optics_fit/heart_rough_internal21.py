"""Integrate a rough dielectric exit lobe without changing the light or body tint."""
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
import forward as f
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate21';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose'];hulls=[f.planes_of(p) for p in parts]
Y,X=np.mgrid[350:835:3,360:850:3];shape=X.shape;x=X.ravel();y=Y.ravel();axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
ray=f.unit(axis[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();studio=f.Studio()
def optical(roughness):
 ok,lo,_,n,_=f.outer(hulls,eye,ray);ids=np.flatnonzero(ok&(lo>0));p=eye[ids]+ray[ids]*lo[ids,None];v=ray[ids];n=n[ids]
 entry=f.fresnel(-np.sum(n*v,1),1,1.77);out=entry[:,None]*studio.sharp(f.reflect(v,n));weight=np.repeat((1-entry)[:,None],3,axis=1);v=f.refract(v,n,1/1.77);absorption=np.array([.16,9.,2.8])/np.ptp(parts[0][:,2])
 for hit in range(6):
  ok,_,distance,_,normal=f.outer(hulls,p,v);distance=np.where(ok,distance,0);p+=v*distance[:,None];weight*=np.exp(-absorption*distance[:,None]*.99)
  reference=np.tile([0,1.,0],(len(p),1));reference[abs(normal[:,1])>.9]=[1.,0,0];u=f.unit(np.cross(normal,reference));w=np.cross(normal,u);mean_reflect=np.zeros(len(p));escaped=np.zeros_like(out)
  for offset in [u,-u,w,-w]:
   micro=f.unit(normal+roughness*offset);cos=np.clip(np.sum(v*micro,1),0,1);share=f.fresnel(cos,1.77,1);direction=f.refract(v,-micro,1.77);escaped+=(1-share)[:,None]*studio.along(direction)/4;mean_reflect+=share/4
  out+=weight*escaped;weight*=mean_reflect[:,None];v=f.reflect(v,normal)
 out=(out+weight*studio.along(v))*.434211563
 frame=np.full((len(x),3),.03);frame[ids]=np.clip(f.agx(out),0,1);return frame.reshape(*shape,3)
sheet=Image.new('RGB',(1500,1060),(12,12,15));draw=ImageDraw.Draw(sheet)
for i,rough in enumerate([0,.08,.16,.24,.32,.48]):
 a=optical(rough);ox=i%3*500;oy=i//3*530;sheet.paste(Image.fromarray(np.uint8(a*255)).resize((500,500)),(ox,oy+25));draw.text((ox+6,oy+6),f'Internal dielectric normal spread {rough}',fill='white')
sheet.save(R/'heart_rough_internal21.png');(R/'heart_rough_internal21.json').write_text(json.dumps(dict(status='diagnostic_only_not_native',actual_geometry_and_environment_unchanged=True,four_internal_microfacet_escape_samples=True,energy_normalized=True,reflected_path_approximation='One macrofacet continuation with mean Fresnel weight',no_appearance_maps=True),indent=2));print('Rough internal dielectric diagnostic ready',flush=True)
