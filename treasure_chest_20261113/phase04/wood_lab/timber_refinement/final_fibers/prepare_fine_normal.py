from pathlib import Path
import numpy as np,json,shutil
from PIL import Image
from scipy.ndimage import gaussian_filter,map_coordinates
D=Path(__file__).resolve().parent;W=D.parent;A=W/'AB_carved_profiles';C=W/'AC_fiber_surface';C.mkdir(exist_ok=True)
for name in ['geometry.blend','normal_frames.npz','surface.npz','master_height.npz','albedo.png','roughness.png']:shutil.copy2(A/name,C/name)
h,w=np.load(A/'master_height.npz')['height'].shape;dx,dy=5.1/(w-1),1.3775/(h-1);X,Y=np.meshgrid(np.linspace(-2.55,2.55,w),np.linspace(-.84,-2.2175,h));kx,ky=-1.31,-1.35
im=Image.open(next((D/'resources/medieval_wood').glob('*nor_gl_4k*'))).convert('RGB').crop((1760,860,1900,1580)).transpose(Image.Transpose.ROTATE_270);n=np.asarray(im,float)/127.5-1;nx=n[:,:,1];ny=-n[:,:,0];nz=np.maximum(n[:,:,2],.15);gx=-nx/nz;gy=ny/nz
sh,sw=gx.shape;fx=2*np.pi*np.fft.fftfreq(sw)[None,:];fy=2*np.pi*np.fft.fftfreq(sh)[:,None];den=fx*fx+fy*fy;den[0,0]=1
height=np.fft.ifft2((-1j*fx*np.fft.fft2(gx)-1j*fy*np.fft.fft2(gy))/den).real
height-=gaussian_filter(height,(2.5,7));im=Image.fromarray(height.astype('float32')).resize((w,h),Image.Resampling.BICUBIC);height=np.asarray(im,float);flowY=Y-.145*np.tanh((Y-ky)/.115)*np.exp(-((X-kx)/.44)**2);height=map_coordinates(height,[(flowY+.84)/-1.3775*(h-1),(X+2.55)/5.1*(w-1)],order=1,mode='reflect');height=gaussian_filter(height,(.0006/dy,.001/dx));height-=gaussian_filter(height,(.009/dy,.05/dx));sy,sx=np.gradient(height,dy,dx);height*=.34/max(np.sqrt(np.mean(sy*sy+sx*sx)),1e-8)
def ss(a,b,x):q=np.clip((x-a)/(b-a),0,1);return q*q*(3-2*q)
core=np.load(D/'structure_layers.npz')['core'];cut=-np.load(W/'grain_hierarchy/detail_layers.npz')['fractures'];mask=(1-core*.85)*(1-ss(.008,.025,cut));fine=height*mask
# The core has compressed short endgrain cells with a preferred vertical direction.
rng=np.random.default_rng(112316);noise=rng.normal(size=(h,w));cells=gaussian_filter(noise,(.006/dy,.002/dx))-gaussian_filter(noise,(.022/dy,.012/dx));sy,sx=np.gradient(cells,dy,dx);cells*=.26/max(np.sqrt(np.mean((sy*sy+sx*sx)[core>.5])),1e-8);fine+=cells*core
edge=np.minimum.reduce([2.35-abs(X),Y+2.16,-.8625-Y]);fine*=ss(.015,.07,edge)
np.savez_compressed(C/'fine_height.npz',height=fine.astype('float32'))
# More independent intrinsic fine pigment. No normal derived shading is painted.
photo=np.asarray(Image.open(next((D/'resources/medieval_wood').glob('*diff_4k*'))).convert('RGB').crop((1760,860,1900,1580)).transpose(Image.Transpose.ROTATE_270).resize((w,h),Image.Resampling.BICUBIC),float)/255;lum=np.maximum(photo@np.array([.2126,.7152,.0722]),.02);p=np.log(lum);p=p-gaussian_filter(p,(.018/dy,.075/dx));p=map_coordinates(p,[(flowY+.84)/-1.3775*(h-1),(X+2.55)/5.1*(w-1)],order=1,mode='reflect');p=np.clip(p/max(np.std(p),1e-8),-2.5,2.5);pig=.13*p*mask+.09*cells/max(np.std(cells[core>.5]),1e-8)*core
rgb=np.asarray(Image.open(A/'albedo.png').convert('RGB'),float)/255;rgb[16:-16,16:-16]*=np.exp(pig[:,:,None]-.5*.13**2);Image.fromarray(np.uint8(np.clip(rgb,0,1)*255+.5)).save(C/'albedo.png')
d=json.loads((A/'design.json').read_text());d.update(source='AB structure with scanned fine tangent relief absent from displacement source',fine_normal_source='medieval_wood 4k OpenGL normal CC0',normal_slope_rms=.34,geometry='AB identical',fine_height_min=float(fine.min()),fine_height_max=float(fine.max()));(C/'design.json').write_text(json.dumps(d,indent=2));print('Prepared fine surface',d['fine_height_min'],d['fine_height_max'])
