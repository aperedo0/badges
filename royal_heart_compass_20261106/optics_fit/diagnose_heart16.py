"""Separate escaped and unfinished optical paths on the actual saved cut."""
from pathlib import Path
import json,time
import numpy as np
from PIL import Image,ImageDraw
from forward import unit,planes_of,outer,reflect,refract,fresnel,Studio,agx

R=Path(__file__).resolve().parent
C=R.parent/'ruby_heart/candidate16'
D=np.load(C/'geometry.npz')
G=json.loads((C/'groups.json').read_text())
points=[D[f'{i}_points'] for i,g in enumerate(G) if g['mat']=='CrestGem_Rose']
hulls=[planes_of(p) for p in points]
studio=Studio()
Y,X=np.mgrid[340:850:6,350:860:6]
shape=X.shape;x=X.ravel();y=Y.ravel()
f=unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],f)
ray=unit(f[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up)
eye=np.broadcast_to([0,1.8,23.],ray.shape).copy()
valid,lo,_,n,_=outer(hulls,eye,ray);valid&=lo>0
ids=np.flatnonzero(valid);d=ray[ids];n=n[ids]
pos=eye[ids]+d*lo[ids,None]
entry=fresnel(-np.sum(n*d,1),1,1.77)
surface=entry[:,None]*studio.sharp(reflect(d,n))
collected=surface.copy();weight=np.repeat((1-entry)[:,None],3,axis=1)
direction=refract(d,n,1/1.77)
absorption=np.array([.16,9,2.8])/np.ptp(points[0][:,2])
panels=[];reports=[];start=time.time()
for hit in range(24):
 ok,_,distance,_,normal=outer(hulls,pos,direction)
 distance=np.where(ok,distance,0)
 pos+=direction*distance[:,None]
 weight*=np.exp(-absorption*distance[:,None]*.99)
 share=fresnel(np.sum(normal*direction,1),1.77,1)
 green=refract(direction,-normal,1.77);rgb=[]
 for channel,index in enumerate([1.76,1.77,1.79]):
  bent=refract(direction,-normal,index)
  bent=np.where((np.linalg.norm(bent,axis=1)==0)[:,None],green,bent)
  rgb.append(studio.along(bent)[:,channel])
 collected+=weight*(1-share)[:,None]*np.stack(rgb,axis=1)
 weight*=share[:,None];direction=reflect(direction,normal)
 if hit+1 in [3,6,12,24]:
  unfinished=weight*studio.along(direction)
  for label,value in [('with unfinished',collected+unfinished),('escaped only',collected)]:
   frame=np.full((len(x),3),.03);frame[ids]=np.clip(agx(value*.32),0,1)
   panels.append((f'{hit+1} hits, {label}',frame.reshape(*shape,3)))
  reports.append(dict(hits=hit+1,mean_escaped=collected.mean(0).tolist(),mean_unfinished=unfinished.mean(0).tolist(),unfinished_red_share=float(unfinished[:,0].sum()/np.maximum((collected+unfinished)[:,0].sum(),1e-9)),outside_paths=int((~ok).sum())))
native=np.asarray(Image.open(C/'review/native_front_precheck.png').convert('RGB'))/255
panels.insert(0,('Actual native simulator',native[Y,X]))
W=300;H=324;out=Image.new('RGB',(W*3,H*3),(12,12,15));draw=ImageDraw.Draw(out)
for i,(label,a) in enumerate(panels):
 im=Image.fromarray(np.uint8(np.clip(a,0,1)*255)).resize((W,300));ox=i%3*W;oy=i//3*H
 out.paste(im,(ox,oy+24));draw.text((ox+5,oy+5),label,fill='white')
out.save(R/'heart16_path_diagnosis.png')
report=dict(status='diagnostic_only_not_native',candidate='candidate16',no_appearance_images_used_in_optics=True,omissions=['Sparse cleavage','Density noise','Native bloom and antialiasing'],seconds=time.time()-start,paths=reports)
(R/'heart16_path_diagnosis.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
