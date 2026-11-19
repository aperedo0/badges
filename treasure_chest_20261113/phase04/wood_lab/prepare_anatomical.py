from pathlib import Path
import numpy as np,json
from scipy.ndimage import gaussian_filter,map_coordinates
from scipy.interpolate import CubicSpline
from PIL import Image
P=Path(__file__).resolve().parent;out=P/'G_anatomical';out.mkdir(exist_ok=True)
h,w=736,2016;dx=5.1/(w-1);dy=1.3775/(h-1);x=np.linspace(-2.55,2.55,w);y=np.linspace(-.84,-2.2175,h);X,Y=np.meshgrid(x,y);rng=np.random.default_rng(2315);kx=-1.18;ky=-1.40

def ss(a,b,q):
 t=np.clip((q-a)/(b-a),0,1);return t*t*(3-2*t)
height=np.zeros((h,w));latewood=np.zeros_like(height);channels=[]
# Authored uneven growth layer spacing. Each layer has an independent slow drift.
ys=[-.875,-.926,-.972,-1.010,-1.068,-1.103,-1.151,-1.218,-1.259,-1.311,-1.360,-1.414,-1.456,-1.508,-1.559,-1.602,-1.670,-1.714,-1.766,-1.831,-1.879,-1.935,-1.981,-2.052,-2.106,-2.161,-2.200]
for i,base in enumerate(ys):
 phase=rng.uniform(0,6.28);ctrl=rng.normal(0,.009,9);drift=CubicSpline(np.linspace(-2.55,2.55,9),ctrl,bc_type='natural')(x)
 delta=base-ky;bow=np.sign(delta)*.17*np.exp(-abs(delta)/.43)*np.exp(-((x-kx)/(.39+.22*abs(delta)))**2)
 line=base+drift+bow;dist=Y-line[None,:]
 width=(.0045+rng.random()*.006)*(1+.24*np.sin(x*3.2+phase)+.15*np.sin(x*12.3+phase))
 depth=(.010+rng.random()*.014)*(1+.20*np.sin(x*2.5+phase))
 # Interrupted growth channels, with quiet broad surfaces between them.
 gate=.55+.45*ss(-.5,.6,np.sin(x*(1.4+rng.random())+phase));core=np.maximum(1-abs(dist)/width[None,:],0)
 # One wider weathered shoulder, one sharp fracture edge.
 shoulder=np.exp(-(np.maximum(dist,0)/(width[None,:]*2.1))**2)*(.0025*(dist>0))
 cut=depth[None,:]*core**1.4*gate[None,:]+shoulder
 height-=cut;latewood=np.maximum(latewood,np.exp(-(dist/(width[None,:]*2.8))**2))
 channels.append(dict(y=base,depth=float(depth.mean()),width=float(width.mean())))
# The branch knot blends into the same board, with irregular close growth rings.
r=np.sqrt(((X-kx)/.151)**2+((Y-ky)/.143)**2);theta=np.arctan2((Y-ky)/.143,(X-kx)/.151);core=1-ss(.92,1.16,r)
knot=-.005+.0013*np.cos(r*24+np.sin(theta*3)*.35);knot-=.003*np.exp(-(np.sin(r*12+.3*np.sin(theta*2))/.25)**2)
height=height*(1-core)+knot*core
# Outer boundary of the knot is broken and slightly eccentric, never a perfect ring.
ring=np.abs(r-(1.04+.035*np.sin(theta*5)+.025*np.sin(theta*9)));height-=.009*np.exp(-(ring/.045)**2)*(1-.35*ss(.2,.9,np.cos(theta*2)))
# Long irregular fractures are localized to three grain layers, not spread everywhere.
fract=np.zeros_like(height)
for start,end,y0,dep,width,phase in [(-2.35,-.46,-1.055,.029,.017,.7),(.65,2.25,-1.735,.033,.016,2.1),(-.6,.4,-2.032,.020,.009,1.3)]:
 t=np.clip((X-start)/(end-start),0,1);active=((X>start)&(X<end));taper=np.sin(np.pi*t)**.7;path=y0+.012*np.sin(X*5+phase)+.003*np.sin(X*29+phase);localw=width*taper*(.8+.3*np.sin(X*18+phase));v=np.maximum(1-abs(Y-path)/np.maximum(localw,.0001),0)**.65
 fract=np.maximum(fract,v*dep*taper*active)
