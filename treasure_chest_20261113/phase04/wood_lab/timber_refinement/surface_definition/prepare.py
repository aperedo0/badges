from pathlib import Path
import json,numpy as np,shutil
from PIL import Image
from scipy.ndimage import gaussian_filter,map_coordinates,zoom
D=Path(__file__).resolve().parent;W=D.parent;A=W/'AE_controlled_fibers';OLD=W/'final_fibers'
H0=np.load(A/'master_height.npz')['height'].astype('float32');G0=np.load(A/'surface.npz')['height'].astype('float32');h,w=1472,4032;dx,dy=5.1/(w-1),1.3775/(h-1)
def resize(a,wh=(w,h)):
 return np.asarray(Image.fromarray(a.astype('float32')).resize(wh,Image.Resampling.BICUBIC),dtype='float32').copy()
def ss(a,b,v):q=np.clip((v-a)/(b-a),0,1);return q*q*(3-2*q)
H=resize(H0);X,Y=np.meshgrid(np.linspace(-2.55,2.55,w,dtype='float32'),np.linspace(-.84,-2.2175,h,dtype='float32'));kx,ky=-1.31,-1.35
M=np.load(W/'grain_hierarchy/detail_layers.npz');medium=resize(M['medium']+M['knot']);cuts=-resize(M['fractures']);core=1-ss(.76,1.10,np.hypot((X-kx)/.145,(Y-ky)/.17));plate=(1-ss(.003,.014,-medium))*(1-ss(.001,.012,cuts))*(1-core)
angle=resize(np.load(OLD/'broken_fiber_layers.npz')['angle']);rng=np.random.default_rng(161143)
density=gaussian_filter(rng.normal(size=(184,504)).astype('float32'),(4,7));density=resize(density);density=ss(np.percentile(density,20),np.percentile(density,80),density)*.7+.3
fibers=np.zeros((h,w),dtype='float32');exposed=np.zeros_like(fibers);micro=np.zeros_like(fibers)
def value(a,x,y):
 ix=int(np.clip((x+2.55)/dx,0,w-1));iy=int(np.clip((-.84-y)/dy,0,h-1));return float(a[iy,ix])
def ribbon(cx,cy,length,width,amp,dest):
 phi=value(angle,cx,cy);co,si=np.cos(phi),np.sin(phi);rx=length*abs(co)+width*abs(si)*2;ry=length*abs(si)+width*2
 x0=max(0,int((cx-rx+2.55)/dx));x1=min(w,int((cx+rx+2.55)/dx)+2);y0=max(0,int((-.84-cy-ry)/dy));y1=min(h,int((-.84-cy+ry)/dy)+2)
 if x1<=x0 or y1<=y0:return
 xx=X[y0:y1,x0:x1]-cx;yy=Y[y0:y1,x0:x1]-cy;s=(xx*co+yy*si)/length;t=(-xx*si+yy*co)/width
 phase=rng.uniform(0,6.28);t-=.10*np.sin(s*5+phase)+.07*np.sin(s*13+phase);t/=1+.16*np.sin(s*4+phase)
 # A short torn wall, a flat sloping fiber face, and a shallow worn shoulder.
 cross=np.where(t<-.65,np.clip((t+1)/.35,0,1),np.where(t<.45,1-.28*(t+.65)/1.10,np.clip((1-t)/.55,0,1)*.72))
 ends=np.clip((s+1+.13*t)/.10,0,1)*np.clip((1-s-.08*t)/.22,0,1);z=amp*cross*ends
 dest[y0:y1,x0:x1]=np.maximum(dest[y0:y1,x0:x1],z)
for count,lr,wr,ar,dest in [(1800,(.018,.070),(.0025,.0065),(.0007,.0021),fibers),(2600,(.007,.032),(.0009,.0023),(.00025,.00075),micro)]:
 n=0
 while n<count:
  cx=rng.uniform(-2.30,2.30);cy=rng.uniform(-2.10,-.92)
  if value(plate,cx,cy)<.62 or rng.random()>value(density,cx,cy):continue
  ribbon(cx,cy,rng.uniform(*lr),rng.uniform(*wr),rng.uniform(*ar),dest);n+=1
# Replace the soft fine band only on the raised interior faces. All medium anatomy and fractures remain.
oldfine=H-gaussian_filter(H,(.0035/dy,.010/dx));detail=fibers+micro;detail-=gaussian_filter(detail,(.018/dy,.065/dx));detail=plate*(detail-.72*oldfine)
# Boundary constrained reconstruction of the existing core, removing the transverse trench inside it.
ix0=int((kx-.18+2.55)/dx);ix1=int((kx+.18+2.55)/dx)+1;iy0=int((-.84-(ky+.21))/dy);iy1=int((-.84-(ky-.21))/dy)+1
patch=H[iy0:iy1,ix0:ix1].copy();mask=core[iy0:iy1,ix0:ix1]>.12;fixed=patch.copy();fill=patch.copy();fill[mask]=np.median(patch[mask])
for _ in range(1700):
 avg=(np.roll(fill,1,0)+np.roll(fill,-1,0)+np.roll(fill,1,1)+np.roll(fill,-1,1))*.25;fill[mask]=avg[mask]
