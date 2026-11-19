from pathlib import Path
import numpy as np,json,shutil
from PIL import Image
from scipy.ndimage import gaussian_filter,map_coordinates
D=Path(__file__).resolve().parent;W=D.parent;U=W/'U_scan_fibers';C=W/'V_lookdev_refinement';C.mkdir(exist_ok=True)
rgb=np.asarray(Image.open(U/'albedo.png').convert('RGB'),float)[16:-16,16:-16]/255;rough=np.asarray(Image.open(U/'roughness.png').convert('L'),float)[16:-16,16:-16]/255;h,w=rough.shape;dx=5.1/(w-1);dy=1.3775/(h-1);X,Y=np.meshgrid(np.linspace(-2.55,2.55,w),np.linspace(-.84,-2.2175,h));kx,ky=-1.31,-1.35
r=np.hypot((X-kx)/.145,(Y-ky)/.17);t=np.clip((r-.70)/(.99-.70),0,1);core=1-t*t*(3-2*t)
source=W.parent/'resources/rough_wood'
def load(pat,rgb=False):
 im=Image.open(next(source.glob(pat))).convert('RGB' if rgb else 'L').crop((500,0,1000,2048)).transpose(Image.Transpose.ROTATE_270).resize((w,h),Image.Resampling.BICUBIC);return np.asarray(im,float)/255
def rotate_core(a):
 xx=kx+(Y-ky);yy=ky-(X-kx);v=(yy+.84)/(-1.3775)*(h-1);u=(xx+2.55)/5.1*(w-1);return map_coordinates(a,[v,u],order=1,mode='reflect')
scan=load('*diff*',True);lum=scan@np.array([.2126,.7152,.0722]);log=np.log(np.maximum(lum,.02));band=gaussian_filter(log,(.0025/dy,.006/dx))-gaussian_filter(log,(.014/dy,.055/dx));band=rotate_core(band);region=core>.8;band-=np.mean(band[region]);band=np.clip(band/max(np.std(band[region]),1e-6),-2.1,2.1)
# Independent intrinsic pigment variation, with zero directional light painted into it.
pigment=np.exp(.115*band-.5*.115**2);newrgb=rgb*(1-core[:,:,None]+core[:,:,None]*pigment[:,:,None]);chrom=scan/np.maximum(lum[:,:,None],.02)
for c in range(3):
 q=rotate_core(gaussian_filter(chrom[:,:,c],(.005/dy,.015/dx)));q=np.clip((q/np.median(q[region]))**.30,.94,1.06);newrgb[:,:,c]*=1-core+core*q
sr=rotate_core(load('*rough*'));sr-=np.mean(sr[region]);sr=np.clip(sr/max(np.std(sr[region]),1e-6),-2,2)
newrough=np.clip(rough+core*(-.025+.019*sr),.52,.83)
def save(name,a):
 a=np.pad(a,((16,16),(16,16))+(((0,0),) if a.ndim==3 else ()),mode='edge');Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).save(C/name)
save('albedo.png',newrgb);save('roughness.png',newrough);shutil.copy2(D/'calibrated_normal.png',C/'normal.png')
assert np.array_equal(np.uint8(rgb[core==0]*255+.5),np.uint8(newrgb[core==0]*255+.5));assert np.array_equal(np.uint8(rough[core==0]*255+.5),np.uint8(newrough[core==0]*255+.5))
d=dict(source='U_scan_fibers',geometry_changed=False,source_height_changed=False,primary_grain_knots_and_fractures_preserved=True,normal='Fine tangent correction based on actual mesh normals; broad correction removed',normal_strength=1,core_center=[kx,ky],core_radii=[.145,.17],pigment_log_variation=.115,roughness_core_offset=-.025,roughness_variation=.019,roughness_core_before=float(np.mean(rough[region])),roughness_core_after=float(np.mean(newrough[region])),body_albedo_and_roughness_outside_core_exact=True,source_maps='Existing cached CC0 Rough Wood diffuse and roughness, independently mapped to the core; broad source intensity removed',visual_status='Controlled material render pending, owner review required')
(C/'design.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
