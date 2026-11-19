from pathlib import Path
import numpy as np,json,shutil,sys
from scipy.ndimage import gaussian_filter,map_coordinates
from PIL import Image
D=Path(__file__).resolve().parent;W=D.parent;A=W/(sys.argv[1] if len(sys.argv)>1 else 'AK_cohesive_grain');C=W/'AL_organized_endgrain';C.mkdir(exist_ok=True);src=np.load(A/'master_height.npz');H=src['height'];h,w=H.shape;dx,dy=5.1/(w-1),1.3775/(h-1);X,Y=np.meshgrid(np.linspace(-2.55,2.55,w,dtype='float32'),np.linspace(-.84,-2.2175,h,dtype='float32'));rx,ry=X+1.31,Y+1.35
masks=np.load(A/'normal_masks.npz');core=masks['core'];radius=np.hypot(rx/.145,ry/.17);theta=np.arctan2(ry/.17,(rx+.006)/.145)
x0=int((-1.31-.18+2.55)/dx);x1=int((-1.31+.18+2.55)/dx)+1;y0=int((-.84+1.35-.21)/dy);y1=int((-.84+1.35+.21)/dy)+1;cm=core[y0:y1,x0:x1];mask=cm>.12
# Recover the existing core body from its boundary. New endgrain is organized independently.
def harmonic(patch):
 a=patch.copy();a[mask]=np.median(patch[mask],axis=0)
 for _ in range(1500):
  avg=(np.roll(a,1,0)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1))*.25;a[mask]=avg[mask]
 return a
body=H.copy();p=H[y0:y1,x0:x1];filled=harmonic(p);filled+=np.clip(np.mean(p[cm>.7])-np.mean(filled[cm>.7]),-.002,.002)*cm;body[y0:y1,x0:x1]=filled
rng=np.random.default_rng(161153)
def polar_noise(sr,st):
 n=rng.normal(size=(320,1024)).astype('float32');n=gaussian_filter(n,(sr/.20*320,st/.80*1024),mode=('reflect','wrap'));n-=gaussian_filter(n,(.025/.20*320,.04/.80*1024),mode=('reflect','wrap'));n/=max(float(n.std()),1e-8)
 rr=radius*240+.9*np.sin(theta*5);tt=(theta+np.pi)/(2*np.pi)*1024+2*np.sin(radius*8);return map_coordinates(n,[np.clip(rr,0,319),tt%1024],order=1,mode='grid-wrap')
fiber=np.clip(polar_noise(.0023,.013),-2.2,2.2);micro=np.clip(polar_noise(.0012,.005),-2,2)
# One incomplete inner latewood formation, with irregular spacing. No regular concentric ring train.
arc_radius=.64+.040*np.sin(theta*3+.4)+.022*np.sin(theta*7);arc=np.exp(-((radius-arc_radius)/.050)**2);sector=np.clip((np.sin(theta-.05)+.5)/.75,0,1);arc*=sector
pith=np.exp(-((rx+.016)/.035)**2-((ry-.006)/.052)**2)
yrel=ry/.17;line=-1.31+.0018*np.sin(yrel*8)+.0011*np.sin(yrel*17);width=.0035+.0012*(.5+.5*np.sin(yrel*5+.4));gate=np.clip((1-abs(yrel))/.20,0,1);gate=gate*gate*(3-2*gate);check=-.009*np.exp(-((X-line)/width)**4)*gate
core_height=.00034*fiber+.00014*micro-.0015*arc-.0007*pith+check
new=np.minimum(H+(body+core_height-H)*core,0);add=new-H;geo=np.load(A/'surface.npz')['height'];lo=gaussian_filter(add,(.0038/dy,.0038/dx));lo=np.asarray(Image.fromarray(lo).resize((geo.shape[1],geo.shape[0]),Image.Resampling.BICUBIC),dtype='float32');np.savez_compressed(C/'surface.npz',height=np.minimum(geo+lo,0));np.savez_compressed(C/'master_height.npz',height=new,delta=src['delta']+add)
color=np.asarray(Image.open(A/'albedo.png').convert('RGB'),dtype='float32')/255;rgb=color[32:-32,32:-32];patch=rgb[y0:y1,x0:x1].copy();intrinsic=harmonic(patch);intrinsic*=np.array([.94,.91,.90],dtype='float32');rgb[y0:y1,x0:x1]=patch*(1-cm[:,:,None])+intrinsic*cm[:,:,None]
pig=np.clip(polar_noise(.004,.019),-2,2);rgb*=np.exp((.075*pig-.12*arc-.12*pith)*core)[:,:,None]
Image.fromarray(np.uint8(np.clip(color,0,1)*255+.5)).save(C/'albedo.png');shutil.copy2(A/'roughness.png',C/'roughness.png');shutil.copy2(A/'normal_masks.npz',C/'normal_masks.npz');np.savez_compressed(D/'endgrain_layers.npz',fiber=fiber,arc=arc,central_split=check,core_mask=core)
d=json.loads((A/'design.json').read_text());d.update(source='Preserved larger formations with organized short endgrain fibers, one interrupted inner latewood arc and clearer existing vertical split',core_new_detail_policy='Replace uniform core texture, not increase feature count',core_center=[-1.31,-1.35],core_radii=[.145,.17],split_halfwidth_range=[.0035,.0047],core_fiber_amplitude=.00034,height_min=float(new.min()));(C/'design.json').write_text(json.dumps(d,indent=2));print('Prepared organized knot from',A.name,flush=True)