# Preserve mean core recession, not the inherited horizontal trench.
cm=core[iy0:iy1,ix0:ix1];fill+=np.clip(np.mean(patch[cm>.7])-np.mean(fill[cm>.7]),-.003,.003)*cm
core_target=H.copy();core_target[iy0:iy1,ix0:ix1]=fill
cells=rng.normal(size=(h,w)).astype('float32');cells=gaussian_filter(cells,(.004/dy,.002/dx))-gaussian_filter(cells,(.018/dy,.015/dx));cells/=max(float(np.std(cells[core>.6])),1e-8);cells=np.clip(cells,-2,2)*.00065
# Keep a single near vertical split at the established center with uneven opening and tapered ends.
yrel=(Y-ky)/.17;line=kx+.0025*np.sin(yrel*8)+.0015*np.sin(yrel*19);width=.0016+.0014*ss(-.5,.7,np.sin(yrel*5+.4));check=-.0085*np.exp(-((X-line)/width)**4)*(1-ss(.72,1.0,abs(yrel)))
core_delta=(core_target+cells+check-H)*core;detail+=core_delta
edge=np.minimum.reduce([2.35-abs(X),Y+2.16,-.8625-Y]);detail*=ss(.015,.07,edge);full=np.minimum(H+detail,0);delta=full-H
# Only the physically resolved part of the new detail moves the existing grid.
lo=gaussian_filter(delta,(.0038/dy,.0038/dx));geometry=np.minimum(G0+resize(lo,(H0.shape[1],H0.shape[0])),0)
np.savez_compressed(D/'layers.npz',fibers=fibers,micro=micro,plate=plate,core=core,core_delta=core_delta,delta=delta)
def image2(name):return Image.open(A/(name+'.png')).resize((4096,1536),Image.Resampling.BICUBIC)
basecolor=np.asarray(image2('albedo').convert('RGB'),dtype='float32')/255;baserough=np.asarray(image2('roughness').convert('L'),dtype='float32')/255
# Clear the old transverse pigment mark only inside the reconstructed core.
rgb=basecolor[32:-32,32:-32].copy();core_color=np.empty_like(rgb)
for c in range(3):core_color[:,:,c]=gaussian_filter(rgb[:,:,c],(.018/dy,.012/dx))
rgb=rgb*(1-core[:,:,None])+core_color*core[:,:,None];rgb*=1-core[:,:,None]*np.array([.04,.08,.07],dtype='float32')
# Endgrain pigment has independent small compressed formations, rather than painted relief shadows.
pig=gaussian_filter(rng.normal(size=(h,w)).astype('float32'),(.006/dy,.003/dx));pig/=max(float(np.std(pig[core>.6])),1e-8);rgb*=np.exp(.13*np.clip(pig,-2,2)*core)[:,:,None]
for key,rich in [('AG_fiber_facets',False),('AH_aged_fibers',True)]:
 C=W/key;C.mkdir(exist_ok=True);np.savez_compressed(C/'master_height.npz',height=full,delta=delta);np.savez_compressed(C/'surface.npz',height=geometry)
 color=basecolor.copy();rough=baserough.copy();color[32:-32,32:-32]=rgb
 if rich:
  # Fiber exposure is a property of broken wood. It has no baked light direction.
  exposure=np.clip(fibers/.0018,0,1)*plate;stain=gaussian_filter(rng.normal(size=(h,w)).astype('float32'),(.035/dy,.13/dx));stain/=max(float(np.std(stain)),1e-8);stain=np.clip(stain,-1.6,1.6)
  color[32:-32,32:-32]*=np.exp(.08*stain)[:,:,None]*np.array([.98,.94,.93],dtype='float32')
  color[32:-32,32:-32]*=1+exposure[:,:,None]*np.array([.045,.055,.025],dtype='float32')
  rough[32:-32,32:-32]=np.clip(rough[32:-32,32:-32]+.065+.025*exposure,.56,.83)
 for name,a in [('albedo',color),('roughness',rough)]:Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).save(C/(name+'.png'))
 d=dict(source='Preserved AE medium anatomy and primary fractures, finite angular fibers replacing only soft tertiary band, boundary constrained existing knot core',seed=161143,texture_size=[4096,1536],fine_fibers=2600,secondary_fibers=1800,core_center=[kx,ky],core_radii=[.145,.17],normal_split=.0038,macro_grain_and_fractures_preserved=True,material='Shared AE with localized reconstructed core' if not rich else 'Independent aged pigment, exposed broken fibers and roughness',height_min=float(full.min()))
 (C/'design.json').write_text(json.dumps(d,indent=2));print('PREPARED',key,flush=True)
(D/'STATE.json').write_text(json.dumps(dict(working=True,baseline='baseline.blend',baseline_candidate='AE_controlled_fibers',scope='Existing test plank only',next='Render controlled structure and material comparisons, inspect before selection'),indent=2))
