"""Use the detailed crown with a flat polished ruby back, not the rear dome."""
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
import forward as f
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate20';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose']
ps=[]
for p in parts:
 q=p[:139].copy();q[48:96,2]=q[:48,2].mean()-.15;ps.append(q)
np.savez_compressed(R/'heart_rose_cut.npz',**{f'{i}_points':p for i,p in enumerate(ps)})
hulls=[f.planes_of(p) for p in ps]
Y,X=np.mgrid[350:835:3,360:850:3];shape=X.shape;x=X.ravel();y=Y.ravel();axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
ray=f.unit(axis[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();studio=f.Studio()
ok,lo,_,n,_=f.outer(hulls,eye,ray);ids=np.flatnonzero(ok&(lo>0));v=ray[ids];n=n[ids];p=eye[ids]+v*lo[ids,None];entry=f.fresnel(-np.sum(v*n,1),1,1.77);surface=entry[:,None]*studio.sharp(f.reflect(v,n));weight=1-entry;v=f.refract(v,n,1/1.77);path=np.zeros(len(p));steps=[]
for hit in range(6):
 ok,_,distance,_,normal=f.outer(hulls,p,v);distance=np.where(ok,distance,0);path+=distance*.99;p+=v*distance[:,None];share=f.fresnel(np.sum(v*normal,1),1.77,1);green=f.refract(v,-normal,1.77);rgb=[]
 for channel,index in enumerate([1.76,1.77,1.79]):
  bent=f.refract(v,-normal,index);bent=np.where((np.linalg.norm(bent,axis=1)==0)[:,None],green,bent);rgb.append(studio.along(bent)[:,channel])
 steps.append((path.copy(),(weight*(1-share))[:,None]*np.stack(rgb,axis=1)));weight*=share;v=f.reflect(v,normal)
steps.append((path.copy(),weight[:,None]*studio.along(v)))
sheet=Image.new('RGB',(1500,1590),(12,12,15));draw=ImageDraw.Draw(sheet);reports=[]
for i,(red,gain) in enumerate((r,g) for r in [.16,.5,1.] for g in [.434211563,.7,1.0]):
 absorption=np.array([red,9,2.8])/np.ptp(ps[0][:,2]);out=surface.copy()
 for travelled,energy in steps:out+=energy*np.exp(-absorption*travelled[:,None])
 frame=np.full((len(x),3),.03);frame[ids]=np.clip(f.agx(out*gain),0,1);ox=i%3*500;oy=i//3*530;sheet.paste(Image.fromarray(np.uint8(frame.reshape(*shape,3)*255)).resize((500,500)),(ox,oy+25));draw.text((ox+6,oy+6),f'Flat back detailed crown, red absorption {red}, gain {gain:.2f}',fill='white');reports.append(dict(red=red,exposure=gain))
sheet.save(R/'heart_rose_cut_material.png');(R/'heart_rose_cut_material.json').write_text(json.dumps(dict(status='diagnostic_only_not_native',old_shallow_raised_rear_cut_removed=True,detailed_crown_preserved=True,original_clear_optics=True,no_appearance_map=True,variants=reports),indent=2));print('Detailed flat back ruby diagnostic ready',flush=True)
