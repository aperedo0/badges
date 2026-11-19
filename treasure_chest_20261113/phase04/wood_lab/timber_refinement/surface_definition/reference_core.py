from pathlib import Path
import numpy as np,json,sys,shutil
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter
from scipy.interpolate import CubicSpline
D=Path(__file__).resolve().parent;sys.argv=[sys.argv[0],'AT_hardwood_faces'];s=(D/'organize_knot.py').read_text().split('rng=')[0];exec(compile(s,'existing_core_boundary_solver','exec'));C=W/'AU_reference_knot';C.mkdir(exist_ok=True)
# Anatomical landmarks are traced from the owner image. Heights are an artistic interpretation.
points=np.array([(591,827),(582,829),(577,837),(576,845),(577,852),(583,859),(591,862),(599,860),(606,854),(609,846),(605,836),(599,831)],dtype='float32')
def local(p):return np.stack([-1.31+(p[:,0]-593)/31*.145,-1.35+(845-p[:,1])/28*.17],1)
p=local(points);t=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];t/=t[-1];curve=CubicSpline(t,p,bc_type='natural')(np.linspace(0,1,300)).astype('float32');xp=X[y0:y1,x0:x1];yp=Y[y0:y1,x0:x1];dist=np.full(xp.shape,np.inf,dtype='float32');progress=np.zeros_like(dist)
for i,(a,b) in enumerate(zip(curve[:-1],curve[1:])):
 v=b-a;u=np.clip(((xp-a[0])*v[0]+(yp-a[1])*v[1])/max(float(v@v),1e-8),0,1);d=(xp-a[0]-u*v[0])**2+(yp-a[1]-u*v[1])**2;better=d<dist;progress[better]=(i+u[better])/(len(curve)-1);dist=np.minimum(dist,d)
dist=np.sqrt(dist);width=.0055+.0015*np.sin(progress*11+.2)+.0008*np.sin(progress*25+.6)
def ss(a,b,q):q=np.clip((q-a)/(b-a),0,1);return q*q*(3-2*q)
growth=(1-ss(.42,1,dist/width))*ss(0,.08,progress)*(1-ss(.90,1,progress))
pith=Image.new('L',(x1-x0,y1-y0));dr=ImageDraw.Draw(pith);polygons=[[(591,835),(587,834),(582,839),(584,844),(581,849),(588,853),(592,851),(591,844)],[(596,837),(600,840),(603,846),(600,849),(595,847),(596,842)]]
for poly in polygons:
 q=local(np.array(poly,dtype='float32'));uv=[((x+2.55)/dx-x0,(-.84-y)/dy-y0) for x,y in q];dr.polygon(uv,fill=255)
pith=gaussian_filter(np.asarray(pith,dtype='float32')/255,(.0014/dy,.0014/dx));yr=(yp+1.35)/.17;line=-1.31+.0018*np.sin(yr*8)+.0011*np.sin(yr*17);sw=.0035+.0012*(.5+.5*np.sin(yr*5+.4));gate=ss(0,.2,1-abs(yr));split=np.exp(-((xp-line)/sw)**4)*gate
fine=np.load(D/'source_normal_fibers.npz')['addition'];target=body.copy();target[y0:y1,x0:x1]+=.0018*growth-.0015*pith-.014*split;target+=fine;full=np.minimum(H+(target-H)*core,0);addition=full-H;geo=np.load(A/'surface.npz')['height'];lo=gaussian_filter(addition,(.0038/dy,.0038/dx));lo=np.asarray(Image.fromarray(lo).resize((geo.shape[1],geo.shape[0]),Image.Resampling.BICUBIC),dtype='float32');np.savez_compressed(C/'surface.npz',height=np.minimum(geo+lo,0));np.savez_compressed(C/'master_height.npz',height=full,delta=src['delta']+addition)
color=np.asarray(Image.open(A/'albedo.png').convert('RGB'),dtype='float32')/255;rgb=color[32:-32,32:-32];patch=rgb[y0:y1,x0:x1].copy();intrinsic=harmonic(patch)*np.array([.96,.94,.92],dtype='float32')
R=W/'final_fibers/resources/raw_plank_wall';sourcebox=(1800,2525,1860,2570);photo=np.asarray(Image.open(next(R.glob('*diff_4k*'))).convert('RGB').crop(sourcebox).resize((x1-x0,y1-y0),Image.Resampling.BICUBIC),dtype='float32')/255;lum=np.maximum(photo@np.array([.2126,.7152,.0722],dtype='float32'),.02);pig=np.log(lum)-gaussian_filter(np.log(lum),(.018/dy,.018/dx));pig/=max(float(np.std(pig[cm>.6])),1e-8);intrinsic*=np.exp(.055*np.clip(pig,-2,2))[:,:,None];intrinsic*=1+.10*growth[:,:,None];intrinsic*=1-.23*pith[:,:,None];intrinsic*=1-.24*split[:,:,None];rgb[y0:y1,x0:x1]=patch*(1-cm[:,:,None])+intrinsic*cm[:,:,None]
rough=np.asarray(Image.open(A/'roughness.png').convert('L'),dtype='float32')/255;rr=np.asarray(Image.open(next(R.glob('*rough_2k*'))).convert('L').crop((900,1262,930,1285)).resize((x1-x0,y1-y0),Image.Resampling.BICUBIC),dtype='float32')/255;rr=(rr-np.mean(rr[cm>.6]))/max(float(np.std(rr[cm>.6])),1e-8);r=rough[32+y0:32+y1,32+x0:32+x1];r[:]=r*(1-cm)+np.clip(.665+.016*np.clip(rr,-2,2)+.020*pith-.014*growth,.57,.79)*cm
for name,a in [('albedo',color),('roughness',rough)]:Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).save(C/(name+'.png'))
shutil.copy2(A/'normal_masks.npz',C/'normal_masks.npz');np.savez_compressed(D/'reference_core_layers.npz',growth=growth,pith=pith,split=split,mask=cm)
d=json.loads((A/'design.json').read_text());d.update(source='AT organized body and natural fine fibers with owner reference guided inner growth contour and angular pith replacing the mismatched scan pith',reference_inner_growth_points=points.tolist(),reference_pith_polygons=polygons,reference_mapping=dict(center=[593,845],radii=[31,28],target_center=[-1.31,-1.35],target_radii=[.145,.17]),core_growth_height=.0018,core_pith_depth=.0015,source_pigment_healthy_box=sourcebox,core_source_geometry='Owner reference anatomical contour; artistic depth, not recovered depth',height_min=float(full.min()));(C/'design.json').write_text(json.dumps(d,indent=2));print('Prepared direct reference core',flush=True)
