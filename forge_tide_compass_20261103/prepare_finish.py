"""Prepare reference fill and a native lighting calibration for real metal."""
from pathlib import Path
import sys,json,numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,distance_transform_edt,map_coordinates
from pace import work
work(2)
ROOT=Path(__file__).resolve().parent;R=ROOT/sys.argv[1];C=R/(R/'candidate.txt').read_text().strip();cfg=json.loads((R/'design.json').read_text())
sys.path.insert(0,str(ROOT.parent/'stair_ruby_20261029'))
from display_transform import agx,agx_inv
N=1024;reference=np.asarray(Image.open(R/'reference.png').convert('RGB').resize((N,N),Image.Resampling.LANCZOS),float)/255
groups=json.loads((C/'groups.json').read_text());D=np.load(C/'geometry.npz');height=np.full((N,N),-100.,float);roles=np.full((N,N),-1,np.int16)
all_roles=list(dict.fromkeys(g['role'] for g in groups));indices={name:i for i,name in enumerate(all_roles)}
S=cfg['scale'];W,H=cfg['reference_size'];CX=cfg['reference_center_x'];TOP=cfg['reference_top']
for i,g in enumerate(groups):
 p=D[str(i)+'_points'];t=D[str(i)+'_triangles'];xy=np.c_[(p[:,0]/S+CX)*N/W,(TOP+(3.015-p[:,1])/S)*N/H]
 for tri in t:
  pp=xy[tri];zz=p[tri,2]
  if zz.max()<0:continue
  a=pp[1]-pp[0];b=pp[2]-pp[0];det=np.cross(a,b)
  if abs(det)<1e-7:continue
  x0=max(0,int(np.floor(pp[:,0].min())));x1=min(N,int(np.ceil(pp[:,0].max()))+1);y0=max(0,int(np.floor(pp[:,1].min())));y1=min(N,int(np.ceil(pp[:,1].max()))+1)
  if x1<=x0 or y1<=y0:continue
  yy,xx=np.mgrid[y0:y1,x0:x1];gx=xx+.5-pp[0,0];gy=yy+.5-pp[0,1]
  u=(gx*b[1]-gy*b[0])/det;v=(a[0]*gy-a[1]*gx)/det;z=zz[0]+u*(zz[1]-zz[0])+v*(zz[2]-zz[0]);region=height[y0:y1,x0:x1]
  m=(u>=-1e-5)&(v>=-1e-5)&(u+v<=1+1e-5)&(z>region);region[m]=z[m];roles[y0:y1,x0:x1][m]=indices[g['role']]
gem_mask=np.zeros((N,N),bool)
for role,index in indices.items():
 if role.startswith('CrestGem_'):gem_mask|=roles==index
reference[gem_mask]=[.025,.035,.065]
target=np.minimum(reference.reshape(-1,3),.97);result=np.empty_like(target)
for start in range(0,len(target),50000):
 goal=target[start:start+50000];linear=np.maximum(agx_inv(goal),1e-6)
 for _ in range(9):
  now=agx(linear);h=linear*.015+1e-5;columns=[]
  for j in range(3):q=linear.copy();q[:,j]+=h[:,j];columns.append((agx(q)-now)/h[:,j,None])
  jac=np.stack(columns,-1)+np.eye(3)[None]*1e-5;delta=np.linalg.solve(jac,(goal-now)[...,None])[...,0]
  linear=np.clip(linear+np.clip(delta,-linear*.55,linear*.8+.01)*.8,1e-6,8)
 result[start:start+len(goal)]=linear
target=result.reshape(N,N,3)
def encode(a):return np.uint8(np.clip(np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)*255+.5,0,255))
metaldata={};lum=reference@np.array([.2126,.7152,.0722]);grain=gaussian_filter(lum,.8)-gaussian_filter(lum,4)
for role in cfg['textured_roles']:
 valid=roles==indices[role];assert valid.any(),role
 _,near=distance_transform_edt(~valid,return_indices=True)
 desired=np.broadcast_to(cfg.get('desired_colors',{}).get(role,[.006,.006,.006]),(N,N,3)).copy()
 desired*=1+np.clip(grain,-.15,.15)[...,None]*.18
 rough=np.clip(cfg['roughness'][role]+grain*.10,.15,.85);metal=role in cfg['metal_roles']
 color=desired*.05 if metal else np.minimum(target*.007,.009)
 emission=np.zeros_like(color) if metal else np.maximum(0,target-color*.4)
 for array in [color,emission,rough]:array[~valid]=array[tuple(near[:,~valid])]
 for suffix,array in [('color',color),('emission',emission/8)]:Image.fromarray(encode(array)).save(C/'textures'/(role+'_'+suffix+'.png'))
 Image.fromarray(np.uint8(rough*255+.5)).save(C/'textures'/(role+'_roughness.png'))
 if metal:
  desired[~valid]=desired[tuple(near[:,~valid])]
  np.savez_compressed(C/('metal_'+role+'.npz'),desired=desired,target=target,valid=valid,roughness=rough)
np.savez_compressed(C/'atlas.npz',height=height,roles=roles,gem_mask=gem_mask)
(C/'finish.json').write_text(json.dumps(dict(mode='calibration',gain=.05,roles=all_roles,texture_size=N),indent=2)+'\n')
print(cfg['name'],'finish ready for native metal measurement',flush=True)
