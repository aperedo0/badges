from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates

W=Path(__file__).resolve().parent
P=W.parent
scan=np.load(P/'C_scan/surface.npz')['height'].astype(float)
h,w=scan.shape
dx,dy=5.1/(w-1),1.3775/(h-1)
X,Y=np.meshgrid(np.linspace(-2.55,2.55,w),np.linspace(-.84,-2.2175,h))
def ss(a,b,v):
    t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
def sample(a,x,y):
    return map_coordinates(a,[(y+.84)/-1.3775*(h-1),(x+2.55)/5.1*(w-1)],order=1,mode='reflect')
def save(folder,name,a):
    pads=((16,16),(16,16))+(((0,0),) if a.ndim==3 else ())
    Image.fromarray(np.uint8(np.clip(np.pad(a,pads,mode='edge'),0,1)*255+.5)).save(folder/name)

# Natural scanned structure replaces the generated concentric anatomy.
kx,ky=-1.18,-1.38
warp=.070*np.tanh((Y-ky)/.10)*np.exp(-((X-kx)/.37)**2)
sx=(X-.12)*.88
sy=Y-warp
natural=sample(scan,sx,sy)
q=np.clip(-natural/.045,0,1)
base=-.014*q**1.45
fine=natural-gaussian_filter(natural,(.009/dy,.045/dx))
base+=.35*fine

# A shallow asymmetric wooden core, no circular groove or contour rings.
theta=np.arctan2((Y-ky)/.14,(X-kx)/.16)
r=np.sqrt(((X-kx+.10*(Y-ky))/.16)**2+((Y-ky)/.14)**2)
r/=1+.08*np.cos(3*theta)+.05*np.sin(5*theta)
core=1-ss(.60,1.10,r)
endgrain=sample(scan,kx+(Y-ky)*.9,ky-(X-kx)*.8)
coreheight=-.006+.12*(endgrain-gaussian_filter(endgrain,(.02/dy,.02/dx)))
base=base*(1-core)+coreheight*core

# Sparse authored fractures follow reference structure, not procedural rings.
paths=[
 ([(-2.47,-1.13),(-2.14,-1.12),(-1.83,-1.15),(-1.55,-1.12)],.018,.022),
 ([(-1.58,-1.17),(-1.35,-1.13),(-1.12,-1.14),(-.85,-1.18),(-.54,-1.17)],.014,.018),
 ([(-2.31,-1.68),(-1.99,-1.66),(-1.71,-1.61),(-1.47,-1.60),(-1.20,-1.62),(-.86,-1.66),(-.53,-1.64)],.022,.026),
 ([(.42,-1.13),(.72,-1.11),(1.03,-1.13),(1.21,-1.10)],.013,.016),
 ([(.70,-1.57),(1.03,-1.58),(1.40,-1.55),(1.70,-1.58),(2.30,-1.56)],.020,.024),
 ([(1.36,-1.92),(1.69,-1.90),(1.92,-1.93),(2.22,-1.91)],.012,.016),
 ([(-1.27,-1.28),(-1.23,-1.36),(-1.25,-1.43),(-1.20,-1.52)],.008,.018),
 ([(-1.25,-1.43),(-1.13,-1.46),(-1.03,-1.50)],.006,.009),
 ([(-1.99,-1.66),(-1.80,-1.72),(-1.61,-1.72)],.009,.012),
 ([(1.40,-1.55),(1.53,-1.64),(1.76,-1.65)],.008,.012)]
fract=np.zeros_like(base)
for index,(points,width,depth) in enumerate(paths):
    lengths=[np.linalg.norm(np.subtract(b,a)) for a,b in zip(points[:-1],points[1:])]
    total=sum(lengths);offset=0;cut=np.zeros_like(base)
    for a,b,length in zip(points[:-1],points[1:],lengths):
        a=np.array(a);v=np.array(b)-a
        t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/np.dot(v,v),0,1)
        progress=(offset+t*length)/total
        taper=np.sin(np.pi*progress)**.65
        varying=.55+.28*np.sin(progress*9+index)**2+.20*np.sin(progress*23+index*.7)**2
        # Local bridges interrupt the long fractures instead of drawing outlines.
        bridge=1-.92*np.exp(-((progress-(.36+.08*(index%3)))/.045)**4)
        distance=np.sqrt((X-a[0]-t*v[0])**2+(Y-a[1]-t*v[1])**2)
        profile=np.clip(1-distance/(width*varying*np.maximum(taper,.02)),0,1)**.75
        cut=np.maximum(cut,profile*taper*bridge)
        offset+=length
    fract=np.maximum(fract,depth*cut)

