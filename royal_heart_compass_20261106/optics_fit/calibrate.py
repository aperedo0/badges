"""Compare numeric optics to the actual native front, not to the target photo."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.ndimage import binary_erosion
from forward import planes_of,optical,Studio,unit,agx
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate05';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());hulls=[planes_of(D[f'{i}_points']) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose'];native=np.asarray(Image.open(C/'review/front.png').convert('RGB'),float)/255
ys,xs=np.mgrid[355:785:2,385:825:2];x=xs.ravel();y=ys.ravel();f=unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],f);scale=47/60
mx=(x-603)/scale+540;my=(y-69.3)/scale
ray=unit(f[None,:]+np.c_[(mx-540)/2250,np.zeros(len(x)),np.zeros(len(x))]+((720-my)/2250)[:,None]*up)
eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();ids,color=optical(hulls,eye,ray,Studio());mask=np.zeros(len(x),bool);mask[ids]=True;mask=mask.reshape(xs.shape);safe=binary_erosion(mask,iterations=3).ravel();pred=np.zeros((len(x),3));pred[ids]=np.clip(agx(color),0,1);obs=native[y,x];err=np.abs(pred[safe]-obs[safe]);report=dict(native_projection_estimate=True,body_sample_count=int(safe.sum()),mean_abs_error=float(err.mean()),median_abs_error=float(np.median(err)),p90_abs_error=float(np.percentile(err,90)),density_scale=.5,omissions=['Native bloom','Sparse cleavage','Density noise','Antialiasing']);(R/'native_calibration.json').write_text(json.dumps(report,indent=2));print(report)
shape=(*xs.shape,3);a=np.uint8(np.clip(obs.reshape(shape),0,1)*255);b=np.uint8(np.clip(pred.reshape(shape),0,1)*255);e=np.uint8(np.clip(abs(pred-obs).reshape(shape)*3,0,1)*255);Image.fromarray(np.concatenate([a,b,e],axis=1)).save(R/'native_calibration.png')
