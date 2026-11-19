"""Check the actual Blender development render against independent native optical equations."""
from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import binary_erosion
import forward as f
R=Path(__file__).resolve().parent;C=R.parent/'sapphire_teardrop/candidate15';P=np.load(C/'blender/optics/planes.npz')['planes'];n=P[:,:3];w=P[:,3];im=np.asarray(Image.open(C/'blender/optics/diagnosis/corrected_ray.png').convert('RGB'))/255;H,W=im.shape[:2];yy,xx=np.mgrid[:H,:W];x=(xx.ravel()+.5-W/2)*6.2/W;y=.27+(H/2-yy.ravel()-.5)*6.2/H;o=np.c_[x,y,np.full(len(x),14.)];inc=np.broadcast_to([0.,0.,-1.],o.shape);ok,entry,_,norm,_=f.interval((n,w),o,inc);ok&=entry>0;mask=binary_erosion(ok.reshape(H,W),iterations=4).ravel();ids=np.flatnonzero(mask);o=o[ids];inc=inc[ids];norm=norm[ids];entry=entry[ids];studio=f.Studio();density=.5;absorption=np.array([8,4.3503597,.2])*density

def trace(flip_v=False):
 def sample(d,level):
  d=d.copy()
  if flip_v:d[:,1]*=-1
  return studio.sample(d,level)
 def sharp(d):return np.minimum(sample(d,1),24)
 def along(d):return sharp(d)+1.4576831*np.minimum(sample(d,8),3)
 F=f.fresnel(-np.sum(norm*inc,1),1,1.77);out=F[:,None]*sharp(f.reflect(inc,norm));weight=np.repeat((1-F)[:,None],3,axis=1);pos=o+inc*entry[:,None];direction=f.refract(inc,norm,1/1.77)
 for hit in range(3):
  approach=direction@n.T;gap=w-pos@n.T;valid=(approach>1e-4)&(gap> -1e-5);distance=np.where(valid,np.maximum(gap,0)/np.where(valid,approach,1),np.inf);ix=distance.argmin(1);t=distance[np.arange(len(ids)),ix];found=np.isfinite(t);t=np.where(found,t,0);facet=n[ix];pos+=direction*t[:,None];weight*=np.exp(-t[:,None]*absorption);share=f.fresnel(np.sum(facet*direction,1),1.77,1);green=f.refract(direction,-facet,1.77);channels=[]
  for ci,index in enumerate([1.76,1.77,1.79]):
   d=f.refract(direction,-facet,index);d=np.where((np.linalg.norm(d,axis=1)==0)[:,None],green,d);channels.append(along(d)[:,ci])
  out+=weight*(1-share)[:,None]*np.stack(channels,1);weight*=share[:,None];direction=np.where(found[:,None],f.reflect(direction,facet),direction)
 out+=weight*along(direction);return np.clip(f.agx(out*.28),0,1)
pred=trace();flip=trace(True);actual=im.reshape(-1,3)[ids];report=dict(development_validation=True,no_app_build=True,body_pixels=len(ids),actual_render_size=[W,H],native_equations_mae=float(np.mean(abs(pred-actual))),vertical_flip_control_mae=float(np.mean(abs(flip-actual))),expected_native_median=np.median(pred,0).tolist(),actual_blender_median=np.median(actual,0).tolist(),native_final_validation_pending=True)
(C/'blender/optics/numeric_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
canvas=np.zeros((H*W,3),np.uint8);canvas[ids]=np.uint8(pred*255);Image.fromarray(canvas.reshape(H,W,3)).save(C/'blender/optics/independent_prediction.png')
