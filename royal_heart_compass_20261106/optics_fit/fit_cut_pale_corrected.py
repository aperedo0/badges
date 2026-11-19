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
initial_hulls=[planes_of(p) for p in parts];studio=Studio();ids,base=optical(initial_hulls,eye,ray,studio);good=np.zeros(len(x),bool);good[ids]=1;good&=map_coordinates((np.asarray(Image.open(R/'reference_ruby_measurement_mask.png').convert('L'))>0).astype(float),[sy,sx],order=0,mode='constant')>.5
# A deterministic spread of rays preserves whole stone coverage.
ids=np.flatnonzero(good);ids=ids[np.unique(np.linspace(0,len(ids)-1,min(550,len(ids))).astype(int))];eye=eye[ids];ray=ray[ids];target=target[ids];sx=sx[ids];sy=sy[ids]
count=13;first=len(parts[0])-2*count;initial=parts[0][first:first+count,2].copy();girdle=float(parts[0][:first,2].max());start=time.time();history=[];best=[np.inf,None];max_seconds=125

from scipy.optimize import LinearConstraint
from scipy.spatial import ConvexHull
A=[];B=[]
for p in parts:
 h=ConvexHull(p);roof=h.simplices[h.equations[:,2]>.10]
 for face in roof:
  M=np.c_[p[face,:2],np.ones(3)]
  if abs(np.linalg.det(M))<1e-7:continue
  weights=np.c_[p[:,:2],np.ones(len(p))]@np.linalg.inv(M)
  for j,w in enumerate(weights):
   row=np.zeros(13);constant=0.
   if first<=j<first+13:row[j-first]+=1
   else:constant+=p[j,2]
   for k,idx in enumerate(face):
    if first<=idx<first+13:row[idx-first]-=w[k]
    else:constant-=w[k]*p[idx,2]
   if np.max(abs(row))<1e-8:continue
   slack=-constant-row@initial
   # Keep only constraints that can matter within the allowed local change.
   if slack>.20*np.sum(abs(row))+.001:continue
   length=np.linalg.norm(row);A.append(row/length);B.append((slack+2e-5)/length)
A=np.array(A);B=np.array(B);unique,ii=np.unique(np.round(np.c_[A,B],6),axis=0,return_index=True);A=A[ii];B=B[ii]
print('Roof topology constraints',len(A),'initial minimum margin',B.min(),flush=True)
best=[np.inf,np.zeros(13)];calls=[0]
def actual_parts(dz):
 out=[]
 for p in parts:
  q=p.copy();q[first:first+count,2]=initial+dz;out.append(q)
 return out
def objective(dz):
 if time.time()-start>125:raise TimeoutError()
 hulls=[planes_of(p) for p in actual_parts(dz)];ok,lin=optical(hulls,eye,ray,studio);pred=np.zeros_like(target);pred[ok]=np.clip(agx(lin),0,1)
 value=float(np.mean((pred-target)**2))+.015*float(np.mean(dz**2))+30*max(.90*np.std(initial)-np.std(initial+dz),0)**2
 if np.max(A@dz-B)>3e-5:value+=100*float(np.mean(np.maximum(A@dz-B,0)**2))
 if value<best[0] and np.max(A@dz-B)<3e-5:best[:]=[value,dz.copy()]
 calls[0]+=1
 return value
base=objective(np.zeros(13))
try:
 result=minimize(objective,np.zeros(13),method='SLSQP',bounds=[(-.20,.20)]*13,constraints=[LinearConstraint(A,-np.inf,B)],options=dict(maxiter=80,ftol=1e-6,eps=.003))
except TimeoutError:pass
new=actual_parts(best[1]);np.savez_compressed(R/'heart_cut_pale_corrected.npz',**{f'{i}_points':p for i,p in enumerate(new)})
report=dict(status='diagnostic_not_installed',front_cut_topology_constrained=True,maximum_landmark_change=float(max(abs(best[1]))),topology_constraint_maximum_violation=float(np.max(A@best[1]-B)),initial_loss=base,final_loss=best[0],seconds=time.time()-start,calls=calls[0],front_heights=(initial+best[1]).tolist(),deltas=best[1].tolist(),geometry_only=True,pavilion_preserved=True)
(R/'pale_corrected_fit.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
