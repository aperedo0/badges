"""Fit dynamic metal to the approved front using an actual app calibration."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,distance_transform_edt,gaussian_filter
from display_transform import agx,agx_inv
ROOT=Path(__file__).resolve().parent;key=sys.argv[1];R=ROOT/key;C=R/(R/'candidate.txt').read_text().strip()
trace=json.loads((C/'trace.json').read_text());cfg=json.loads((R/'design.json').read_text());geometry=np.load(C/'geometry.npz');meta=json.loads((C/'metal_finish.json').read_text());GAIN=meta['calibration_gain']
screen=np.asarray(Image.open(C/'app_calibration.png').convert('RGB'),float)/255
def encode(a):return np.uint8(np.clip(np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)*255+.5,0,255))
def inverse(goal):
 out=np.zeros_like(goal)
 for start in range(0,len(goal),50000):
  target=goal[start:start+50000];lin=np.maximum(agx_inv(target),1e-6)
  for i in range(9):
   now=agx(lin);h=lin*.015+1e-5;columns=[]
   for j in range(3):
    q=lin.copy();q[:,j]+=h[:,j];columns.append((agx(q)-now)/h[:,j,None])
   jac=np.stack(columns,-1)+np.eye(3)[None]*1e-5;change=np.linalg.solve(jac,(target-now)[...,None])[...,0]
   lin=np.clip(lin+np.clip(change,-lin*.55,lin*.8+.01)*.8,1e-6,16)
  out[start:start+len(lin)]=lin
 return out
camera=np.array([0,1.8,23.]);forward=np.array([0,-.55,0])-camera;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,forward)
summaries={}
for role in ['surface','star']:
 path=C/('metal_'+role+'.npz')
 if not path.exists():continue
 data=np.load(path);rx=data['rx'];ry=data['ry'];valid=data['valid'];cat=data['category'];desired=data['desired'];target=data['target'];height=map_coordinates(geometry['height'],[ry,rx],order=1,mode='nearest')
 if role=='star':
  spec=cfg['facets'][0];center=np.array(spec['center']);outline=np.array(spec['outline']);height[:]=spec['seat']
  for a,b in zip(outline,np.roll(outline,-1,axis=0)):
   aa=a-center;bb=b-center;det=aa[0]*bb[1]-aa[1]*bb[0]
   u=((rx-center[0])*bb[1]-(ry-center[1])*bb[0])/det;v=(aa[0]*(ry-center[1])-aa[1]*(rx-center[0]))/det
   inside=(u>=0)&(v>=0)&(u+v<=1);height[inside]=(spec['crest']*(1-u-v)+spec['seat']*(u+v))[inside]
 wx=(rx-trace['reference_center'][0])*trace['reference_scale'];wy=3.015-(ry-trace['reference_bounds'][0][1])*trace['reference_scale']
 world=np.stack([wx,wy,height],-1);delta=world-camera;depth=delta@forward
 projected=np.stack([540+2250*(delta@right)/depth,720-2250*(delta@up)/depth],-1)*47/60+[180,70]
 observed=np.stack([map_coordinates(screen[...,j],[projected[...,1]-.5,projected[...,0]-.5],order=1,mode='nearest') for j in range(3)],-1)
 physical=valid&(cat>0);clean=physical&(distance_transform_edt(physical)>6)&(observed.max(-1)<.985)
 measured=np.zeros_like(observed)
 measured[clean]=inverse(np.clip(observed[clean],.001,.98))/GAIN
 # Mixed edge pixels get the nearest reliable sample of the same metal.
 for category in [1,2,3]:
  interior=clean&(cat==category);region=physical&(cat==category)
  if not interior.any():continue
  _,nearest=distance_transform_edt(~interior,return_indices=True);missing=region&~interior
  measured[missing]=measured[tuple(nearest[:,missing])]
 ratio=np.minimum(1,.78*np.min(target/np.maximum(measured,1e-7),axis=-1))
 ratio=np.clip(ratio,0,1);ratio[~physical]=0
 color=desired*ratio[...,None]
 emission=np.maximum(0,target-measured*ratio[...,None])
 color[~physical]=data['approved_color'][~physical];emission[~physical]=data['approved_emission'][~physical]
 # Pad by the closest real surface, keeping texture filtering out of the background.
 _,nearest=distance_transform_edt(~valid,return_indices=True)
 for array in [color,emission]:array[~valid]=array[tuple(nearest[:,~valid])]
 Image.fromarray(encode(color)).save(C/'textures'/(role+'_color.png'));Image.fromarray(encode(emission/8)).save(C/'textures'/(role+'_emission.png'))
 np.savez_compressed(C/('metal_fit_'+role+'.npz'),measured=measured,ratio=ratio,color=color,emission=emission,physical=physical,projected=projected)
 summaries[role]={'metal_texels':int(physical.sum()),'clean_light_samples':int(clean.sum()),'mean_retained_physical_reflectance':float(ratio[physical].mean()),'roughness_metal':float(np.median(data['roughness'][physical]))}
meta.update(mode='fitted',calibrated_in_native_app=True,fit=summaries)
(C/'metal_finish.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta,indent=2))
