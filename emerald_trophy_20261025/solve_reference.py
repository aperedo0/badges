"""Fit reference detail maps to measured light on the actual app sculpture."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,gaussian_filter,distance_transform_edt
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'silver2_metal_claude'))
from agx import agx,agx_inv
R=Path(__file__).resolve().parent;C=R/'candidate05';D=np.load('/tmp/emerald_trophy_20261025/reference_relief.npz')
N=1024;S=2.42/490
ty,tx=np.mgrid[:N,:N];wx=((tx+.5)/N-.5)*6.03;wy=(.5-(ty+.5)/N)*6.03
rx=627+wx/S;ry=590-wy/S
coords=[ry,rx]
def sample(a,coords=coords):
 return map_coordinates(a,coords,order=1,mode='nearest')
mask=sample(D['mask'].astype(float))>.4;gem=sample(D['gem_mask'].astype(float))>.4
height=sample(D['height']);valid=mask|gem
# Use the actual facet plane depth when projecting a gemstone texel into the calibration capture.
for g in range(2):
 p=D['gem'+str(g)+'_points'];t=D['gem'+str(g)+'_triangles']
 for q in p[t]:
  a=q[1,:2]-q[0,:2];b=q[2,:2]-q[0,:2];det=a[0]*b[1]-a[1]*b[0]
  u=((wx-q[0,0])*b[1]-(wy-q[0,1])*b[0])/det;v=(a[0]*(wy-q[0,1])-a[1]*(wx-q[0,0]))/det
  inside=(u>=-1e-5)&(v>=-1e-5)&(u+v<=1.00001)
  height[inside]=(q[0,2]+u*(q[1,2]-q[0,2])+v*(q[2,2]-q[0,2]))[inside]
cam=np.array([0,1.8,23.]);target=np.array([0,-.55,0]);f=target-cam;f/=np.linalg.norm(f);right=np.cross(f,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,f)
world=np.stack([wx*.96,wy*.96+.4394,height*.96],-1);delta=world-cam;depth=delta@f
screen=np.stack([540+2250*(delta@right)/depth,720-2250*(delta@up)/depth],-1)*47/60+[180,70]
cal=np.asarray(Image.open(C/'app_calibration.png').convert('RGB'),float)/255
obs=np.stack([sample(cal[...,c],[screen[...,1]-.5,screen[...,0]-.5]) for c in range(3)],-1)
# Invert the same AgX transform as the app, including its color channel coupling.
def invert(target):
 lin=np.maximum(agx_inv(target),1e-6)
 for i in range(10):
  now=agx(lin);err=target-now;h=lin*.015+1e-5
  columns=[]
  for c in range(3):
   q=lin.copy();q[:,c]+=h[:,c];columns.append((agx(q)-now)/h[:,c,None])
  jac=np.stack(columns,-1)+np.eye(3)[None]*1e-5
  change=np.linalg.solve(jac,err[...,None])[...,0]
  change=np.clip(change,-lin*.55,lin*.80+.01)
  lin=np.clip(lin+change*.8,1e-6,24)
 return lin
# Edge samples mix the badge with its field. Obtain their light from the closest clean interior.
dist=distance_transform_edt(valid);inside=valid&(dist>2.0)&(obs.max(-1)<.985)
_,nearest=distance_transform_edt(~inside,return_indices=True)
light_rgb=obs.copy();light_rgb[~inside]=obs[tuple(nearest[:,~inside])]
light_rgb=np.clip(light_rgb,.015,.98)
light=np.zeros_like(light_rgb);light[valid]=invert(light_rgb[valid])/.502886458
for c in range(3):
 num=gaussian_filter(light[...,c]*valid,.65);den=gaussian_filter(valid.astype(float),.65)
 light[...,c]=num/np.maximum(den,1e-6)
reference=np.asarray(Image.open(C/'target_reference.png').convert('RGB'),float)/255
# Preserve the reference's hue and fine marks; gently contain the highest highlight cores.
reference=np.minimum(reference,.965)
linear=np.zeros_like(reference);linear[valid]=invert(reference[valid])
# Solve color first. Emission supplies only what the measured studio light cannot provide.
albedo=np.clip(linear/np.maximum(light,1e-5),.001,1)
emission=np.clip(linear-albedo*light,0,8)
# Extend each surface color into the atlas padding so mipmaps never sample a green fringe.
_,nearest=distance_transform_edt(~valid,return_indices=True)
for tex in [albedo,emission]:tex[~valid]=tex[tuple(nearest[:,~valid])]
def encode(a):return np.uint8(np.clip(np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)*255+.5,0,255))
Image.fromarray(encode(albedo)).save(C/'textures/relief_color.png')
Image.fromarray(encode(emission/8)).save(C/'textures/relief_emission.png')
np.savez_compressed(C/'light_solution.npz',light=light,linear=linear,valid=valid,height=height,screen=screen,albedo=albedo,emission=emission)
summary={'measured_app_light':True,'reference_contours':True,'interior_samples':int(inside.sum()),'relief_texels':int(valid.sum()),
 'target_display_max':float(reference[valid].max()),'emission_scale':8,'albedo_mean':albedo[valid].mean(0).tolist(),
 'emission_mean':emission[valid].mean(0).tolist(),'predicted_error':float(abs(agx((albedo*light+emission)[valid])-reference[valid]).mean())}
(C/'material_fit.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
