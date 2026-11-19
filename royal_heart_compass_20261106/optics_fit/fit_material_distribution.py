"""Fit constant physical absorption and optical throughput on the fixed cut."""
from pathlib import Path
import json,time,numpy as np
from scipy.optimize import minimize
from scipy.ndimage import map_coordinates,binary_fill_holes,binary_closing,label,binary_erosion
from PIL import Image
import forward
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate05'
D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());hulls=[forward.planes_of(D[f'{i}_points']) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose']
source=Path(forward.__file__).read_text();start=source.index('def optical(');end=source.index('\ndef render',start)
code=source[start:end].replace('def optical(hulls,o,d,studio):','def parameter_optical(hulls,o,d,studio,parameters):').replace('absorption=np.array([.16,9.,2.8])*.5','absorption=np.array(parameters[:3])*.5').replace('*.32','*parameters[3]')
ns=dict(forward.__dict__);exec(code,ns);optical=ns['parameter_optical'];studio=forward.Studio()
studio.gain=.9
studio.along=lambda d: studio.sharp(d)+np.minimum(studio.sample(d,8),3)*studio.gain
ref=np.asarray(Image.open(C.parent/'reference.png').convert('RGB'),float)/255
Y,X=np.mgrid[365:775:9,390:820:9];x=X.ravel();y=Y.ravel();scale=47/60;f=forward.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],f);mx=(x-603)/scale+540;my=(y-69.3)/scale;ray=forward.unit(f[None,:]+np.c_[(mx-540)/2250,np.zeros(len(x)),np.zeros(len(x))]+((720-my)/2250)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy()
sx=118+(x-388)/429*1006;sy=111+(y-361)/409*1002;target=np.stack([map_coordinates(ref[:,:,i],[sy,sx],order=1,mode='constant') for i in range(3)],axis=1)
ids,lin=optical(hulls,eye,ray,studio,[.16,9,2.8,.32,.9]);valid=np.zeros(len(x),bool);valid[ids]=True;rr,gg,bb=ref.transpose(2,0,1);seed=(rr>gg*1.15)&(bb>gg*1.15)&(rr>.25)
lab,n=label(seed);sizes=np.bincount(lab.ravel());sizes[0]=0;gemmask=binary_erosion(binary_fill_holes(binary_closing(lab==sizes.argmax(),iterations=4)),iterations=5)
valid&=map_coordinates(gemmask.astype(float),[sy,sx],order=0,mode='constant')>.5
Image.fromarray(np.uint8(gemmask)*255).save(R/'reference_ruby_measurement_mask.png')
eye=eye[valid];ray=ray[valid];target=target[valid]
t0=time.time();best=[float('inf'),None];history=[];base=np.array([.16,9,2.8,.32,.9]);bounds=[(.02,.8),(1.5,13),(.1,4),(.15,1.6),(.08,3)]
def loss(p):
 if time.time()-t0>135:raise TimeoutError()
 studio.gain=p[4];ids,lin=optical(hulls,eye,ray,studio,p);a=np.zeros_like(target);a[ids]=np.clip(forward.agx(lin),0,1)
 # Full color agreement, with bright target facets given the same weight.
 qs=np.linspace(3,97,24)
 value=float(np.mean((np.percentile(a,qs,axis=0)-np.percentile(target,qs,axis=0))**2))
 saturation=lambda rgb:(rgb.max(1)-rgb.min(1))/np.maximum(rgb.max(1),1e-4)
 value+=.18*float(np.mean((np.percentile(saturation(a),qs)-np.percentile(saturation(target),qs))**2))
 if value<best[0]:best[:]=[value,p.copy()];history.append(dict(seconds=time.time()-t0,loss=value,parameters=p.tolist()))
 return value
initial=loss(base)
try:
 for p in [base,[.08,6.,1.2,.7,1.4],[.10,5.,.8,.6,2.]]:
  minimize(loss,np.array(p),method='Powell',bounds=bounds,options=dict(maxiter=5,xtol=.015,ftol=.0002))
except TimeoutError:pass
p=best[1];report=dict(status='diagnostic_only_not_installed',fixed_geometry=True,no_appearance_texture=True,parameters=dict(absorption=p[:3].tolist(),exposure=float(p[3]),tent_gain=float(p[4])),initial_loss=initial,final_loss=best[0],seconds=time.time()-t0,rays=len(eye),history=history)
(R/'material_distribution_fit.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='history'}),flush=True)
# Full diagnostic projection with unchanged geometry.
Y,X=np.mgrid[355:785:3,380:830:3];shape=X.shape;x=X.ravel();y=Y.ravel();mx=(x-603)/scale+540;my=(y-69.3)/scale;ray=forward.unit(f[None,:]+np.c_[(mx-540)/2250,np.zeros(len(x)),np.zeros(len(x))]+((720-my)/2250)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();sx=118+(x-388)/429*1006;sy=111+(y-361)/409*1002;target=np.stack([map_coordinates(ref[:,:,i],[sy,sx],order=1,mode='constant') for i in range(3)],axis=1);panels=[target]
for q in [base,p]:
 studio.gain=q[4];ids,lin=optical(hulls,eye,ray,studio,q);a=np.full((len(x),3),.03);a[ids]=np.clip(forward.agx(lin),0,1);panels.append(a)
Image.fromarray(np.concatenate([np.uint8(np.clip(a.reshape(*shape,3),0,1)*255) for a in panels],axis=1)).resize((900,shape[0]*2)).save(R/'material_distribution_comparison.png')
