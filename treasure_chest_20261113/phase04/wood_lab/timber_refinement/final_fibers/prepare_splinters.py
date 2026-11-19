from pathlib import Path
import numpy as np,json,shutil
from PIL import Image
from scipy.ndimage import gaussian_filter,map_coordinates,maximum_filter
D=Path(__file__).resolve().parent;W=D.parent;V=W/'V_lookdev_refinement';U=W/'U_scan_fibers';M=np.load(W/'grain_hierarchy/detail_layers.npz');layers=np.load(D/'structure_layers.npz');base=np.load(U/'master_height.npz')['height'].astype(float);geo=np.load(U/'surface.npz')['height'].astype(float);R=np.load(W/'R_layers_full/master_height.npz')['height'].astype(float);oldadd=base-R;h,w=base.shape;dx,dy=5.1/(w-1),1.3775/(h-1);X,Y=np.meshgrid(np.linspace(-2.55,2.55,w),np.linspace(-.84,-2.2175,h));kx,ky=-1.31,-1.35

def ss(a,b,v):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
def sample(a,x,y):
 u=float(np.clip((x+2.55)/5.1*(w-1),0,w-1));v=float(np.clip((y+.84)/-1.3775*(h-1),0,h-1));ix,iy=int(u),int(v);fx,fy=u-ix,v-iy
 return a[iy,ix]*(1-fx)*(1-fy)+a[iy,min(ix+1,w-1)]*fx*(1-fy)+a[min(iy+1,h-1),ix]*(1-fx)*fy+a[min(iy+1,h-1),min(ix+1,w-1)]*fx*fy
# Local grain direction comes from the established medium anatomy, not a row pattern.
gy,gx=np.gradient(gaussian_filter(M['medium']+M['knot'],(.008/dy,.012/dx)),dy,dx);gy=-gy;jxx=gaussian_filter(gx*gx,(.045/dy,.09/dx));jyy=gaussian_filter(gy*gy,(.045/dy,.09/dx));jxy=gaussian_filter(gx*gy,(.045/dy,.09/dx));angle=.5*np.arctan2(2*jxy,jxx-jyy)+np.pi/2;angle=(angle+np.pi/2)%np.pi-np.pi/2;angle=np.clip(angle,-.85,.85);confidence=(jxx+jyy)/(jxx+jyy+.001);angle*=confidence
plate=layers['plate'].astype(float);core=layers['core'].astype(float);rng=np.random.default_rng(161123);strips=np.zeros_like(base);small=np.zeros_like(base)
def strip(cx,cy,length,width,amp,dest,core_mode=False):
 if core_mode:
  phi=rng.uniform(-.35,.35);co,si=np.cos(phi),np.sin(phi);rx,ry=width*2+length*abs(si),length+width
  ix0=max(0,int((cx-rx+2.55)/dx));ix1=min(w,int((cx+rx+2.55)/dx)+2);iy0=max(0,int((-.84-(cy+ry))/dy));iy1=min(h,int((-.84-(cy-ry))/dy)+2)
  xx=X[iy0:iy1,ix0:ix1]-cx;yy=Y[iy0:iy1,ix0:ix1]-cy;s=(yy*co+xx*si)/length;t=(xx*co-yy*si)/width
 else:
  xs=np.linspace(cx-length,cx+length,max(9,int(2*length/dx)+1));ys=np.zeros_like(xs);mid=len(xs)//2;ys[mid]=cy
  for j in range(mid+1,len(xs)):ys[j]=ys[j-1]+np.tan(float(sample(angle,xs[j-1],ys[j-1])))*(xs[j]-xs[j-1])
  for j in range(mid-1,-1,-1):ys[j]=ys[j+1]-np.tan(float(sample(angle,xs[j+1],ys[j+1])))*(xs[j+1]-xs[j])
  ix0=max(0,int((xs[0]+2.55)/dx));ix1=min(w,int((xs[-1]+2.55)/dx)+2);iy0=max(0,int((-.84-(ys.max()+width*2))/dy));iy1=min(h,int((-.84-(ys.min()-width*2))/dy)+2)
  xx=X[iy0:iy1,ix0:ix1];yy=Y[iy0:iy1,ix0:ix1];line=np.interp(xx,xs,ys);s=(xx-cx)/length;slope=np.interp(xx,xs,np.gradient(ys,xs));t=(yy-line)/np.sqrt(1+slope*slope)/width
 if ix1<=ix0 or iy1<=iy0:return
 phase=rng.uniform(0,6.28);t=t/(1+.22*np.sin(s*3.4+phase)+.1*np.sin(s*12+phase))
 # A short sharp broken edge, broad tilted wood plate and a long worn shoulder.
 enter=np.clip((s+1+.18*t)/.14,0,1);leave=np.clip((1-s+.12*t)/.29,0,1)
 cross=np.where(t<-.65,np.clip((t+1)/.35,0,1),np.where(t<.25,1-.18*(t+.65)/.9,np.clip(1-(t-.25)/1.15,0,1)*.82))
 face=enter*leave*cross*(.92+.08*s);dest[iy0:iy1,ix0:ix1]=np.maximum(dest[iy0:iy1,ix0:ix1],amp*face)
