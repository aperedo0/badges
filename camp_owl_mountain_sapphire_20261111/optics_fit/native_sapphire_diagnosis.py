"""Compare actual uploaded facet planes and native pixels without changing optics."""
from pathlib import Path
import json,time
import numpy as np
from scipy.ndimage import binary_erosion
from PIL import Image
import forward as f
R=Path(__file__).resolve().parent;C=R.parent/'sapphire_teardrop/candidate08'
s=json.loads((R.parent/'schedule.json').read_text());assert s['phase']=='work' and time.time()+30<s['work_until_epoch']
planes=np.asarray(json.loads((C/'actual_native_planes.json').read_text())['/Badge/Gem'])
# Reconstruct the actual two row half precision upload.
hi=planes.astype(np.float16).astype(float);lo=((planes-hi)*1024).astype(np.float16).astype(float)
uploaded=hi+lo/1024;n=uploaded[:,:3];w=uploaded[:,3]
yy,xx=np.mgrid[410:764,475:731];shape=xx.shape;x=xx.ravel();y=yy.ravel()
eye=np.broadcast_to([0,1.8,23.],(len(x),3)).copy();axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
direction=f.unit(axis+(x+.5-603)[:,None]/1762.5*np.array([1,0,0])-(y+.5-633.3)[:,None]/1762.5*up)
ok,entry,_,normal,_=f.interval((n,w),eye,direction);ok&=entry>0;inside=binary_erosion(ok.reshape(shape),iterations=4).ravel();ids=np.flatnonzero(inside)
origin=eye[ids];incident=direction[ids];entry=entry[ids];normal=normal[ids]
native=np.asarray(Image.open(C/'app/front.png').convert('RGB'))[y[ids],x[ids]]/255
studio=f.Studio();gain=1.45768306077441;absorption=np.array([8,4.350359687795594,.2])*.78125
def along(d):return studio.sharp(d)+gain*np.minimum(studio.sample(d,8),3)
def trace(normal_quantized=False):
 normal_entry=normal.astype(np.float16).astype(float) if normal_quantized else normal.copy();normal_entry=f.unit(normal_entry)
 reflection=f.fresnel(-np.sum(normal_entry*incident,1),1,1.77)
 out=reflection[:,None]*studio.sharp(f.reflect(incident,normal_entry));weight=1-reflection
 pos=origin+incident*entry[:,None];d=f.refract(incident,normal_entry,1/1.77);length=np.zeros(len(ids));failed=np.zeros(len(ids),bool)
 for hit in range(3):
  approach=d@n.T;gap=w-pos@n.T;valid=(approach>1e-4)&(gap> -1e-5)
  distances=np.where(valid,np.maximum(gap,0)/np.where(valid,approach,1),np.inf);ix=distances.argmin(1);distance=distances[np.arange(len(ids)),ix];found=np.isfinite(distance);failed|=~found
  distance=np.where(found,distance,0);facet=n[ix];pos+=d*distance[:,None];length+=distance;weight_color=np.exp(-length[:,None]*absorption)
  share=f.fresnel(np.sum(facet*d,1),1.77,1);green=f.refract(d,-facet,1.77);light=[]
  for channel,index in enumerate([1.76,1.77,1.79]):
   bent=f.refract(d,-facet,index);bent=np.where((np.linalg.norm(bent,axis=1)==0)[:,None],green,bent);light.append(along(bent)[:,channel])
  out+=(weight*(1-share)*found)[:,None]*weight_color*np.stack(light,1);weight*=np.where(found,share,1);d=np.where(found[:,None],f.reflect(d,facet),d)
 out+=weight[:,None]*np.exp(-length[:,None]*absorption)*along(d)
 return np.clip(f.agx(out*.28),0,1),failed,length
pred,failed,length=trace();quant,_,_=trace(True);dark=native[:,2]<.12;selected=np.flatnonzero(dark)
rows=[]
for i in selected[:100]:rows.append(dict(pixel=[int(x[ids[i]]),int(y[ids[i]])],native=native[i].tolist(),predicted=pred[i].tolist(),normal_half_predicted=quant[i].tolist(),trace_exit_failed=bool(failed[i]),path_length=float(length[i])))
report=dict(diagnostic_only=True,geometry_and_runtime_unchanged=True,actual_uploaded_planes=len(planes),body_pixels=len(ids),native_mean_absolute_error=float(np.mean(abs(pred-native))),native_dark_pixels=int(dark.sum()),predicted_dark_pixels=int((pred[:,2]<.12).sum()),dark_pixel_mean_error=float(np.mean(abs(pred[dark]-native[dark]))) if dark.any() else None,failed_exit_rays=int(failed.sum()),maximum_path_length=float(length.max()),dark_pixel_samples=rows)
(R/'native_sapphire_diagnosis.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='dark_pixel_samples'},indent=2))
canvas=np.zeros((shape[0],shape[1],3),np.uint8);canvas.reshape(-1,3)[ids]=np.uint8(pred*255);Image.fromarray(canvas).save(R/'native_sapphire_predicted.png')
