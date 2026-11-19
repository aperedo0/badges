from pathlib import Path
import numpy as np,json,sys
from PIL import Image
from scipy.ndimage import gaussian_filter
R=Path(__file__).resolve().parent;C=R/(sys.argv[1] if len(sys.argv)>1 else 'candidate01');D=json.loads(((C/'design.json') if (C/'design.json').exists() else (R/'design.json')).read_text());T=C/'textures';T.mkdir(parents=True,exist_ok=True);rng=np.random.default_rng(D['seed']);W=D['texture_width'];H=D['texture_height'];pad=D['padding'];w=W-2*pad;h=H-2*pad;b=D['bounds'];x=np.linspace(b['xmin'],b['xmax'],w);y=np.linspace(b['ymax'],b['ymin'],h);X,Y=np.meshgrid(x,y);dx=x[1]-x[0];dy=abs(y[1]-y[0])
def noise(nx,ny,sx=0,sy=0):
 a=rng.normal(size=(ny,nx)).astype(np.float32);a=np.asarray(Image.fromarray(a,mode='F').resize((w,h),Image.Resampling.BICUBIC),float);a=gaussian_filter(a,(sy,sx));return (a-a.mean())/(a.std()+1e-10)
def smooth(a,b,v):
 z=np.clip((v-a)/(b-a),0,1);return z*z*(3-2*z)
slow=noise(11,8,12,5);fiber=noise(23,78,10,1.3);drift=noise(15,25,15,3);fine=noise(42,110,7,1.2);k=D['knot'];kx,ky=k['x'],k['y'];xx=X-kx;yy=Y-ky
# A continuous growth coordinate bends outside the branch and closes around its core.
r=np.sqrt((xx/.27)**2+(yy/.18)**2);rj=r+.014*drift+.009*np.sin(np.arctan2(yy,xx)*5+r*3)
flow_y=Y-yy/np.maximum(rj*rj,1.)
inside_y=ky+.245*(1-rj)
q=np.where(rj<1,inside_y,flow_y)+.009*np.sin(X*2.1)+.003*drift
strand=noise(95,230,3,.65);chips=noise(220,280,1.2,.65)
phase=q/.066+.050*fiber+.035*strand
track=np.exp(-(np.sin(np.pi*phase)/.46)**2)
fine_phase=q/.024+.08*strand+.035*chips
fine_tracks=np.exp(-(np.sin(np.pi*fine_phase)/.34)**2)
tracks=gaussian_filter(track,(.55,.4))*np.clip(.68+.26*strand,.22,1)
km=1-smooth(.70,1.35,r)
# Tapered fissures follow the surrounding fibers instead of random scratches.
cracks=np.zeros_like(X)
for i in range(31):
 x0=rng.uniform(-2.50,2.05);length=rng.uniform(.16,.78);y0=rng.uniform(b['ymin']+.025,b['ymax']-.025);u=(X-x0)/length;window=smooth(0,.12,u)*(1-smooth(.82,1,u));bend=.010*np.sin(u*5+rng.uniform(0,6))+.008*np.sin(X*11+rng.uniform(0,6));localflow=.08*np.tanh((y0-ky)/.10)*np.exp(-((X-kx)/.5)**2)*np.exp(-((y0-ky)/.3)**2);yc=y0+bend-localflow;width=rng.uniform(.006,.013)*(0.35+.65*np.sin(np.pi*np.clip(u,0,1))**.55);v=np.exp(-((Y-yc)/(width+1e-6))**2)*window;v*=.4+.6*smooth(-1.4,.8,fiber);cracks=np.maximum(cracks,v)
# A short split in the round knot heart.
heart=np.exp(-((xx-.008*np.sin(yy*33))/.0075)**2)*(1-smooth(.10,.145,abs(yy)));cracks*=smooth(.91,1.15,r);cracks=np.maximum(cracks,.85*heart);cracks=gaussian_filter(cracks,(.45,.35))
core=(1-smooth(.3,.70,r))*(.75+.25*np.sin(X*14+Y*9));tone=np.clip(.62+.11*slow+.11*fiber+.09*strand+.095*chips+.025*fine,0,1);tone=tone*(1-km*.35)+(.50+.10*slow+.07*chips)*(km*.35)
dark=np.array([.28,.084,.020]);light=np.array([.76,.365,.125]);rgb=dark+(light-dark)*tone[...,None];rgb*=1-.31*tracks[...,None];rgb*=1-.21*fine_tracks[...,None];rgb*=1-.18*core[...,None];rgb*=1-.62*cracks[...,None];rgb=np.clip(rgb,0,1)
# Height is measured in the actual chest units. Normal strength is fully baked.
height=.00045*gaussian_filter(strand,(1.2,.9))+.00025*gaussian_filter(chips,(1.,.8))-.0027*tracks-.0065*cracks-.0010*core;height=gaussian_filter(height,(.65,.5));gy,gx=np.gradient(height,dy,dx);gy=-gy;N=np.stack([-gx,-gy,np.ones_like(gx)],axis=2);slope=np.linalg.norm(N[...,:2],axis=2);maximum=np.tan(np.deg2rad(D['maximum_normal_degrees']));fac=np.minimum(1,maximum/(slope+1e-12));N[...,:2]*=fac[...,None];N/=np.linalg.norm(N,axis=2)[...,None];normal=.5+.5*N
rough=np.clip(.735+.035*tracks+.07*cracks+.015*slow+.025*core,D['roughness_min'],D['roughness_max']);rough=gaussian_filter(rough,(.55,.4))
def save(name,a):
 if a.ndim==3:a=np.pad(a,((pad,pad),(pad,pad),(0,0)),mode='edge')
 else:a=np.pad(a,((pad,pad),(pad,pad)),mode='edge')
 Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).save(T/name)
save('wood_albedo.png',rgb);save('wood_roughness.png',rough);save('wood_normal.png',normal)
lo,hi=-.020,.005;encoded=np.uint16(np.clip((height-lo)/(hi-lo),0,1)*65535+.5);Image.fromarray(np.pad(encoded,((pad,pad),(pad,pad)),mode='edge'),mode='I;16').save(T/'wood_height_diagnostic.png');np.savez_compressed(C/'physical_height.npz',height=height,x=x,y=y)
report=dict(canvas=[W,H],padding=pad,seed=D['seed'],physical_height_min=float(height.min()),physical_height_max=float(height.max()),normal_tilt_max=float(np.rad2deg(np.arccos(N[:,:,2])).max()),roughness_min=float(rough.min()),roughness_max=float(rough.max()),linear_light_baked=False,emission=False,reference_pixels_used=False,palette_srgb_mean=rgb.mean((0,1)).tolist());(C/'texture_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
