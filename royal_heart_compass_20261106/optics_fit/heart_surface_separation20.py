"""Separate real surface reflection from colored internal light paths."""
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
import forward as f
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate20'
D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());ps=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose'];hulls=[f.planes_of(p) for p in ps]
Y,X=np.mgrid[350:835:3,360:850:3];shape=X.shape;x=X.ravel();y=Y.ravel();axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
ray=f.unit(axis[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();studio=f.Studio()
ok,lo,_,normal,_=f.outer(hulls,eye,ray);ids=np.flatnonzero(ok&(lo>0));n=normal[ids];v=ray[ids];position=eye[ids]+v*lo[ids,None]
share=f.fresnel(-np.sum(n*v,1),1,1.77);surface=share[:,None]*studio.sharp(f.reflect(v,n))*.434211563
source=Path(f.__file__).read_text();a=source.index('def optical(');b=source.index('\ndef render',a)
code=source[a:b].replace('absorption=np.array([.16,9.,2.8])*.5','absorption=np.array([.16,9.,2.8])/'+repr(float(np.ptp(ps[0][:,2])))).replace('*.32','*.434211563');ns=dict(f.__dict__);exec(code,ns);_,total=ns['optical'](hulls,eye,ray,studio);through=np.maximum(total-surface,0)
sheet=Image.new('RGB',(1500,535),(12,12,15));draw=ImageDraw.Draw(sheet)
for i,(title,lin) in enumerate([('Total current optics',total),('Neutral surface reflection only',surface),('Only colored internal light',through)]):
 frame=np.full((len(x),3),.03);frame[ids]=np.clip(f.agx(lin),0,1);sheet.paste(Image.fromarray(np.uint8(frame.reshape(*shape,3)*255)).resize((500,500)),(i*500,30));draw.text((i*500+6,8),title,fill='white')
sheet.save(R/'heart_surface_separation20.png')
bright=(np.min(f.agx(total),axis=1)>.48)&(y[ids]>470)&(y[ids]<650)&(abs(x[ids]-603)<90)
records=[]
for i in np.flatnonzero(bright)[::max(1,int(bright.sum()/12))]:
 records.append(dict(pixel=[int(x[ids[i]]),int(y[ids[i]])],point=position[i].tolist(),normal=n[i].tolist(),surface_fraction=(surface[i]/np.maximum(total[i],1e-7)).tolist()))
(R/'heart_surface_separation20.json').write_text(json.dumps(dict(status='diagnostic_only',central_neutral_samples=records),indent=2));print('Reflection separation ready',len(records),flush=True)
