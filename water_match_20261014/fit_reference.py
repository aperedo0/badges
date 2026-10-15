"""Fit separate material atlases against measured Home lighting, without shared-layer ghosts."""
from pathlib import Path
import json,sys,numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,distance_transform_edt,binary_dilation,map_coordinates,maximum_filter
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));from solve import project,sample,inverse,encode,agx,agx_inv
SIZE=512;TEMP=Path('/tmp/achievement_coins_20261014')
def water_inverse(target):
    # Preserve cyan chroma when the display transform cannot reproduce both
    # the reference's saturation and its highest luminance simultaneously.
    lin=np.clip(agx_inv(target),2**-12,64.);best=lin.copy();best_error=np.full(len(target),np.inf)
    cyan=(target[:,1]>target[:,0]*1.35)&(target[:,2]>target[:,0]*1.5)
    weights=np.ones_like(target);weights[cyan,0]=3.
    for _ in range(16):
        value=agx(lin);error=target-value;cost=(error*error*weights).sum(-1)
        take=cost<best_error;best[take]=lin[take];best_error=np.minimum(cost,best_error)
        jac=np.empty((len(target),3,3))
        for c in range(3):
            changed=lin.copy();changed[:,c]*=1.035;jac[:,:,c]=(agx(changed)-value)/np.log(1.035)
        lhs=np.einsum('...ji,...j,...jk->...ik',jac,weights,jac)+np.eye(3)*.00003
        rhs=np.einsum('...ji,...j,...j->...i',jac,weights,error)
        delta=np.linalg.solve(lhs,rhs);lin=np.clip(lin*np.exp(np.clip(delta,-.7,.7)),2**-12,64.)
    return best

def raster(name):
 b=ROOT/name;m=json.loads((b/'design.json').read_text());a=np.load(b/'reliefs.npz');layers={}
 groups=[]
 for i,f in enumerate(m['features']):groups.append((f['role'],a[f'{i}_points'],a[f'{i}_triangles'][:f['front_count']]))
 shell=np.load(ROOT/'shell_geometry.npz')
 for role in ['face','bevel','inner']:
  take=(shell['roles']==role)&(shell['normals'].mean(1)[:,2]>.05)
  groups.append(('shell_'+role,shell['points'],shell['triangles'][take]))
 for role,points,triangles in groups:
  layer=layers.setdefault(role,{'cover':np.zeros((SIZE,SIZE),bool),'pos':np.zeros((SIZE,SIZE,3))})
  cover,pos=layer['cover'],layer['pos']
  for tri in points[triangles]:
   uv=(tri[:,:2]+3.015)/6.03;px=np.c_[uv[:,0]*SIZE-.5,(1-uv[:,1])*SIZE-.5]
   lo=np.maximum(np.floor(px.min(0)).astype(int),0);hi=np.minimum(np.ceil(px.max(0)).astype(int),SIZE-1)
   gx,gy=np.meshgrid(np.arange(lo[0],hi[0]+1),np.arange(lo[1],hi[1]+1));e1,e2=px[1]-px[0],px[2]-px[0];den=np.cross(e1,e2)
   if abs(den)<1e-9:continue
   u=((gx-px[0,0])*e2[1]-(gy-px[0,1])*e2[0])/den;v=(e1[0]*(gy-px[0,1])-e1[1]*(gx-px[0,0]))/den
   keep=(u>=-1e-4)&(v>=-1e-4)&(u+v<=1.0001)
   if not keep.any():continue
   x,y=gx[keep],gy[keep];p=(1-u[keep]-v[keep])[:,None]*tri[0]+u[keep,None]*tri[1]+v[keep,None]*tri[2]
   take=(~cover[y,x])|(p[:,2]>=pos[y,x,2]);x,y,p=x[take],y[take],p[take];cover[y,x]=True;pos[y,x]=p
 return m,layers

def fill(image,valid,iterations=60):
 _,(y,x)=distance_transform_edt(~valid,return_indices=True);out=image[y,x].copy()
 missing=~valid
 for _ in range(iterations):
  smooth=gaussian_filter(out,(1,1,0));out[missing]=smooth[missing]
 return out

def solve(name,calibration_name=None):
 m,layers=raster(name);b=ROOT/name;ref=np.asarray(Image.open(m['reference']).convert('RGB'),float)/255
 ref=gaussian_filter(ref,(1.2,1.2,0));calib=np.asarray(Image.open(TEMP/'water_standard_cal.png').convert('RGB'),float)/255
 yy,xx=np.indices((SIZE,SIZE));wx=(xx+.5)/SIZE*6.03-3.015;wy=3.015-(yy+.5)/SIZE*6.03;cx,cy,r=m['circle']
 target=sample(ref,cx+wx*r/3.015,cy-wy*r/3.015)
 global_z=np.full((SIZE,SIZE),-100.)
 for l in layers.values():global_z[l['cover']]=np.maximum(global_z[l['cover']],l['pos'][l['cover'],2])
 for role,layer in layers.items():
  cover,pos=layer['cover'],layer['pos'];visible=cover&(pos[:,:,2]>=global_z-.002)
  # Fill regions hidden by other solids, rather than painting those solids twice.
  role_target=target.copy()
  if role.startswith('shell_'):
   radius=np.sqrt(wx*wx+wy*wy)
   mapped=np.interp(radius,[2.420,2.485,2.945,3.015],[2.640,2.710,2.910,2.965])
   role_target=sample(ref,cx+wx*mapped/np.maximum(radius,1e-6)*r/3.015,cy-wy*mapped/np.maximum(radius,1e-6)*r/3.015)
  if role in ['background','emerald_background','glass']:
   blocked=cover&~visible;blocked=binary_dilation(blocked,iterations=6)
   if role=='emerald_background':blocked|=(target[:,:,0]>target[:,:,1]*1.18)&cover
   valid=cover&~blocked
   role_target=fill(target,valid)
  screen=project(pos[cover]);observed=sample(calib,screen[:,0]-.5,screen[:,1]-.5)
  light=np.zeros((SIZE,SIZE,3));light[cover]=np.clip(inverse(observed)/.15,.002,150.)
  # Calibrated pixels near boundaries blend the stage or another surface.
  dist=distance_transform_edt(visible);threshold=np.clip(maximum_filter(dist,size=11)*.6,.8,3.2);inner=visible&(dist>=threshold)
  if inner.sum()<8:inner=visible
  light=fill(light,inner,12)
  distance=distance_transform_edt(cover);border=cover&(distance<np.clip(maximum_filter(distance,size=11)*.6,.8,3.2))
  valid=cover&~border
  continued=fill(role_target,valid,18);role_target[border]=continued[border]
  # Lower a highlight only on the silhouette's outermost texels.
  role_target[border]=np.minimum(role_target[border],.88)
  desired=(water_inverse if role=='water' else inverse)(np.clip(role_target[cover],.012,.96));scale=.03125 if role=='background' else 1.
  albedo=np.clip(desired/np.maximum(light[cover],1e-6),0,scale)
  emission=np.clip(desired-albedo*light[cover],0,16.)/16.
  color=np.zeros((SIZE,SIZE,3));glow=color.copy();color[cover]=albedo/scale;glow[cover]=emission
  color=fill(color,cover,8);glow=fill(glow,cover,8)
  Image.fromarray(encode(color)).save(b/'textures'/(role+'_color.png'))
  Image.fromarray(encode(glow)).save(b/'textures'/(role+'_emission.png'))
  print(name,role,cover.sum(),'fitted texels',flush=True)
if __name__=='__main__':
 for name in sys.argv[1:]:solve(name,'hourglass_teal' if name=='hourglass_gold' else None)