# The radial check in the branch core follows a bent, irregular path.
path=kx+.006*np.sin((Y-ky)*39)+.008*(Y-ky);taper=ss(-1.67,-1.58,Y)*(1-ss(-1.22,-1.13,Y));fract=np.maximum(fract,.028*np.maximum(1-abs(X-path)/(.004+.003*taper),0)**.7*taper)
height-=fract
# Torn fiber chips cluster beside the larger checks. Broad tops stay untouched.
chips=np.zeros_like(height)
for cx,cy,rx,ry,dep,skew in [(-1.94,-1.07,.12,.025,.014,.3),(-1.74,-1.08,.085,.018,.009,-.1),(-.73,-1.05,.16,.021,.014,.2),(1.22,-1.74,.18,.026,.013,-.4),(1.47,-1.73,.07,.018,.010,.1),(-.28,-2.03,.12,.022,.009,.2)]:
 xx=(X-cx)/rx;yy=(Y-cy)/ry+skew*xx;chip=np.clip(1-abs(xx)-abs(yy),0,1)**.65;chips=np.maximum(chips,dep*chip)
height-=chips
# Natural fine fibers from the free scanned material, bent with the branch flow.
scan=np.load(P/'C_scan/surface.npz')['height'];flowY=Y-.10*np.tanh((Y-ky)/.10)*np.exp(-((X-kx)/.44)**2);v=np.clip((flowY+.84)/(-1.3775)*(h-1),0,h-1);u=np.broadcast_to(np.arange(w)[None,:],(h,w));scan=map_coordinates(scan,[v,u],order=1,mode='reflect');fine=scan-gaussian_filter(scan,(.008/dy,.065/dx));height+=fine*.33*(1-.6*core)
# Independent wood pigment: broad age, growth layer chroma and scanned fine stains.
oldrgb=np.asarray(Image.open(P/'C_scan/albedo.png').convert('RGB'),float)[16:-16,16:-16]/255;lum=np.dot(oldrgb,[.2126,.7152,.0722]);p=lum/np.maximum(gaussian_filter(lum,(.025/dy,.12/dx)),.01);p=np.clip(p**.55,.82,1.14)
broad=.07*np.sin(X*.9+Y*1.8)+.04*np.cos(X*2.1-Y*.6);color=np.array([.51,.252,.112])[None,None,:]*(1+broad[:,:,None])*p[:,:,None]
color*= (1-.065*latewood-.20*np.clip(fract/.025,0,1)-.13*core)[:,:,None]
color+=np.array([.022,.014,.005])[None,None,:]*np.clip(chips/.015,0,1)[:,:,None]
rough=np.clip(.62+.05*latewood+.07*core+.07*np.clip(fract/.025,0,1)+.035*(p-1),.55,.82)
low=gaussian_filter(height,(.0013/dy,.0013/dx));res=height-low;gy,gx=np.gradient(res,dy,dx);n=np.stack([-gx,gy,np.ones_like(gx)],axis=2);n/=np.linalg.norm(n,axis=2)[:,:,None]
def save(name,a):
 a=np.pad(a,((16,16),(16,16))+(((0,0),) if a.ndim==3 else ()),mode='edge');Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).save(out/name)
save('albedo.png',color);save('normal.png',n*.5+.5);save('roughness.png',rough);np.savez_compressed(out/'surface.npz',height=low.astype('float32'));np.savez_compressed(out/'master_height.npz',height=height.astype('float32'),fractures=fract.astype('float32'),chips=chips.astype('float32'))
Image.fromarray(np.uint16(np.clip((height+.08)/.08,0,1)*65535+.5)).save(out/'height16.png');(out/'design.json').write_text(json.dumps(dict(seed=2315,channels=channels,knot=[kx,ky],depth_min=float(height.min()),depth_max=float(height.max()),source='Authored longitudinal growth anatomy, branch flow, checks, chips and CC0 scanned fine fibers',pigment='independent chestnut age stains; cavity stain limited to 20 percent in checks',normal='residual finer than 0.0013 units',height16_zero=-.08,height16_one=0),indent=2))
