"""Fit physical crown and pavilion angles, retaining the actual facet graph."""
from pathlib import Path
import time,json
import numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import minimize,LinearConstraint
from scipy.ndimage import map_coordinates,label
from PIL import Image,ImageDraw
from forward import unit,planes_of,outer,reflect,refract,fresnel,Studio,agx
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate16'
D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text())
parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose']
start=time.time();nfree=len(parts[0])-96;initial=parts[0][96:,2].copy()
# Keep both lobe cuts symmetric. The studio provides the asymmetric light.
assert nfree==55
A=[];B=[]
for p in parts:
 hull=ConvexHull(p)
 for face,eq in zip(hull.simplices,hull.equations):
  if abs(eq[2])<.05:continue
  M=np.c_[p[face,:2],np.ones(3)]
  if abs(np.linalg.det(M))<1e-9:continue
  weights=np.c_[p[:,:2],np.ones(len(p))]@np.linalg.inv(M)
  for j,w in enumerate(weights):
   row=np.zeros(nfree);constant=0
   if j>=96:row[j-96]+=1
   else:constant+=p[j,2]
   for k,idx in enumerate(face):
    if idx>=96:row[idx-96]-=w[k]
    else:constant-=w[k]*p[idx,2]
   if eq[2]<0:row=-row;constant=-constant
   length=np.linalg.norm(row)
   if length<1e-8:continue
   slack=-constant-row@initial
   if slack>.40*np.sum(abs(row))+.001:continue
   A.append(row/length);B.append((slack+1e-5)/length)
A=np.array(A);B=np.array(B);_,ii=np.unique(np.round(np.c_[A,B],6),axis=0,return_index=True);A=A[ii];B=B[ii]
print('Physical height parameters',nfree,'support constraints',len(A),flush=True)
native=np.asarray(Image.open(C/'review/native_front_precheck.png').convert('RGB'),float)/255
ref=np.asarray(Image.open(C.parent/'reference.png').convert('RGB'),float)/255
def goldbox(a,roi):
 r,g,b=a.transpose(2,0,1);m=(r>g*1.035)&(g>b*1.06)&(r>.16)&roi;lab,n=label(m);sizes=np.bincount(lab.ravel());sizes[0]=0;yy,xx=np.nonzero(lab==sizes.argmax());return np.array([xx.min(),yy.min(),xx.max(),yy.max()],float)
