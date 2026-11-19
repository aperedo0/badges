from pathlib import Path
import numpy as np,json,shutil
from PIL import Image
from scipy.ndimage import gaussian_filter,map_coordinates
D=Path(__file__).resolve().parent;W=D.parent;V=W/'V_lookdev_refinement';U=W/'U_scan_fibers';Ycase=W/'Y_broken_lamina';fullY=np.load(Ycase/'master_height.npz')['height'].astype(float);base=np.load(U/'master_height.npz')['height'].astype(float);geo=np.load(U/'surface.npz')['height'].astype(float);layers=np.load(D/'structure_layers.npz');h,w=base.shape;dx,dy=5.1/(w-1),1.3775/(h-1);X,Y=np.meshgrid(np.linspace(-2.55,2.55,w),np.linspace(-.84,-2.2175,h));kx,ky=-1.31,-1.35;core=layers['core'].astype(float);plate=layers['plate'].astype(float)

def ss(a,b,v):
 q=np.clip((v-a)/(b-a),0,1);return q*q*(3-2*q)
def load(asset,role):
 pat={'height':'*disp_4k*','color':'*diff_4k*','rough':'*rough_2k*'}[role];im=Image.open(next((D/'resources'/asset).glob(pat)));return im
# Actual broken fiber surface, avoiding the scan's board seams and metal fasteners.
box=(1760,860,1900,1580);im=load('medieval_wood','height').crop(box).transpose(Image.Transpose.ROTATE_270).resize((w,h),Image.Resampling.BICUBIC);height=np.asarray(im,float);height=(height-np.mean(height))/max(np.std(height),1e-8)
band=gaussian_filter(height,(.0020/dy,.006/dx))-gaussian_filter(height,(.032/dy,.13/dx));band=np.clip(band/max(np.std(band),1e-8),-2.6,2.6)
flowY=Y-.145*np.tanh((Y-ky)/.115)*np.exp(-((X-kx)/.44)**2)
def flow(a):return map_coordinates(a,[(flowY+.84)/-1.3775*(h-1),(X+2.55)/5.1*(w-1)],order=1,mode='reflect')
relief=.0017*flow(band)*plate
# Natural knot detail is mapped only into the existing core. Broad source shape is removed.
source=np.asarray(load('raw_plank_wall','height'),float);cu=1864+(X-kx)/.145*38;cv=2596-(Y-ky)/.17*29;sample=map_coordinates(source,[cv,cu],order=1,mode='nearest');sample=gaussian_filter(sample,(.002/dy,.002/dx))-gaussian_filter(sample,(.024/dy,.024/dx));sample/=max(np.std(sample[core>.8]),1e-8);core_relief=.0023*np.clip(sample,-2.4,2.4)
R=np.load(W/'R_layers_full/master_height.npz')['height'].astype(float);oldadd=base-R;check=np.load(W/'surface_fibers/surface_layers.npz')['central_check'].astype(float);coretarget=base+core_relief+.18*check
# Keep the selected knot core level and its successful silhouette; replace the pressed interior.
coretarget-=gaussian_filter(coretarget-base,(.025/dy,.025/dx));full=fullY+relief;full=full*(1-core)+coretarget*core;full=np.minimum(full,0);delta=full-base;geometry=np.minimum(geo+gaussian_filter(delta,(.0038/dy,.0038/dx)),0)
# Independent reflectance maps from the same physical source region, with broad illumination removed.
rgb0=np.asarray(Image.open(V/'albedo.png').convert('RGB'),float)[16:-16,16:-16]/255;rough0=np.asarray(Image.open(V/'roughness.png').convert('L'),float)[16:-16,16:-16]/255
photo=np.asarray(load('medieval_wood','color').convert('RGB').crop(box).transpose(Image.Transpose.ROTATE_270).resize((w,h),Image.Resampling.BICUBIC),float)/255;lum=photo@np.array([.2126,.7152,.0722]);log=np.log(np.maximum(lum,.025));p=flow(gaussian_filter(log,(.003/dy,.008/dx))-gaussian_filter(log,(.06/dy,.23/dx)));p=np.clip(p/max(np.std(p),1e-8),-2.0,2.0)
# Reddish chestnut, amber fibers and darker growth pigment. Never a painted light direction.
pigment=np.exp(.13*p-.5*.13**2);rich=rgb0*pigment[:,:,None];wide=flow(gaussian_filter(lum,(.08/dy,.35/dx)));wide=(wide-np.median(wide))/max(np.std(wide),1e-8);stain=np.clip(-wide*.05,0,.13);rich*=1-stain[:,:,None]
rich[:,:,1]*=1-.025*np.clip(-p,0,2);rich[:,:,2]*=1-.05*np.clip(-p,0,2)
# Compressed intrinsic pigment in the core, taken from the actual knot, not its relief map.
rawcolor=np.asarray(load('raw_plank_wall','color').convert('RGB'),float)/255;cl=rawcolor@np.array([.2126,.7152,.0722]);clog=np.log(np.maximum(cl,.025));cband=gaussian_filter(clog,.8)-gaussian_filter(clog,5.5);cp=map_coordinates(cband,[cv,cu],order=1,mode='nearest');cp=np.clip((cp-np.mean(cp[core>.8]))/max(np.std(cp[core>.8]),1e-8),-2,2);knotpig=np.exp(.16*cp-.5*.16**2);rich=rich*(1-core[:,:,None])+rgb0*knotpig[:,:,None]*core[:,:,None]
rimrough=np.asarray(load('medieval_wood','rough').crop(tuple(v//2 for v in box)).transpose(Image.Transpose.ROTATE_270).resize((w,h),Image.Resampling.BICUBIC),float)/255;rr=flow(rimrough);rr=(rr-gaussian_filter(rr,(.035/dy,.13/dx)))/max(np.std(rr),1e-8);rough=np.clip(rough0+.035*np.clip(rr,-1.5,1.5)-.018*np.clip(p,0,1.5),.50,.82)
for key,mat in [('Z_scan_structure',False),('AA_rich_fibers',True)]:
 C=W/key;C.mkdir(exist_ok=True);np.savez_compressed(C/'surface.npz',height=geometry.astype('float32'));np.savez_compressed(C/'master_height.npz',height=full.astype('float32'),delta=delta.astype('float32'))
 def save(name,a):
  a=np.pad(a,((16,16),(16,16))+(((0,0),) if a.ndim==3 else ()),mode='edge');Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).save(C/name)
 if mat:save('albedo.png',rich);save('roughness.png',rough)
 else:
  for role in ['albedo','roughness']:shutil.copy2(V/(role+'.png'),C/(role+'.png'))
 (C/'design.json').write_text(json.dumps(dict(source='Preserved V anatomy with flow guided broken fiber layers, real weathered fiber microstructure and a natural knot core',geometry_shared_between_Z_and_AA=True,body_source='Poly Haven medieval_wood CC0',body_crop_4k=box,knot_source='Poly Haven raw_plank_wall CC0',core_center=[kx,ky],core_size_preserved=True,knot_source_center=[1864,2596],knot_source_radii=[38,29],fiber_rms=.0017,core_rms=.0023,material='V unchanged' if not mat else 'Independent intrinsic scanned pigment and roughness; no baked directional light',normal_split=.0038,height_min=float(full.min())),indent=2))
np.savez_compressed(D/'scan_hybrid_layers.npz',body=relief.astype('float32'),core=core_relief.astype('float32'),pigment=p.astype('float32'),core_pigment=cp.astype('float32'))
print('Prepared shared structure and independent material control',flush=True)
