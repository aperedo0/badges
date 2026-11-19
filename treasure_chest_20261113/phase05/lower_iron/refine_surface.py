from pathlib import Path
import numpy as np,json,shutil
from scipy.ndimage import gaussian_filter
from PIL import Image
D=Path(__file__).resolve().parent;A=D/'surface';F=D/'surface03';F.mkdir(exist_ok=True);old=np.load(A/'fields.npz');fine=old['fine'];h,w=fine.shape;L,H=18.04,.5035;dx,dy=L/(w-1),H/(h-1);X,Y=np.meshgrid(np.linspace(0,L,w,dtype=np.float32),np.linspace(H,0,h,dtype=np.float32));field=np.zeros_like(fine);rng=np.random.default_rng(261117)
# Unequal polygonal planishing impressions replace the rounded cups.
for i in range(480):
 x=rng.uniform(0,L);y=rng.uniform(-.025,H+.025);a=rng.uniform(.035,.115);b=a*rng.uniform(.5,1);angle=rng.uniform(-np.pi,np.pi);depth=rng.uniform(.0012,.0038)
 if 2.0<x<2.55 and rng.random()<.65:continue
 if rng.random()<.12:a*=1.35;b*=1.25;depth*=.7
 radius=max(a,b)*1.5;u0=max(0,int((x-radius)/dx));u1=min(w,int((x+radius)/dx)+2);v0=max(0,int((H-y-radius)/dy));v1=min(h,int((H-y+radius)/dy)+2)
 if u1<=u0 or v1<=v0:continue
 xx=X[v0:v1,u0:u1]-x;yy=Y[v0:v1,u0:u1]-y;p=(np.cos(angle)*xx+np.sin(angle)*yy)/a;q=(-np.sin(angle)*xx+np.cos(angle)*yy)/b;r=np.full_like(p,-10);count=int(rng.integers(5,8))
 for k in range(count):
  phi=(k+rng.uniform(-.12,.12))*2*np.pi/count;radius_k=rng.uniform(.78,1.1);r=np.maximum(r,(np.cos(phi)*p+np.sin(phi)*q)/radius_k)
 t=np.clip((1-r)/.23,0,1);t=t*t*(3-2*t);z=-depth*(.86+.14*np.maximum(1-r,0)) *t;field[v0:v1,u0:u1]=np.minimum(field[v0:v1,u0:u1],z)
field=gaussian_filter(field,(.0012/dy,.0012/dx));coverage=np.clip(-field/.0015,0,1);fine=fine*(.12+.18*coverage);wear=old['wear']*.82
base=np.array([.066,.059,.053],np.float32)[None,None,:];rough=np.asarray(Image.open(A/'roughness.png'),dtype=np.float32)/255;variation=gaussian_filter(np.asarray(Image.open(A/'metallic.png'),dtype=np.float32)/255,(5,25));patch=.94+.08*variation;base=base*patch[:,:,None]*(1-wear[:,:,None])+np.array([.30,.28,.25],np.float32)[None,None,:]*wear[:,:,None];col=np.where(base<=.0031308,12.92*base,1.055*np.maximum(base,0)**(1/2.4)-.055)
Image.fromarray(np.uint8(np.clip(col,0,1)*255+.5)).save(F/'albedo.png');Image.fromarray(np.uint8(np.clip(rough-.015,0,1)*255+.5)).save(F/'roughness.png');shutil.copy2(A/'metallic.png',F/'metallic.png');Image.fromarray(np.uint8(wear*255+.5)).save(F/'wear.png');Image.fromarray(np.uint16(np.clip((field+fine+.012)/.016,0,1)*65535+.5)).save(F/'height16.png');np.savez_compressed(F/'fields.npz',hammer=field,fine=fine,wear=wear,height=field+fine)
(F/'design.json').write_text(json.dumps(dict(source='02 forged',correction='Broad polygonal planishing, quiet faces and localized fine pitting',fine_rms=float(fine.std()),hammer_min=float(field.min()),seed=261117,exposed_color_linear=[.30,.28,.25],edge_color='Neutral warm iron, no gold or emission'),indent=2));print('Prepared sparse polygonal planishing')