for count,lengths,widths,amps,dest in [(300,(.07,.24),(.006,.020),(.0035,.008),strips),(620,(.025,.115),(.0025,.006),(.0009,.003),small)]:
 accepted=0
 while accepted<count:
  cx=rng.uniform(-2.28,2.28);cy=rng.uniform(-2.10,-.92)
  if float(sample(plate,cx,cy))<.65:continue
  strip(cx,cy,rng.uniform(*lengths),rng.uniform(*widths),rng.uniform(*amps),dest);accepted+=1
surface=strips+.38*small;surface-=gaussian_filter(surface,(.035/dy,.13/dx));surface+=gaussian_filter(oldadd,(.035/dy,.13/dx))
# Short compressed fibers in the existing core, with no new outer ring.
core_strips=np.zeros_like(base)
for i in range(115):
 while True:
  cx=kx+rng.uniform(-.13,.13);cy=ky+rng.uniform(-.15,.15)
  if ((cx-kx)/.13)**2+((cy-ky)/.15)**2<1:break
 strip(cx,cy,rng.uniform(.010,.032),rng.uniform(.0023,.007),rng.uniform(.0012,.0045),core_strips,True)
core_surface=core_strips-gaussian_filter(core_strips,(.018/dy,.018/dx))+gaussian_filter(oldadd,(.025/dy,.025/dx))
check=np.load(W/'surface_fibers/surface_layers.npz')['central_check'].astype(float);core_surface+=1.15*check
# A broad horizontal opening crossed the core. Preserve it outside the core, soften its dominance inside.
cut=-M['fractures'].astype(float);xxmask=(abs(X-kx)>.025)&(abs(X-kx)<.115)&(abs(Y-ky)<.15);row=np.sum(cut*xxmask,axis=1);yh=float(Y[int(row.argmax()),0]);horizontal_fill=.28*cut*core*np.exp(-((Y-yh)/.024)**2)*ss(.008,.025,abs(X-kx))
# Existing small checks get shallow broken shoulders, without new centerlines.
wide=maximum_filter(cut,size=(5,3));thin=ss(.002,.006,wide)*(1-ss(.024,.038,wide));variation=np.clip(.6+.2*layers['scan'],.15,1);fracture_delta=-.26*np.maximum(wide-cut,0)*thin*variation
boundary=ss(.012,.065,np.minimum.reduce([2.35-abs(X),Y+2.16,-.8625-Y]));delta=plate*(surface-oldadd)+core*(core_surface-oldadd)*boundary+horizontal_fill+fracture_delta*boundary
full=np.minimum(base+delta,0);delta=full-base;geometry=np.minimum(geo+gaussian_filter(delta,(.0038/dy,.0038/dx)),0)
C=W/'Y_broken_lamina';C.mkdir(exist_ok=True)
np.savez_compressed(C/'surface.npz',height=geometry.astype('float32'));np.savez_compressed(C/'master_height.npz',height=full.astype('float32'),delta=delta.astype('float32'));np.savez_compressed(D/'broken_fiber_layers.npz',fibers=strips.astype('float32'),fine=small.astype('float32'),core=core_strips.astype('float32'),fracture=fracture_delta.astype('float32'),angle=angle.astype('float32'))
for role in ['albedo','roughness']:shutil.copy2(V/(role+'.png'),C/(role+'.png'))
(C/'design.json').write_text(json.dumps(dict(source='V medium anatomy; flow guided flat broken fiber plates replace the weak internal band',seed=161123,medium_fibers=300,fine_fibers=620,core_fibers=115,knot_center=[kx,ky],knot_size_preserved=True,existing_fracture_centers_preserved=True,horizontal_core_opening_y=yh,material='V unchanged for structural comparison',normal_split=.0038,height_min=float(full.min()),delta_min=float(delta.min()),delta_max=float(delta.max())),indent=2));print('Prepared flow guided fractured wood layers',flush=True)
