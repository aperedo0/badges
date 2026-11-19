"""Fit only real pavilion facet heights under the unchanged measured studio."""
from pathlib import Path
import json,time
import numpy as np
from scipy.ndimage import map_coordinates,label
from PIL import Image,ImageDraw
import forward as f
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate20'
D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose']
rear=float(parts[0][48:96,2].mean());free=np.flatnonzero(parts[0][:,2]<rear-1e-5);initial=rear-parts[0][free,2]
ref=np.asarray(Image.open(C.parent/'reference.png').convert('RGB'),float)/255
native=np.asarray(Image.open(C/'review/native_front_precheck.png').convert('RGB'),float)/255
def goldbox(a,roi):
 r,g,b=a.transpose(2,0,1);m=(r>g*1.035)&(g>b*1.06)&(r>.16)&roi;lab,n=label(m);sizes=np.bincount(lab.ravel());sizes[0]=0;yy,xx=np.nonzero(lab==sizes.argmax());return np.array([xx.min(),yy.min(),xx.max(),yy.max()],float)
roi=np.zeros(native.shape[:2],bool);roi[330:850,345:865]=1;nb=goldbox(native,roi);rb=goldbox(ref,np.ones(ref.shape[:2],bool))
axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
def rays(x,y):
 ray=f.unit(axis[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up)
 return np.broadcast_to([0,1.8,23.],ray.shape).copy(),ray
def target_at(x,y):
 sx=rb[0]+(x-nb[0])/(nb[2]-nb[0])*(rb[2]-rb[0]);sy=rb[1]+(y-nb[1])/(nb[3]-nb[1])*(rb[3]-rb[1])
 return np.stack([map_coordinates(ref[:,:,i],[sy,sx],order=1,mode='constant') for i in range(3)],axis=1)
Y,X=np.mgrid[355:835:12,365:850:12];x=X.ravel();y=Y.ravel();eye,ray=rays(x,y);target=target_at(x,y)
ok,lo,*_=f.outer([f.planes_of(p) for p in parts],eye,ray)
valid=ok&(lo>0)&(target[:,0]>.25)&(target[:,0]>target[:,1]*1.2)&(target[:,2]>target[:,1]*1.1)
ii=np.flatnonzero(valid);ii=ii[np.unique(np.linspace(0,len(ii)-1,min(520,len(ii))).astype(int))]
eye=eye[ii];ray=ray[ii];target=target[ii]
source=Path(f.__file__).read_text();a=source.index('def optical(');b=source.index('\ndef render',a)
code=source[a:b].replace('def optical(hulls,o,d,studio):','def optical(hulls,o,d,studio,thickness):').replace('absorption=np.array([.16,9.,2.8])*.5','absorption=np.array([.16,9.,2.8])/thickness').replace('*.32','*.434211563')
ns=dict(f.__dict__);exec(code,ns);optical=ns['optical'];studio=f.Studio();start=time.time();best=[np.inf,initial.copy()];history=[];calls=0
def actual(z):
 out=[]
 for p in parts:
  q=p.copy();q[free,2]=rear-z;out.append(q)
 return out
def loss(z):
 global calls
 if time.time()-start>420:raise TimeoutError()
 ps=actual(z);hulls=[f.planes_of(p) for p in ps]
 ids,lin=optical(hulls,eye,ray,studio,np.ptp(ps[0][:,2]));pred=np.zeros_like(target);pred[ids]=np.clip(f.agx(lin),0,1)
 value=float(np.mean((pred-target)**2))+.0002*float(np.mean((z-initial)**2))
 if value<best[0]:
  best[:]=[value,z.copy()];history.append(dict(seconds=time.time()-start,loss=value))
  (R/'heart20_pavilion_fit_progress.json').write_text(json.dumps(dict(seconds=time.time()-start,calls=calls,loss=value,heights=z.tolist()),indent=2))
 calls+=1;return value
base=loss(initial);print('Pavilion parameters',len(free),'rays',len(eye),'base',base,flush=True)
try:
 for mult in [1,1.5,2,2.5,3]:loss(initial*mult)
 z=best[1].copy()
 for sweep in range(8):
  before=best[0]
  for i in np.random.default_rng(639+sweep).permutation(len(z)):
   center=z[i];span=.50 if sweep<2 else .22 if sweep<5 else .09
   options=np.unique(np.r_[center,np.linspace(max(.04,center-span),min(2.1,center+span),11)])
   local=(loss(z),center)
   for v in options:
    q=z.copy();q[i]=v;err=loss(q)
    if err<local[0]:local=(err,v)
   z[i]=local[1]
  print('Pavilion sweep',sweep,'loss',best[0],flush=True)
  if before-best[0]<1e-6:break
except TimeoutError:print('Finite diagnostic interval ended',flush=True)
ps=actual(best[1]);np.savez_compressed(R/'heart20_pavilion_fitted.npz',**{f'{i}_points':p for i,p in enumerate(ps)})
(R/'heart20_pavilion_fit.json').write_text(json.dumps(dict(status='diagnostic_only_not_native',front_and_outline_unchanged=True,no_appearance_images=True,initial_loss=base,final_loss=best[0],seconds=time.time()-start,calls=calls,pavilion_indices=free.tolist(),pavilion_heights=best[1].tolist(),source='candidate20',history=history),indent=2))
Y,X=np.mgrid[345:840:3,355:855:3];shape=X.shape;x=X.ravel();y=Y.ravel();eye,ray=rays(x,y)
panels=[('Reference',target_at(x,y).reshape(*shape,3)),('Actual current native',native[Y,X])]
for name,points in [('Physical baseline',[p.copy() for p in parts]),('Fitted actual pavilion',ps)]:
 ids,lin=optical([f.planes_of(p) for p in points],eye,ray,studio,np.ptp(points[0][:,2]));frame=np.full((len(x),3),.03);frame[ids]=np.clip(f.agx(lin),0,1);panels.append((name,frame.reshape(*shape,3)))
sheet=Image.new('RGB',(1000,1060),(12,12,15));draw=ImageDraw.Draw(sheet)
for i,(title,a) in enumerate(panels):
 ox=i%2*500;oy=i//2*530;sheet.paste(Image.fromarray(np.uint8(np.clip(a,0,1)*255)).resize((500,500)),(ox,oy+25));draw.text((ox+6,oy+6),title,fill='white')
sheet.save(R/'heart20_pavilion_fit.png');print('Physical pavilion diagnostic finished',calls,best[0],flush=True)
