from pathlib import Path
import numpy as np,json
from scipy.ndimage import gaussian_filter,map_coordinates
from PIL import Image
P=Path(__file__).resolve().parent;B=P.parents[1]/'phase03/stylized_wood45/candidate05';out=P/'E_carved';out.mkdir(exist_ok=True)
old=np.load(B/'physical_height.npz')['height'];h,w=old.shape;dx=5.1/(w-1);dy=1.3775/(h-1);X,Y=np.meshgrid(np.linspace(-2.55,2.55,w),np.linspace(-.84,-2.2175,h))
def ss(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def save(name,a):
 a=np.pad(a,((16,16),(16,16))+(((0,0),) if a.ndim==3 else ()),mode='edge');Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).save(out/name)
def sample(a,xx,yy):
 v=(yy+.84)/(-1.3775)*(h-1);u=(xx+2.55)/5.1*(w-1)
 return map_coordinates(a,[v,u],order=1,mode='reflect')
# Reuse the approved gross anatomy. Real channels carry their own shadows.
macro=-.043*np.clip(-gaussian_filter(old,(.0016/dy,.0020/dx))/.056,0,1)**2.0
kx=-1.18;ky=-1.38;r=np.sqrt(((X-kx)/.18)**2+((Y-ky)/.17)**2);core=1-ss(.70,1.12,r)
# A wooden knot core, not a deep empty black hole.
macro=macro*(1-core)+(-.009+.0016*np.sin(r*36+.5*np.sin((Y-ky)*23))+.0012*np.cos((X-kx)*65))*core
scan=np.load(P/'C_scan/surface.npz')['height'];flowY=Y-.14*np.tanh((Y-ky)/.09)*np.exp(-((X-kx)/.52)**2);scan=sample(scan,X,flowY)
fibers=scan-gaussian_filter(scan,(.008/dy,.055/dx));fibers*=.32*(1-.35*core)
# Quiet ridge plates retain broad anatomy, fine fibers live on their exposed tops.
ridge=ss(-.035,-.012,macro);full=macro+fibers*(.3+.7*ridge)
# Three long tapered splits and a knot check are authored separately from grain.
fract=np.zeros_like(old)
paths=[([(-2.35,-1.09),(-1.80,-1.08),(-1.48,-1.12),(-1.25,-1.10)],.016,.022), ([(.72,-1.63),(1.15,-1.60),(1.65,-1.64),(2.26,-1.61)],.020,.030),([(-.82,-1.97),(-.31,-1.95),(.15,-1.99)],.008,.016),([(-1.19,-1.18),(-1.17,-1.35),(-1.20,-1.50),(-1.17,-1.57)],.007,.028)]
for points,width,depth in paths:
 lengths=[np.linalg.norm(np.subtract(b,a)) for a,b in zip(points[:-1],points[1:])];total=sum(lengths);off=0;f=np.zeros_like(old)
 for a,b,le in zip(points[:-1],points[1:],lengths):
  a=np.array(a);v=np.array(b)-a;t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/np.dot(v,v),0,1);progress=(off+t*le)/total;taper=np.sin(np.pi*progress)**.55
  dist=np.sqrt((X-a[0]-t*v[0])**2+(Y-a[1]-t*v[1])**2);localwidth=width*(.7+.3*np.sin(progress*17))
  f=np.maximum(f,np.clip(1-dist/(localwidth*np.maximum(taper,.04)),0,1)**.8*taper);off+=le
 fract=np.maximum(fract,f*depth)
# Two small torn flakes sit within exposed ridge plates, away from hardware.
chips=np.zeros_like(old)
for cx,cy,rx,ry,depth in [(-1.68,-1.88,.13,.034,.016),(.92,-1.11,.18,.028,.011),(1.87,-1.77,.11,.025,.009)]:
 xx=(X-cx)/rx;yy=(Y-cy)/ry+.16*xx
 chips=np.maximum(chips,depth*np.clip(1-abs(xx)-abs(yy),0,1)**.55)
full-=fract+chips
# Broad pigment is independent of height. Scan fibers supply small intrinsic variation.
oldrgb=np.asarray(Image.open(B/'textures/wood_albedo.png').convert('RGB'),float)[16:-16,16:-16]/255
broad=gaussian_filter(np.dot(oldrgb,[.2126,.7152,.0722]),(.065/dy,.16/dx));broad=np.clip((broad/np.median(broad))**.22,.83,1.12)
scanrgb=np.asarray(Image.open(P/'C_scan/albedo.png').convert('RGB'),float)[16:-16,16:-16]/255;sl=np.dot(scanrgb,[.2126,.7152,.0722]);pigment=sl/np.maximum(gaussian_filter(sl,(.02/dy,.10/dx)),.01);pigment=sample(pigment,X,flowY);pigment=np.clip(pigment**.65,.80,1.16)
color=np.array([.51,.255,.125])[None,None,:]*broad[:,:,None]*pigment[:,:,None]
# Local age stains, warm exposed fibers and restrained cavity staining.
stain=.16*np.exp(-((X+1.75)/.45)**2-((Y+1.88)/.17)**2)+.13*np.exp(-((X-.9)/.65)**2-((Y+1.02)/.11)**2)
color*= (1-stain)[:,:,None];cavity=ss(.023,.042,-macro);color*= (1-.09*cavity-.18*np.clip(fract/.025,0,1)-.06*core)[:,:,None]
wear=ss(-.012,-.003,macro)*.05;color=color*(1-wear[:,:,None])+np.array([.61,.34,.16])*wear[:,:,None]
rough=.67+.055*gaussian_filter((scan-np.mean(scan))/np.std(scan),(.018/dy,.07/dx))+.055*cavity+.065*np.clip(fract/.025,0,1)-.025*ridge
rough=np.clip(rough,.55,.82)
# Broad and medium details are geometry. Only the complementary high band is normal.
low=gaussian_filter(full,(.0015/dy,.0015/dx));residual=full-low;gy,gx=np.gradient(residual,dy,dx);normal=np.stack([-gx,gy,np.ones_like(gx)],axis=2);normal/=np.linalg.norm(normal,axis=2)[:,:,None]
np.savez_compressed(out/'surface.npz',height=low.astype('float32'));np.savez_compressed(out/'master_height.npz',height=full.astype('float32'),fracture=fract.astype('float32'),pigment=stain.astype('float32'))
save('normal.png',.5+.5*normal);save('albedo.png',color);save('roughness.png',rough)
# 16 bit inspection height, with explicit physical scale recorded.
Image.fromarray(np.uint16(np.clip((full+.08)/.08,0,1)*65535+.5)).save(out/'height16.png')
(out/'design.json').write_text(json.dumps(dict(source='Existing anatomical height plus CC0 Rough Wood fine detail',depth_min=float(full.min()),depth_max=float(full.max()),knot=[kx,ky],source_relief_factor='power 2, 0.043 unit depth',fractures=4,pigment='independent broad chestnut stains and scanned fiber variation',normal='residual after 0.0015 unit low pass',height16_zero=-.08,height16_one=0),indent=2))