scanrgb=np.asarray(Image.open(P/'C_scan/albedo.png').convert('RGB'),float)[16:-16,16:-16]/255
lum=scanrgb@np.array([.2126,.7152,.0722])
pigment=sample(lum,sx,sy)
finepig=pigment/np.maximum(gaussian_filter(pigment,(.028/dy,.12/dx)),.01)
largepig=gaussian_filter(pigment,(.06/dy,.22/dx))
largepig=np.clip(largepig/np.median(largepig),.78,1.16)
color=np.array([.49,.238,.099])[None,None,:]*np.clip(finepig**.42,.79,1.16)[:,:,None]*largepig[:,:,None]
stain=.18*np.exp(-((X+1.9)/.43)**2-((Y+1.9)/.15)**2)+.15*np.exp(-((X-1.3)/.7)**2-((Y+1.03)/.13)**2)
color*= (1-stain)[:,:,None]
color*= (1-.12*np.clip(fract/.025,0,1))[:,:,None]
rough=np.clip(.64+.045*(q-.4)+.065*np.clip(fract/.025,0,1)-.025*np.clip(finepig-1,0,.2),.55,.82)

for key in ['I_structure','J_broken_fibers']:
    folder=W/key;folder.mkdir(exist_ok=True)
    full=base-fract
    chips=np.zeros_like(base);lifts=np.zeros_like(base)
    if key.startswith('J'):
        for cx,cy,length,width,depth,angle in [(-2.02,-1.11,.24,.040,.013,.10),(-1.65,-1.70,.21,.045,.015,-.16),(-.78,-1.15,.16,.030,.009,.08),(-1.64,-1.89,.24,.045,.012,.12),(.85,-1.14,.25,.038,.012,-.09),(1.61,-1.59,.31,.043,.014,.07),(2.03,-1.90,.20,.035,.009,-.12),(1.13,-1.82,.18,.032,.008,.14)]:
            xx=(X-cx)/length;yy=(Y-cy-angle*(X-cx))/width
            footprint=np.clip(1-abs(xx),0,1)
            # Broken terrace with an abrupt shoulder and a tapered compressed bed.
            bed=np.clip(1-abs(yy),0,1)*footprint
            chips=np.maximum(chips,depth*bed)
            shoulder=np.exp(-((yy-.85)/.22)**2)*footprint
            lifts=np.maximum(lifts,.0045*shoulder)
        full+=lifts-chips
    full=np.minimum(full,0)
    low=gaussian_filter(full,(.0055/dy,.0055/dx))
    residual=full-low
    gy,gx=np.gradient(residual,dy,dx)
    normal=np.stack([-gx,gy,np.ones_like(gx)],axis=2);normal/=np.linalg.norm(normal,axis=2)[:,:,None]
    finalcolor=color*(1-.08*np.clip(chips/.015,0,1))[:,:,None]
    finalrough=np.clip(rough+.035*np.clip(chips/.015,0,1),.55,.85)
    np.savez_compressed(folder/'surface.npz',height=low.astype('float32'))
    np.savez_compressed(folder/'master_height.npz',height=full.astype('float32'),fracture=fract.astype('float32'),chips=chips.astype('float32'))
    save(folder,'albedo.png',finalcolor);save(folder,'roughness.png',finalrough);save(folder,'normal.png',normal*.5+.5)
    Image.fromarray(np.uint16(np.clip((full+.065)/.065,0,1)*65535+.5)).save(folder/'height16.png')
    (folder/'design.json').write_text(json.dumps(dict(foundation='Cached CC0 Poly Haven Rough Wood plus sparse authored structural fractures; generated contour anatomy replaced',height_min=float(full.min()),height_max=float(full.max()),fracture_paths=len(paths),broken_terraces=8 if key.startswith('J') else 0,knot='Shallow asymmetric wood core with forked checks, no concentric grooves',normal_split=.0055,scope='Single existing test plank only'),indent=2))
    print(key,float(full.min()),flush=True)
