"""Fit the metal contribution using the actual native studio capture."""
from pathlib import Path
import sys,json,numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,distance_transform_edt
from pace import work
work(1)
ROOT=Path(__file__).resolve().parent;R=ROOT/sys.argv[1];C=R/(R/'candidate.txt').read_text().strip();cfg=json.loads((R/'design.json').read_text());meta=json.loads((C/'finish.json').read_text());atlas=np.load(C/'atlas.npz')
sys.path.insert(0,str(ROOT.parent/'stair_ruby_20261029'))
from display_transform import agx,agx_inv
screen=np.asarray(Image.open(C/'review/calibration.png').convert('RGB'),float)/255
assert screen[297:817,343:863].std(axis=(0,1)).max()>.015
def encode(a):return np.uint8(np.clip(np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)*255+.5,0,255))
def inverse(goal):
 linear=np.maximum(agx_inv(goal),1e-6)
 for _ in range(9):
  now=agx(linear);h=linear*.015+1e-5;columns=[]
  for j in range(3):q=linear.copy();q[:,j]+=h[:,j];columns.append((agx(q)-now)/h[:,j,None])
  jac=np.stack(columns,-1)+np.eye(3)[None]*1e-5;delta=np.linalg.solve(jac,(goal-now)[...,None])[...,0]
  linear=np.clip(linear+np.clip(delta,-linear*.55,linear*.8+.01)*.8,1e-6,16)
 return linear
N=atlas['height'].shape[0];yy,xx=np.mgrid[:N,:N];W,H=cfg['reference_size'];rx=(xx+.5)*W/N;ry=(yy+.5)*H/N
height=np.maximum(atlas['height'],0);world=np.stack([(rx-cfg['reference_center_x'])*cfg['scale'],3.015-(ry-cfg['reference_top'])*cfg['scale'],height],-1)
camera=np.array([0,1.8,23.]);forward=np.array([0,-.55,0])-camera;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,1,0]);up=np.cross(right,forward);delta=world-camera;depth=delta@forward
projected=np.stack([540+2250*(delta@right)/depth,720-2250*(delta@up)/depth],-1)*47/60+[180,70]
observed=np.stack([map_coordinates(screen[...,j],[projected[...,1]-.5,projected[...,0]-.5],order=1,mode='nearest') for j in range(3)],-1)
summary={}
for role in cfg['metal_roles']:
 d=np.load(C/('metal_'+role+'.npz'));valid=d['valid'];clean=valid&(distance_transform_edt(valid)>7)&(observed.max(-1)<.98)
 assert clean.any(),role
 measured=np.zeros_like(observed);pixels=np.flatnonzero(clean)
 for start in range(0,len(pixels),50000):
  ids=pixels[start:start+50000];measured.reshape(-1,3)[ids]=inverse(np.clip(observed.reshape(-1,3)[ids],.001,.98))/.05
 _,nearest=distance_transform_edt(~clean,return_indices=True);measured[~clean]=measured[tuple(nearest[:,~clean])]
 ratio=np.clip(.78*np.min(d['target']/np.maximum(measured,1e-8),axis=-1),0,1)
 color=d['desired']*ratio[...,None];emission=np.maximum(0,d['target']-measured*ratio[...,None])
 _,nearest=distance_transform_edt(~valid,return_indices=True)
 for array in [color,emission]:array[~valid]=array[tuple(nearest[:,~valid])]
 Image.fromarray(encode(color)).save(C/'textures'/(role+'_color.png'));Image.fromarray(encode(emission/8)).save(C/'textures'/(role+'_emission.png'))
 summary[role]=dict(clean_samples=int(clean.sum()),mean_physical_reflectance_factor=float(ratio[valid].mean()))
meta.update(mode='fitted',native_studio_measured=True,fit=summary);(C/'finish.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(summary),flush=True)
