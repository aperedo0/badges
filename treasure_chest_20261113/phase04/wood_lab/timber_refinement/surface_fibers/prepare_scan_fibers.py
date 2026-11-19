from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import gaussian_filter,map_coordinates
D=Path(__file__).resolve().parent;W=D.parent;P=W.parent;L=np.load(D/'surface_layers.npz');M=np.load(W/'grain_hierarchy/detail_layers.npz')
base=L['base'].astype(float);h,w=base.shape;dx,dy=5.1/(w-1),1.3775/(h-1);X,Y=np.meshgrid(np.linspace(-2.55,2.55,w),np.linspace(-.84,-2.2175,h));kx,ky=-1.31,-1.35;rx=X-kx;ry=Y-ky
raw=Image.open(P/'resources/rough_wood/rough_wood_nor_gl_2k.png').convert('RGB').crop((500,0,1000,2048)).transpose(Image.Transpose.ROTATE_270).resize((w,h),Image.Resampling.BICUBIC)
n=np.asarray(raw,float)/127.5-1
# Rotate the tangent basis with the image: new right is old up, new up old left.
nx=n[:,:,1];ny=-n[:,:,0];nz=np.maximum(n[:,:,2],.15)
gradx=-nx/nz;grady=ny/nz
# Integrate the cached normal's coherent fine relief, not its photographed pigment.
fx=2*np.pi*np.fft.fftfreq(w,d=dx)[None,:];fy=2*np.pi*np.fft.fftfreq(h,d=dy)[:,None];den=fx*fx+fy*fy;den[0,0]=1
integrated=np.fft.ifft2((-1j*fx*np.fft.fft2(gradx)-1j*fy*np.fft.fft2(grady))/den).real
fibers=gaussian_filter(integrated,(.0018/dy,.004/dx))-gaussian_filter(integrated,(.013/dy,.060/dx))
fibers*=.0018/max(np.std(fibers),1e-9);fibers=np.clip(fibers,-.0045,.0045)
def ss(a,b,q):
 q=np.clip((q-a)/(b-a),0,1);return q*q*(3-2*q)
def sample(a,x,y):return map_coordinates(a,[(y+.84)/-1.3775*(h-1),(x+2.55)/5.1*(w-1)],order=1,mode='reflect')
V=Y-.105*np.tanh((Y-ky)/.11)*np.exp(-((X-kx)/.42)**2)
flow=sample(fibers,X,V)
plate=1-ss(.003,.014,-M['medium']-M['knot']);plate*=1-ss(.001,.012,-M['fractures'])
core=1-ss(.80,1.15,np.sqrt((rx/.145)**2+(ry/.17)**2))
quiet=1-.45*np.exp(-((X+.7)/.48)**2-((Y+1.03)/.13)**2)
scan_relief=(flow-.0025)*plate*quiet*(1-core)
core_fibers=.65*sample(fibers,kx+ry,ky-rx)*core-.0015*core
addition=.45*L['shaved_fibers']+.25*L['scanned_detail']+.55*L['knot_fibers']+L['central_check']+L['fiber_lift']+scan_relief+core_fibers
full=np.minimum(base+addition,0)
base_geometry=np.load(W/'R_layers_full/surface.npz')['height'].astype(float)
geometry=base_geometry+gaussian_filter(full-base,(.0022/dy,.0022/dx));geometry=np.minimum(geometry,0)
res=full-geometry;gy,gx=np.gradient(res,dy,dx);normal=np.stack([-gx,gy,np.ones_like(gx)],2);normal/=np.linalg.norm(normal,axis=2)[:,:,None]
out=W/'U_scan_fibers';out.mkdir(exist_ok=True)
for role in ['albedo','roughness']:(out/(role+'.png')).write_bytes((W/'T_fiber_material'/(role+'.png')).read_bytes())
a=np.pad(normal*.5+.5,((16,16),(16,16),(0,0)),mode='edge');Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).save(out/'normal.png')
np.savez_compressed(out/'surface.npz',height=geometry.astype('float32'));np.savez_compressed(out/'master_height.npz',height=full.astype('float32'))
np.savez_compressed(D/'normal_reconstruction.npz',integrated=integrated.astype('float32'),directional_fibers=fibers.astype('float32'),scan_relief=scan_relief.astype('float32'),addition=addition.astype('float32'))
d=dict(source_baseline='R_layers_full',source='Existing R anatomy with cached CC0 normal assisted physical fiber relief',normal_source='rough_wood_nor_gl_2k.png',normal_crop=[500,0,1000,2048],tangent_rotation='New X is old Y, new Y is negative old X',physical_source_scale='Amplitude is a controlled artistic test, not a measurement recovered from mockup',normal_split=.0022,split_policy='Original R geometry band retained exactly; only additions use sharper 0.0022 low pass. Complementary residual normal excludes both geometry bands.',height_min=float(full.min()),primary_groove_and_fracture_positions_preserved=True,knot_center=[kx,ky],material_variant='T identical albedo and roughness',layer_file=str(D/'normal_reconstruction.npz'))
(out/'design.json').write_text(json.dumps(d,indent=2));print(json.dumps(d),flush=True)
