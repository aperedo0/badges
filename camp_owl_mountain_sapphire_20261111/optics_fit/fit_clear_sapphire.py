"""Fit uniform optical constants, never an appearance image for the stone."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy.optimize import minimize
from shapely.geometry import Polygon
import shapely
import forward as f

R=Path(__file__).resolve().parent;C=R.parent/'sapphire_teardrop/candidate05'
D=np.load(C/'parts.npz');meta=json.loads((C/'parts.json').read_text());U=meta['units']
corners=D['gem_v'];center=corners.reshape(-1,3).mean(0);planes=[]
for triangle in corners:
 n=np.cross(triangle[1]-triangle[0],triangle[2]-triangle[0]);n/=np.linalg.norm(n);w=float(n@triangle[0])
 if n@center>w:n=-n;w=-w
 p=np.r_[n,w]
 if not any(np.max(abs(p-q))<=.001 for q in planes):planes.append(p)
planes=np.asarray(planes);hull=(planes[:,:3],planes[:,3]);hulls=[hull,hull]
xx,yy=np.meshgrid(np.arange(485,776,8),np.arange(440,817,8));x,y=xx.ravel(),yy.ravel()
table=Polygon([[626,432],[772,624],[722,782],[626,818],[531,778],[482,624]]).buffer(-12)
keep=shapely.contains_xy(table,x,y);x,y=x[keep],y[keep]
P=np.c_[(x-U['axis'])*U['S'],2.995-(y-U['top'])*U['S'],np.full(len(x),.64)]
eye=np.broadcast_to([0,1.8,23.],P.shape).copy();direction=f.unit(P-eye)
ok,entry,_,normal,_=f.outer(hulls,eye,direction);assert ok.all()
position=eye+direction*entry[:,None];F=f.fresnel(-np.sum(normal*direction,1),1,1.77)
studio=f.Studio();surface=F[:,None]*studio.sharp(f.reflect(direction,normal));weight=1-F;direction=f.refract(direction,normal,1/1.77)
length=np.zeros(len(x));terms=[]
def samples(direction):
 return studio.sharp(direction),np.minimum(studio.sample(direction,8),3)
for hit in range(3):
 ok,_,distance,_,normal=f.outer(hulls,position,direction);assert ok.all()
 length+=distance;position+=direction*distance[:,None];share=f.fresnel(np.sum(normal*direction,1),1.77,1)
 green=f.refract(direction,-normal,1.77);sharp=[];tent=[]
 for channel,index in enumerate([1.76,1.77,1.79]):
  bent=f.refract(direction,-normal,index);bent=np.where((np.linalg.norm(bent,axis=1)==0)[:,None],green,bent)
  a,b=samples(bent);sharp.append(a[:,channel]);tent.append(b[:,channel])
 terms.append((length.copy(),(weight*(1-share)).copy(),np.stack(sharp,1),np.stack(tent,1)))
 weight*=share;direction=f.reflect(direction,normal)
a,b=samples(direction);terms.append((length.copy(),weight.copy(),a,b))
density=.78125;exposure=.28
def color(gain,green):
 total=surface.copy();absorption=np.array([8.,green,.2])*density
 for length,weight,sharp,tent in terms:total+=weight[:,None]*np.exp(-length[:,None]*absorption)*(sharp+gain*tent)
 return np.clip(f.agx(total*exposure),0,1)
target=np.asarray(Image.open(R.parent/'sapphire_teardrop/reference.png').convert('RGB'))[y,x]/255
native=np.asarray(Image.open(C/'app/front.png').convert('RGB'))/255
axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis);delta=P-eye;depth=delta@axis
sx=np.rint(603+1762.5*delta[:,0]/depth).astype(int);sy=np.rint(633.3-1762.5*(delta@up)/depth).astype(int);actual=native[sy,sx]
pred=color(3,2);calibration_error=float(np.mean(abs(pred-actual)))
quantiles=[.1,.3,.5,.7,.9];target_q=np.quantile(target,quantiles,axis=0)
def loss(p):
 candidate=color(float(np.exp(p[0])),float(p[1]));q=np.quantile(candidate,quantiles,axis=0)
 return float(np.mean((q-target_q)**2))
fit=minimize(loss,np.array([np.log(.7),3.]),method='Nelder-Mead',bounds=[(np.log(.03),np.log(3)),(.4,7)],options=dict(maxiter=80,xatol=.002,fatol=1e-7))
gain,green=float(np.exp(fit.x[0])),float(fit.x[1]);after=color(gain,green)
report=dict(uniform_material_only=True,no_appearance_image_created=True,existing_studio_preserved=True,reference_body_samples=len(x),native_forward_calibration_error=calibration_error,calibration_reliable=calibration_error<.08,original_tent_gain=3,original_green_absorption=2,fitted_tent_gain=gain,fitted_green_absorption=green,before_loss=loss([np.log(3),2]),after_loss=loss(fit.x),predicted_original_median=np.median(pred,0).tolist(),actual_native_median=np.median(actual,0).tolist(),reference_median=np.median(target,0).tolist(),predicted_fitted_median=np.median(after,0).tolist(),native_review_pending=True)
(R/'clear_sapphire_uniform_fit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
