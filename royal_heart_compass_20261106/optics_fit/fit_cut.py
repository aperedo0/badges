"""Fit physical facet heights against the reference. No appearance map is exported."""
from pathlib import Path
import numpy as np,json,time
from scipy.optimize import minimize
from scipy.ndimage import map_coordinates,binary_erosion,label
from PIL import Image
from forward import planes_of,optical,Studio,unit,agx
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate05';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose'];assert len(parts)==2
native=np.asarray(Image.open(C/'review/front.png').convert('RGB'),float)/255
ref=np.asarray(Image.open(C.parent/'reference.png').convert('RGB'),float)/255
# Choose the actual visible gold component, excluding the floor reflection.
def goldbox(a,roi):
 r,g,b=a.transpose(2,0,1);m=(r>g*1.035)&(g>b*1.06)&(r>.16)&roi;lab,n=label(m);sizes=np.bincount(lab.ravel());sizes[0]=0;yy,xx=np.nonzero(lab==sizes.argmax());return np.array([xx.min(),yy.min(),xx.max(),yy.max()],float)
nroi=np.zeros(native.shape[:2],bool);nroi[330:810,350:860]=1;rb=np.ones(ref.shape[:2],bool);nb=goldbox(native,nroi);rf=goldbox(ref,rb);print('gold alignment',nb,rf,flush=True)
y,x=np.mgrid[365:775:5,390:820:5];x=x.ravel();y=y.ravel();scale=47/60;f=unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],f);mx=(x-603)/scale+540;my=(y-69.3)/scale;ray=unit(f[None,:]+np.c_[(mx-540)/2250,np.zeros(len(x)),np.zeros(len(x))]+((720-my)/2250)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy()
sx=rf[0]+(x-nb[0])/(nb[2]-nb[0])*(rf[2]-rf[0]);sy=rf[1]+(y-nb[1])/(nb[3]-nb[1])*(rf[3]-rf[1]);target=np.stack([map_coordinates(ref[:,:,i],[sy,sx],order=1,mode='constant') for i in range(3)],axis=1)
initial_hulls=[planes_of(p) for p in parts];studio=Studio();ids,base=optical(initial_hulls,eye,ray,studio);good=np.zeros(len(x),bool);good[ids]=1;good&=(target[:,0]>target[:,1]*1.2)&(target[:,0]>.20)
# A deterministic spread of rays preserves whole stone coverage.
ids=np.flatnonzero(good);ids=ids[np.unique(np.linspace(0,len(ids)-1,min(550,len(ids))).astype(int))];eye=eye[ids];ray=ray[ids];target=target[ids];sx=sx[ids];sy=sy[ids]
count=13;first=len(parts[0])-2*count;initial=parts[0][first:first+count,2].copy();girdle=float(parts[0][:first,2].max());start=time.time();history=[];best=[np.inf,None];max_seconds=105

def actual_parts(z):
 out=[]
 for p in parts:
  q=p.copy();q[first:first+count,2]=z
  # Preserve the existing real pavilion so the fit remains constrained.
  out.append(q)
 return out

def objective(z):
 if time.time()-start>max_seconds:raise TimeoutError('Finite fitting interval ended')
 try:
  hulls=[planes_of(p) for p in actual_parts(z)];ok,lin=optical(hulls,eye,ray,studio);pred=np.zeros_like(target);pred[ok]=np.clip(agx(lin),0,1)
  weights=1+30*np.maximum(target.min(1)-.25,0)**2
  loss=float(np.mean(np.mean((pred-target)**2,axis=1)*weights))+.003*float(np.mean((z-initial)**2))
  # Interior landmarks may share a facet plane, but cannot sink well below the cut.
  for points,hull in zip(actual_parts(z),hulls):
   nn,ww=hull;roofgap=(points[first:first+count]@nn.T-ww).max(1)
   loss+=.3*float(np.mean(np.maximum(-roofgap-.012,0)**2))
 except Exception:loss=1.
 if loss<best[0]:best[:]=[loss,z.copy()];history.append(dict(seconds=time.time()-start,loss=loss));(R/'fit_progress.json').write_text(json.dumps(history[-15:],indent=2))
 return loss
base=objective(initial);print('Initial physical fit loss',base,'rays',len(ids),flush=True)
z=initial.copy()
try:
 for sweep in range(5):
  before=best[0]
  for i in np.random.default_rng(271+sweep).permutation(count):
   values=np.unique(np.r_[np.linspace(girdle+.035,1.35,45),np.linspace(max(girdle+.035,z[i]-.12),min(1.7,z[i]+.12),25),z[i]])
   local=(objective(z),z[i])
   for value in values:
    trial=z.copy();trial[i]=value;loss=objective(trial)
    if loss<local[0]:local=(loss,value)
   z[i]=local[1]
  print('Physical cut sweep',sweep,best[0],flush=True)
  if before-best[0]<1e-5:break
except TimeoutError:pass

z=best[1];new=actual_parts(z);out={f'{i}_points':p for i,p in enumerate(new)};np.savez_compressed(R/'heart_cut_fit.npz',**out)
report=dict(status='physical_fit_requires_native_review',native_calibration='native_calibration.json',source_candidate='candidate05',initial_loss=base,final_loss=best[0],seconds=time.time()-start,front_heights=z.tolist(),initial_front_heights=initial.tolist(),exported_appearance_texture=False,pavilion_unchanged=True,rays=len(ids));(R/'fit_result.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
