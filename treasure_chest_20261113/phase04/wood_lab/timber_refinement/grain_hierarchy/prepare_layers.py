from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,map_coordinates,maximum_filter
D=Path(__file__).resolve().parent;W=D.parent;P=W.parent
H=np.load(P/'H_resolved/master_height.npz')['height'].astype(float)
current=np.load(W/'P_physical_fractures/master_height.npz')
scan=np.load(W/'O_timber_balanced/master_height.npz')['height'].astype(float)
h,w=H.shape;dx,dy=5.1/(w-1),1.3775/(h-1)
X,Y=np.meshgrid(np.linspace(-2.55,2.55,w),np.linspace(-.84,-2.2175,h))
def ss(a,b,v):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
def sample(a,x,y):
 return map_coordinates(a,[(y+.84)/-1.3775*(h-1),(x+2.55)/5.1*(w-1)],order=1,mode='nearest')

# A: subdued broad wood shape independent of ridges and damage.
A=-.003+.12*(gaussian_filter(scan,(.08/dy,.20/dx))-np.median(scan))
A=np.clip(A,-.006,-.001)

# B and D: recover H's useful layered anatomy without its oversized ring field.
kx,ky=-1.31,-1.35
rx,ry=X-kx,Y-ky
r=np.sqrt(rx*rx+ry*ry)
falloff=np.exp(-(r/.62)**4)
outer=ss(.12,.30,r)*falloff
centerfall=np.exp(-(r/1.25)**4)
Xs=X+(-1.18-kx)*centerfall+.55*rx*outer
Ys=Y+(-1.38-ky)*centerfall+.32*ry*outer
gx=np.gradient(Xs,dx,axis=1);gy=-np.gradient(Ys,dy,axis=0)
assert np.min(gx)>.1 and np.min(gy)>.1,'Anatomy warp must not fold'
lowH=gaussian_filter(H,(.0055/dy,.0055/dx))
band=lowH-gaussian_filter(lowH,(.075/dy,.14/dx))
recovered=sample(band,Xs,Ys)
# Flatten raised plate tops rather than retaining inflated positive humps.
recovered=-np.maximum(-recovered-.0012,0)
theta=np.arctan2(ry,rx)
breaks=np.zeros_like(H)
for angle,radius in [(-2.25,.245),(.65,.27)]:
 delta=np.arctan2(np.sin(theta-angle),np.cos(theta-angle))
 breaks=np.maximum(breaks,.72*np.exp(-(delta/.24)**2-((r-radius)/.04)**2))
raised=maximum_filter(recovered,size=(max(3,int(.035/dy)),max(3,int(.035/dx))))
recovered=recovered*(1-breaks)+raised*breaks
knotmask=1-ss(.25,.48,np.sqrt((rx/.95)**2+(ry/1.05)**2))
B=recovered*(1-knotmask)
K=recovered*knotmask*.80

# C: keep successful irregular fracture shapes as an independent physical layer.
C=-current['cut'].astype(float)
core=1-ss(.10,.17,r)
C*=1-.55*core

# E: fine anatomy is restrained and remains complementary to the geometry.
fineH=H-gaussian_filter(H,(.0055/dy,.0055/dx))
E=.30*sample(fineH,Xs,Ys)

# F: retain the palette and roughness; only remap their intrinsic coordinates.
rgb0=np.asarray(Image.open(P/'H_resolved/albedo.png').convert('RGB'),float)[16:-16,16:-16]/255
rough0=np.asarray(Image.open(P/'H_resolved/roughness.png').convert('L'),float)[16:-16,16:-16]/255
rgb=np.stack([sample(rgb0[:,:,i],Xs,Ys) for i in range(3)],2)
rough=sample(rough0,Xs,Ys)
np.savez_compressed(D/'detail_layers.npz',broad=A.astype('float32'),medium=B.astype('float32'),knot=K.astype('float32'),fractures=C.astype('float32'),fine=E.astype('float32'),knot_mask=knotmask.astype('float32'))

for key,gain in [('Q_layers_soft',.70),('R_layers_full',1.0)]:
 out=W/key;out.mkdir(exist_ok=True)
 full=np.minimum(A+gain*B+K+C+E,0)
 assert full.min()>-.075
 geometry=gaussian_filter(full,(.0045/dy,.0045/dx))
 residual=full-geometry
 ny,nx=np.gradient(residual,dy,dx);normal=np.stack([-nx,ny,np.ones_like(nx)],2);normal/=np.linalg.norm(normal,axis=2)[:,:,None]
 def save(name,a):
  pads=((16,16),(16,16))+(((0,0),) if a.ndim==3 else ())
  Image.fromarray(np.uint8(np.clip(np.pad(a,pads,mode='edge'),0,1)*255+.5)).save(out/name)
 save('albedo.png',rgb);save('roughness.png',rough);save('normal.png',normal*.5+.5)
 np.savez_compressed(out/'surface.npz',height=geometry.astype('float32'))
 np.savez_compressed(out/'master_height.npz',height=full.astype('float32'))
 design=dict(source='Recovered H medium anatomy and readable knot, independent preserved P fractures, restrained fine detail',medium_gain=gain,knot_center=[kx,ky],knot_warp='Contract outer deformation, preserve inner core, interrupt two partial arcs',normal_split=.0045,height_min=float(full.min()),palette_and_roughness='Shared unchanged H values remapped to anatomy',independent_layers=str(D/'detail_layers.npz'),warp_min_dx=float(gx.min()),warp_min_dy=float(gy.min()))
 (out/'design.json').write_text(json.dumps(design,indent=2))
 print(key,float(full.min()),flush=True)
