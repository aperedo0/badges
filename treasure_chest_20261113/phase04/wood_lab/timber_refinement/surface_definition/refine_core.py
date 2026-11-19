from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
D=Path(__file__).resolve().parent;W=D.parent;A=W/'AH_aged_fibers';C=W/'AI_core_definition';C.mkdir(exist_ok=True);a=np.load(A/'master_height.npz');H=a['height'];delta=a['delta'];L=np.load(D/'layers.npz');core=L['core'];plate=L['plate'];h,w=H.shape;dx,dy=5.1/(w-1),1.3775/(h-1);X,Y=np.meshgrid(np.linspace(-2.55,2.55,w,dtype='float32'),np.linspace(-.84,-2.2175,h,dtype='float32'));rx,ry=X+1.31,Y+1.35
r=np.hypot((rx+.010)/.113,(ry-.004)/.135);theta=np.arctan2(ry/.135,(rx+.01)/.113);radius=.73+.035*np.sin(theta*3+.4)+.020*np.sin(theta*7);arc=np.exp(-((r-radius)/.035)**2);arc*=np.clip((np.sin(theta-.3)+.4)/.65,0,1)
add=-.0013*arc*core;full=np.minimum(H+add,0);newdelta=delta+add;geo=np.load(A/'surface.npz')['height']
lo=gaussian_filter(add,(.0038/dy,.0038/dx));lo=np.asarray(Image.fromarray(lo).resize((geo.shape[1],geo.shape[0]),Image.Resampling.BICUBIC),dtype='float32');np.savez_compressed(C/'surface.npz',height=np.minimum(geo+lo,0));np.savez_compressed(C/'master_height.npz',height=full,delta=newdelta)
color=np.asarray(Image.open(A/'albedo.png').convert('RGB'),dtype='float32')/255;rgb=color[32:-32,32:-32];rough=np.asarray(Image.open(A/'roughness.png').convert('L'),dtype='float32')/255
# Reconstruct intrinsic core color from its boundary, instead of blurring a transverse painted mark.
x0=int((-1.31-.18+2.55)/dx);x1=int((-1.31+.18+2.55)/dx)+1;y0=int((-.84+1.35-.21)/dy);y1=int((-.84+1.35+.21)/dy)+1;cm=core[y0:y1,x0:x1];mask=cm>.12;patch=rgb[y0:y1,x0:x1].copy();filled=patch.copy();filled[mask]=np.median(patch[mask],axis=0)
for _ in range(1300):
 avg=(np.roll(filled,1,0)+np.roll(filled,-1,0)+np.roll(filled,1,1)+np.roll(filled,-1,1))*.25;filled[mask]=avg[mask]
filled*=np.array([.88,.83,.82],dtype='float32');rgb[y0:y1,x0:x1]=patch*(1-cm[:,:,None])+filled*cm[:,:,None]
rng=np.random.default_rng(161145);pig=gaussian_filter(rng.normal(size=(h,w)).astype('float32'),(.0035/dy,.003/dx));pig/=max(float(np.std(pig[core>.6])),1e-8);pith=np.exp(-((rx+.018)/.043)**2-((ry-.010)/.056)**2);rgb*=np.exp(.12*np.clip(pig,-2,2)*core-.18*arc*core-.14*pith*core)[:,:,None]
for role,a in [('albedo',color),('roughness',rough)]:Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).save(C/(role+'.png'))
np.savez_compressed(C/'normal_masks.npz',core=core,plate=plate)
d=json.loads((A/'design.json').read_text());d.update(source='AH with local boundary reconstructed core pigment, one interrupted inner latewood arc and source gradient corrected normals',normal_policy='Actual source height gradient in reconstructed core; blend 0.7 on raised faces; inherited normal retained elsewhere',core_horizontal_pigment_mark_removed=True,extra_outer_growth_rings=False,height_min=float(full.min()));(C/'design.json').write_text(json.dumps(d,indent=2));print('Prepared localized core definition',flush=True)
