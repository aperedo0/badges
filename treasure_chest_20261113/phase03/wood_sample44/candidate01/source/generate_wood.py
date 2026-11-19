from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import gaussian_filter
R=Path(__file__).resolve().parent;D=json.loads((R/'design.json').read_text());C=R/'candidate01';T=C/'textures';T.mkdir(parents=True,exist_ok=True);rng=np.random.default_rng(D['seed']);W=D['texture_width'];H=D['texture_height'];pad=D['padding'];w=W-2*pad;h=H-2*pad;b=D['bounds'];x=np.linspace(b['xmin'],b['xmax'],w);y=np.linspace(b['ymax'],b['ymin'],h);X,Y=np.meshgrid(x,y);dx=x[1]-x[0];dy=abs(y[1]-y[0])
def noise(nx,ny,sx=0,sy=0):
 a=rng.normal(size=(ny,nx)).astype(np.float32);a=np.asarray(Image.fromarray(a,mode='F').resize((w,h),Image.Resampling.BICUBIC),float);a=gaussian_filter(a,(sy,sx));return (a-a.mean())/(a.std()+1e-10)
def smooth(a,b,v):
 z=np.clip((v-a)/(b-a),0,1);return z*z*(3-2*z)
slow=noise(11,8,12,5);fiber=noise(23,78,10,1.3);drift=noise(15,25,15,3);fine=noise(42,110,7,1.2);k=D['knot'];kx,ky=k['x'],k['y'];xx=X-kx;yy=Y-ky
# A rounded heartwood core opens into wider flowing grain outside it.
rx=.235;ry=.18;r=np.sqrt((xx/rx)**2+(yy/ry)**2);rj=r+.018*drift+.012*np.sin(np.arctan2(yy,xx)*5+r*3)
flow=.100*np.tanh(yy/.085)*np.exp(-(xx/.48)**2)*np.exp(-(yy/.30)**2)
q=Y+flow+.020*np.sin(X*2.1)+.012*np.sin(X*5.7+.4)+.009*drift
phase=q/.069+.075*fiber+.035*np.sin(X*12+Y*2)
track=np.exp(-(np.sin(np.pi*phase)/.47)**2);strand=noise(57,190,3,.65);chips=noise(110,120,1.2,.7);fine_phase=q/.025+.22*fiber+.11*strand;fine_tracks=np.exp(-(np.sin(np.pi*fine_phase)/.35)**2)
knots=np.exp(-(np.sin(np.pi*(3.85*rj+.12*slow))/.44)**2);km=1-smooth(.9,1.70,r);tracks=track*(1-km)+knots*km;tracks=gaussian_filter(tracks,(.65,.4));tracks*=np.clip(.72+.24*strand,.30,1)
# Tapered fissures follow the surrounding fibers instead of random scratches.
cracks=np.zeros_like(X)
for i in range(31):
 x0=rng.uniform(-2.50,2.05);length=rng.uniform(.16,.78);y0=rng.uniform(b['ymin']+.025,b['ymax']-.025);u=(X-x0)/length;window=smooth(0,.12,u)*(1-smooth(.82,1,u));bend=.010*np.sin(u*5+rng.uniform(0,6))+.008*np.sin(X*11+rng.uniform(0,6));localflow=.08*np.tanh((y0-ky)/.10)*np.exp(-((X-kx)/.5)**2)*np.exp(-((y0-ky)/.3)**2);yc=y0+bend-localflow;width=rng.uniform(.006,.013)*(0.35+.65*np.sin(np.pi*np.clip(u,0,1))**.55);v=np.exp(-((Y-yc)/(width+1e-6))**2)*window;v*=.4+.6*smooth(-1.4,.8,fiber);cracks=np.maximum(cracks,v)
# A short split in the round knot heart.
heart=np.exp(-((xx-.008*np.sin(yy*33))/.0075)**2)*(1-smooth(.10,.145,abs(yy)));cracks=np.maximum(cracks,.92*heart);cracks=gaussian_filter(cracks,(.45,.35))
core=(1-smooth(.3,.70,r))*(.75+.25*np.sin(X*14+Y*9));tone=np.clip(.60+.10*slow+.10*fiber+.075*strand+.055*chips+.025*fine,0,1)
dark=np.array([.28,.084,.020]);light=np.array([.76,.365,.125]);rgb=dark+(light-dark)*tone[...,None];rgb*=1-.25*tracks[...,None];rgb*=1-.18*fine_tracks[...,None];rgb*=1-.18*core[...,None];rgb*=1-.62*cracks[...,None];rgb=np.clip(rgb,0,1)
# Height is measured in the actual chest units. Normal strength is fully baked.
height=.0011*gaussian_filter(strand,(1.0,.8))+.0007*gaussian_filter(chips,(.8,.6))-.0048*tracks-.0025*fine_tracks-.011*cracks-.0013*core;height=gaussian_filter(height,(.65,.5));gy,gx=np.gradient(height,dy,dx);gy=-gy;N=np.stack([-gx,-gy,np.ones_like(gx)],axis=2);slope=np.linalg.norm(N[...,:2],axis=2);maximum=np.tan(np.deg2rad(D['maximum_normal_degrees']));fac=np.minimum(1,maximum/(slope+1e-12));N[...,:2]*=fac[...,None];N/=np.linalg.norm(N,axis=2)[...,None];normal=.5+.5*N
rough=np.clip(.59+.075*tracks+.16*cracks+.025*slow+.025*core,D['roughness_min'],D['roughness_max']);rough=gaussian_filter(rough,(.55,.4))
def save(name,a):
 if a.ndim==3:a=np.pad(a,((pad,pad),(pad,pad),(0,0)),mode='edge')
 else:a=np.pad(a,((pad,pad),(pad,pad)),mode='edge')
 Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).save(T/name)
save('wood_albedo.png',rgb);save('wood_roughness.png',rough);save('wood_normal.png',normal)
lo,hi=-.020,.005;encoded=np.uint16(np.clip((height-lo)/(hi-lo),0,1)*65535+.5);Image.fromarray(np.pad(encoded,((pad,pad),(pad,pad)),mode='edge'),mode='I;16').save(T/'wood_height_diagnostic.png');np.savez_compressed(C/'physical_height.npz',height=height,x=x,y=y)
report=dict(canvas=[W,H],padding=pad,seed=D['seed'],physical_height_min=float(height.min()),physical_height_max=float(height.max()),normal_tilt_max=float(np.rad2deg(np.arccos(N[:,:,2])).max()),roughness_min=float(rough.min()),roughness_max=float(rough.max()),linear_light_baked=False,emission=False,reference_pixels_used=False,palette_srgb_mean=rgb.mean((0,1)).tolist());(C/'texture_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