roi=np.zeros(native.shape[:2],bool);roi[340:835,350:860]=True;nb=goldbox(native,roi);rf=goldbox(ref,np.ones(ref.shape[:2],bool))
f=unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],f)
def rays(x,y):
 d=unit(f[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up)
 return np.broadcast_to([0,1.8,23.],d.shape).copy(),d
def target_at(x,y):
 sx=rf[0]+(x-nb[0])/(nb[2]-nb[0])*(rf[2]-rf[0]);sy=rf[1]+(y-nb[1])/(nb[3]-nb[1])*(rf[3]-rf[1])
 return np.stack([map_coordinates(ref[:,:,i],[sy,sx],order=1,mode='constant') for i in range(3)],axis=1)
Y,X=np.mgrid[360:810:13,375:835:13];x=X.ravel();y=Y.ravel();eye,ray=rays(x,y);target=target_at(x,y)
valid,lo,*_=outer([planes_of(p) for p in parts],eye,ray);valid&=(lo>0)&(target[:,0]>target[:,1]*1.2)&(target[:,2]>target[:,1]*1.1)&(target[:,0]>.25)
ids=np.flatnonzero(valid);ids=ids[np.unique(np.linspace(0,len(ids)-1,min(400,len(ids))).astype(int))];eye=eye[ids];ray=ray[ids];target=target[ids]
studio=Studio();indices=[1.76,1.77,1.79];thickness=np.ptp(parts[0][:,2])
def actual_parts(q):
 out=[]
 for p in parts:
  a=p.copy();a[96:,2]=initial+q[:nfree];out.append(a)
 return out
def optical(q,eye,ray):
 hulls=[planes_of(p) for p in actual_parts(q)]
 valid,lo,_,n,_=outer(hulls,eye,ray);valid&=lo>0;ids=np.flatnonzero(valid);d=ray[ids];n=n[ids]
 pos=eye[ids]+d*lo[ids,None];entry=fresnel(-np.sum(n*d,1),1,1.77)
 collected=entry[:,None]*studio.sharp(reflect(d,n));weight=np.repeat((1-entry)[:,None],3,axis=1);direction=refract(d,n,1/1.77)
 absorption=np.array([.16,9*q[-2],2.8*q[-1]])/thickness
 for hit in range(6):
  ok,_,distance,_,normal=outer(hulls,pos,direction);distance=np.where(ok,distance,0);pos+=direction*distance[:,None];weight*=np.exp(-absorption*distance[:,None]*.99)
  share=fresnel(np.sum(normal*direction,1),1.77,1);green=refract(direction,-normal,1.77);rgb=[]
  for channel,index in enumerate(indices):
   bent=refract(direction,-normal,index);bent=np.where((np.linalg.norm(bent,axis=1)==0)[:,None],green,bent);rgb.append(studio.along(bent)[:,channel])
  collected+=weight*(1-share)[:,None]*np.stack(rgb,axis=1);weight*=share[:,None];direction=reflect(direction,normal)
 return ids,(collected+weight*studio.along(direction))*q[-3]
q0=np.r_[np.zeros(nfree),.32,1,1];best=[np.inf,q0.copy()];calls=0;history=[]
constraint=np.pad(A,((0,0),(0,3)))
def loss(q):
 global calls
 if time.time()-start>180:raise TimeoutError()
 ids,lin=optical(q,eye,ray);pred=np.zeros_like(target);pred[ids]=np.clip(agx(lin),0,1)
 value=float(np.mean((pred-target)**2))+.002*float(np.mean(q[:nfree]**2))
 violation=np.max(constraint@q-B)
 if violation<3e-5 and value<best[0]:
  best[:]=[value,q.copy()];history.append(dict(seconds=time.time()-start,loss=value))
 calls+=1
 return value
base=loss(q0)
try:
 result=minimize(loss,q0,method='SLSQP',bounds=[(-.4,.4)]*nfree+[(.20,1.2),(.2,1.8),(.2,2)],constraints=[LinearConstraint(constraint,-np.inf,B)],options=dict(maxiter=45,ftol=2e-6,eps=.002))
except TimeoutError:pass
q=best[1];np.savez_compressed(R/'heart16_fitted_surfaces.npz',**{f'{i}_points':p for i,p in enumerate(actual_parts(q))})
report=dict(status='diagnostic_not_installed',source='candidate16',physical_geometry_only=True,no_appearance_texture=True,front_and_pavilion_fitted=True,support_violation=float(np.max(constraint@q-B)),initial_loss=base,final_loss=best[0],rays=len(eye),calls=calls,seconds=time.time()-start,exposure=float(q[-3]),absorption=[.16,9*q[-2],2.8*q[-1]],height_deltas=q[:nfree].tolist(),history=history)
(R/'heart16_fitted_surfaces.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['height_deltas','history']}),flush=True)
Y,X=np.mgrid[340:850:4,350:860:4];shape=X.shape;x=X.ravel();y=Y.ravel();eye,ray=rays(x,y);panels=[('Reference',target_at(x,y)),('Current native',native[Y,X].reshape(-1,3))]
for name,q in [('Physical baseline diagnostic',q0),('Physical fit diagnostic',q)]:
 ids,lin=optical(q,eye,ray);frame=np.full((len(x),3),.03);frame[ids]=np.clip(agx(lin),0,1);panels.append((name,frame))
W=400;H=424;out=Image.new('RGB',(W*2,H*2),(12,12,15));draw=ImageDraw.Draw(out)
for i,(name,a) in enumerate(panels):
 ox=i%2*W;oy=i//2*H;im=Image.fromarray(np.uint8(np.clip(a.reshape(*shape,3),0,1)*255)).resize((W,400));out.paste(im,(ox,oy+24));draw.text((ox+5,oy+5),name,fill='white')
out.save(R/'heart16_fitted_surfaces.png')
