"""Fit only uniform physical ruby absorption and throughput to reference color."""
from pathlib import Path
import json,time,numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_closing,binary_fill_holes,binary_erosion,label
from scipy.optimize import minimize
import forward as f
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate24';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose'];hulls=[f.planes_of(p) for p in parts];density=max(.5,1/np.ptp(parts[0][:,2]))
ref=np.asarray(Image.open(C.parent/'reference.png').convert('RGB'),float)/255;r,g,b=ref.transpose(2,0,1);seed=(r>g*1.2)&(b>g*1.2)&(r>.23);lab,n=label(seed);sizes=np.bincount(lab.ravel());sizes[0]=0;mask=binary_erosion(binary_fill_holes(binary_closing(lab==sizes.argmax(),iterations=3)),iterations=6);target=ref[mask][::8]
Y,X=np.mgrid[350:835:4,360:850:4];shape=X.shape;x=X.ravel();y=Y.ravel();axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
ray=f.unit(axis[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();studio=f.Studio()
valid,lo,_,normal,_=f.outer(hulls,eye,ray);ids=np.flatnonzero(valid&(lo>0));inside=np.zeros(len(x),bool);inside[ids]=1;inside=binary_erosion(inside.reshape(shape),iterations=2).ravel();used=inside[ids]
v=ray[ids];normal=normal[ids];p=eye[ids]+v*lo[ids,None];entry=f.fresnel(-np.sum(v*normal,1),1,1.77);surface=entry[:,None]*studio.sharp(f.reflect(v,normal));weight=1-entry;v=f.refract(v,normal,1/1.77);path=np.zeros(len(p));steps=[]
for hit in range(6):
 ok,_,distance,_,normal=f.outer(hulls,p,v);distance=np.where(ok,distance,0);path+=distance*.99;p+=v*distance[:,None];share=f.fresnel(np.sum(v*normal,1),1.77,1);green=f.refract(v,-normal,1.77);rgb=[]
 for channel,index in enumerate([1.76,1.77,1.79]):
  bent=f.refract(v,-normal,index);bent=np.where((np.linalg.norm(bent,axis=1)==0)[:,None],green,bent);rgb.append(studio.along(bent)[:,channel])
 steps.append((path.copy(),(weight*(1-share))[:,None]*np.stack(rgb,axis=1)));weight*=share;v=f.reflect(v,normal)
steps.append((path.copy(),weight[:,None]*studio.along(v)))
def render(q):
 absorption=np.array([q[0],9,q[1]])*density;out=surface.copy()
 for travelled,energy in steps:out+=energy*np.exp(-absorption*travelled[:,None])
 return np.clip(f.agx(out*q[2]),0,1)
quantiles=np.linspace(5,95,19);goal=np.percentile(target,quantiles,axis=0);start=time.time();best=[np.inf,None];history=[];base=np.array([.16,.65,.434211563])
def objective(q):
 if time.time()-start>85:raise TimeoutError()
 pred=render(q)[used];value=float(np.mean((np.percentile(pred,quantiles,axis=0)-goal)**2))
 if value<best[0]:best[:]=[value,q.copy()];history.append(dict(seconds=time.time()-start,loss=value,parameters=q.tolist()))
 return value
initial=objective(base)
try:minimize(objective,base,method='Powell',bounds=[(.01,.5),(.25,2.5),(.25,1.2)],options=dict(maxiter=6,xtol=.003,ftol=.00005))
except TimeoutError:pass
q=best[1];report=dict(status='diagnostic_only_not_installed',geometry_and_shared_studio_unchanged=True,uniform_constants_only=True,no_appearance_image_exported=True,green_absorption_fixed=9,old_parameters=base.tolist(),fitted_parameters=q.tolist(),initial_distribution_loss=initial,final_distribution_loss=best[0],seconds=time.time()-start,reference_outline_excluded=True,prediction_not_native_evidence=True,history=history);(R/'heart24_color_fit.json').write_text(json.dumps(report,indent=2))
sheet=Image.new('RGB',(1000,535),(12,12,15));draw=ImageDraw.Draw(sheet)
for i,(title,params) in enumerate([('Current physical ruby color',base),('Uniform physical color fit prediction',q)]):
 frame=np.full((len(x),3),.03);frame[ids]=render(params);sheet.paste(Image.fromarray(np.uint8(frame.reshape(*shape,3)*255)).resize((500,500)),(i*500,30));draw.text((i*500+6,8),title,fill='white')
sheet.save(R/'heart24_color_fit.png');print(json.dumps({k:v for k,v in report.items() if k!='history'}),flush=True)
