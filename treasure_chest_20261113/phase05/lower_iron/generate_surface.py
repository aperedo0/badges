from pathlib import Path
import numpy as np,json
from scipy.ndimage import gaussian_filter,map_coordinates
from PIL import Image
D=Path(__file__).resolve().parent;F=D/'surface';F.mkdir(exist_ok=True);rng=np.random.default_rng(261116);w,h=8192,256;L,H=18.04,.5035;dx,dy=L/(w-1),H/(h-1);X,Y=np.meshgrid(np.linspace(0,L,w,dtype=np.float32),np.linspace(H,0,h,dtype=np.float32));height=np.zeros((h,w),np.float32);lip=height.copy()
# Individual irregular hammer impressions, with quiet spans and several scales.
for i in range(760):
 x=rng.uniform(0,L);y=rng.uniform(-.04,H+.04)
 if 2.0<x<2.55 and rng.random()<.6:continue
 a=rng.uniform(.025,.095);b=a*rng.uniform(.42,.95);angle=rng.uniform(-np.pi,np.pi);depth=rng.uniform(.001,.005)*rng.uniform(.6,1)
 if rng.random()<.15:a*=1.6;b*=1.4;depth*=.7
 radius=max(a,b)*1.15;u0=max(0,int((x-radius)/dx));u1=min(w,int((x+radius)/dx)+2);v0=max(0,int((H-y-radius)/dy));v1=min(h,int((H-y+radius)/dy)+2)
 if u1<=u0 or v1<=v0:continue
 xx=X[v0:v1,u0:u1]-x;yy=Y[v0:v1,u0:u1]-y;p=(np.cos(angle)*xx+np.sin(angle)*yy)/a;q=(-np.sin(angle)*xx+np.cos(angle)*yy)/b;r=np.sqrt(np.maximum(p*p+q*q+.20*p*q,0));shape=np.maximum(1-r*r,0)**1.7
 height[v0:v1,u0:u1]-=depth*shape;lip[v0:v1,u0:u1]+=.055*depth*np.exp(-((r-1)/.11)**2)
height=np.maximum(height,-.010)+lip
# Reuse professional physical surface data only for fine pitting and reflectance variation.
R=D/'resources/Metal055A';raw=np.asarray(Image.open(next(R.glob('*Displacement.png'))),dtype=np.float32);raw=(raw-raw.mean())/max(float(raw.std()),1e-8);fine_source=raw-gaussian_filter(raw,7,mode='wrap');srcrough=np.asarray(Image.open(next(R.glob('*Roughness.png'))).convert('L'),dtype=np.float32)/255
u=(X/.72%1)*(raw.shape[1]-1);v=(Y/.72%1)*(raw.shape[0]-1);fine=map_coordinates(fine_source,[v,u],order=1,mode='wrap');fine*=.00020/max(float(fine.std()),1e-8);fine=np.clip(fine,-.0007,.0007);roughsource=map_coordinates(srcrough,[v,u],order=1,mode='wrap')
noise=gaussian_filter(rng.standard_normal((h,w)).astype(np.float32),(7,45));noise=(noise-noise.mean())/max(float(noise.std()),1e-8);patch=np.clip(.5+.18*noise,0,1)
edge=np.minimum(Y,H-Y);breaks=gaussian_filter(rng.uniform(size=w).astype(np.float32),.032/dx);breaks=(breaks-breaks.min())/max(float(breaks.max()-breaks.min()),1e-8);width=.006+.014*breaks[None,:];wear=np.clip((width+.006-edge)/.009,0,1);wear=wear*wear*(3-2*wear);wear*=np.clip((breaks[None,:]-.15)/.42,0,1)
base=np.array([.058,.052,.047],np.float32)[None,None,:]*(.86+.24*patch[:,:,None]);exposed=np.array([.31,.29,.265],np.float32)[None,None,:];base=base*(1-wear[:,:,None])+exposed*wear[:,:,None];rough=np.clip(.50+.11*(roughsource-.5)+.05*(patch-.5)-.12*wear,.33,.67);metal=np.clip(.95-.10*(patch>.8),0,1)
def rgb(a):return np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)
Image.fromarray(np.uint8(np.clip(rgb(base),0,1)*255+.5)).save(F/'albedo.png');Image.fromarray(np.uint8(rough*255+.5)).save(F/'roughness.png');Image.fromarray(np.uint8(metal*255+.5)).save(F/'metallic.png');Image.fromarray(np.uint16(np.clip((height+fine+.012)/.016,0,1)*65535+.5)).save(F/'height16.png');Image.fromarray(np.uint8(wear*255+.5)).save(F/'wear.png');np.savez_compressed(F/'fields.npz',hammer=height,fine=fine,wear=wear,height=height+fine)
(F/'design.json').write_text(json.dumps(dict(seed=261116,atlas=[w,h],physical_perimeter=L,physical_height=H,height_encoding=dict(midlevel=.75,scale=.016),hammer_depth_range=[float(height.min()),float(height.max())],fine_source='ambientCG Metal055A',fine_rms=float(fine.std()),wear='Sparse variable width exposed neutral iron at existing upper and lower edges; no golden pigment or emission'),indent=2));print('Generated coordinated forging surface')
