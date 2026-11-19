from pathlib import Path
import numpy as np,json,shutil
from PIL import Image
from scipy.ndimage import gaussian_filter,map_coordinates
D=Path(__file__).resolve().parent;W=D.parent;A=W/'AQ_source_growth';C=W/'AR_core_fibers';C.mkdir(exist_ok=True);R=W/'final_fibers/resources/raw_plank_wall';box=(1740,2480,2000,2720)
n=np.asarray(Image.open(next(R.glob('*nor_gl_4k*'))).convert('RGB').crop(box),dtype='float32')/127.5-1;z=np.maximum(n[:,:,2],.2);gx=-n[:,:,0]/z;gy=n[:,:,1]/z;photo=np.asarray(Image.open(next(R.glob('*diff_4k*'))).convert('RGB').crop(box),dtype='float32')/255;void=photo@np.array([.2126,.7152,.0722],dtype='float32')<.27
for a in [gx,gy]:
 a[void]=np.median(a[~void])
 for _ in range(500):
  avg=(np.roll(a,1,0)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1))*.25;a[void]=avg[void]
hs,ws=gx.shape;fx=2*np.pi*np.fft.fftfreq(ws)[None,:];fy=2*np.pi*np.fft.fftfreq(hs)[:,None];den=fx*fx+fy*fy;den[0,0]=1;integrated=np.fft.ifft2((-1j*fx*np.fft.fft2(gx)-1j*fy*np.fft.fft2(gy))/den).real.astype('float32');band=gaussian_filter(integrated,.65)-gaussian_filter(integrated,3.5)
s=np.load(A/'master_height.npz');H=s['height'];h,w=H.shape;dx,dy=5.1/(w-1),1.3775/(h-1);X,Y=np.meshgrid(np.linspace(-2.55,2.55,w,dtype='float32'),np.linspace(-.84,-2.2175,h,dtype='float32'));cu=1864+(X+1.31)/.145*80-box[0];cv=2596-(Y+1.35)/.17*65-box[1];sample=map_coordinates(band,[cv,cu],order=1,mode='nearest');mask=np.load(A/'normal_masks.npz')['core'];healthy=1-map_coordinates(gaussian_filter(void.astype('float32'),1.5),[cv,cu],order=1,mode='nearest');sample/=max(float(np.std(sample[(mask>.7)&(healthy>.9)])),1e-8);fine=np.clip(sample,-2.3,2.3)*.00028*mask*healthy
# New source band replaces the previously unresolved fine scale; physical mesh is identical.
full=np.minimum(H+fine,0);np.savez_compressed(C/'master_height.npz',height=full,delta=s['delta']+full-H)
for name in ['surface.npz','geometry.blend','normal_frames.npz','albedo.png','roughness.png','normal_masks.npz','validation.json']:shutil.copy2(A/name,C/name)
np.savez_compressed(D/'source_normal_fibers.npz',source_integrated=integrated,source_band=band,addition=fine)
d=json.loads((A/'design.json').read_text());d.update(source='AQ with actual cached normal assisted fine endgrain band; same geometry, albedo and roughness',core_fine_source='raw_plank_wall OpenGL normal, healthy source excludes pith hole',fine_height_rms=.00028,source_normal_crop=box,geometry_identical_to='AQ_source_growth',normal_strength=1.0,height_min=float(full.min()));(C/'design.json').write_text(json.dumps(d,indent=2));print('Prepared fine normal source control',flush=True)
