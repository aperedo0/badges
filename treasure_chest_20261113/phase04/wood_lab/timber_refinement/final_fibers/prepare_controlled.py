from pathlib import Path
import numpy as np,json,shutil
from scipy.ndimage import gaussian_filter,map_coordinates,grey_closing,median_filter
from PIL import Image
D=Path(__file__).resolve().parent;W=D.parent;A=W/'AB_carved_profiles';U=W/'U_scan_fibers';C=W/'AE_controlled_fibers';C.mkdir(exist_ok=True);full=np.load(A/'master_height.npz')['height'].astype(float);base=np.load(U/'master_height.npz')['height'].astype(float);geo=np.load(U/'surface.npz')['height'].astype(float);h,w=full.shape;dx,dy=5.1/(w-1),1.3775/(h-1);X,Y=np.meshgrid(np.linspace(-2.55,2.55,w),np.linspace(-.84,-2.2175,h));kx,ky=-1.31,-1.35;L=np.load(D/'structure_layers.npz');core=L['core'].astype(float);plate=L['plate'].astype(float);M=np.load(W/'grain_hierarchy/detail_layers.npz');cut=-M['fractures'].astype(float)
def ss(a,b,x):q=np.clip((x-a)/(b-a),0,1);return q*q*(3-2*q)
flowY=Y-.145*np.tanh((Y-ky)/.115)*np.exp(-((X-kx)/.44)**2)
def flow(a):return map_coordinates(a,[(flowY+.84)/-1.3775*(h-1),(X+2.55)/5.1*(w-1)],order=1,mode='reflect')
rng=np.random.default_rng(161127)
def noise(sy,sx):
 a=gaussian_filter(rng.normal(size=(h,w)),(sy/dy,sx/dx));return a/max(np.std(a),1e-8)
# Irregular finite directional fibers. Different frequencies use independent seeds.
breakup=ss(-.8,.8,noise(.025,.035));lamina=flow(noise(.0032,.035));sharp=np.clip(lamina-.18,-.6,1.8);sharp-=gaussian_filter(sharp,(.02/dy,.07/dx));raised=.0009*sharp*(.4+.6*flow(breakup));fiber=.00045*flow(noise(.0013,.012));micro=.00020*flow(noise(.0007,.0035));detail=(raised+fiber+micro)*plate
# Compressed core cells differ from longitudinal trunk fibers.
cells=noise(.008,.0018);cells=np.clip(cells,-1.8,1.8);detail+=.0012*cells*core
# Restore core continuity at the preexisting horizontal fracture, preserving its course outside the core.
opening=json.loads((W/'Y_broken_lamina/design.json').read_text())['horizontal_core_opening_y'];fill=.75*cut*core*np.exp(-((Y-opening)/.032)**2)*ss(.008,.025,abs(X-kx));detail+=fill
# Close the unwanted horizontal interruption only inside the existing core.
closure=np.maximum(grey_closing(full,size=(29,1))-full,0);corefill=.8*closure*core*ss(.008,.018,abs(X-kx));detail+=corefill
edge=np.minimum.reduce([2.35-abs(X),Y+2.16,-.8625-Y]);detail*=ss(.015,.07,edge);full=np.minimum(full+detail,0);delta=full-base;geometry=np.minimum(geo+gaussian_filter(delta,(.0038/dy,.0038/dx)),0)
np.savez_compressed(C/'master_height.npz',height=full.astype('float32'),delta=delta.astype('float32'));np.savez_compressed(C/'surface.npz',height=geometry.astype('float32'));np.savez_compressed(D/'final_directional_layers.npz',detail=detail.astype('float32'),fiber=fiber.astype('float32'),lamina=raised.astype('float32'),core=cells.astype('float32'),horizontal_fill=fill.astype('float32'))
# Independent fine intrinsic pigment and softer dielectric response on exposed fibers.
pig=flow(.12*noise(.0035,.025)+.065*noise(.012,.09));pig*=plate;pig+=.12*noise(.009,.003)*core
rgb=np.asarray(Image.open(A/'albedo.png').convert('RGB'),float)/255;rgb[16:-16,16:-16]*=np.exp(pig[:,:,None]-.5*.13**2)
corecolor=rgb[16:-16,16:-16];filtered=median_filter(corecolor,size=(29,1,1));cm=ss(.001,.005,corefill)*core;corecolor[:]=corecolor*(1-cm[:,:,None])+filtered*cm[:,:,None];corecolor*=1-core[:,:,None]*np.array([.08,.13,.12])
# A low frequency chestnut variation, independent from illumination and relief.
stain=flow(noise(.10,.32));t=ss(-.7,.8,stain);rgb[16:-16,16:-16]*=np.stack([1-.03*t,1-.08*t,1-.07*t],2)
rough=np.asarray(Image.open(A/'roughness.png').convert('L'),float)/255;rough[16:-16,16:-16]=np.clip(rough[16:-16,16:-16]+.025*flow(noise(.004,.03)),.51,.84)
for name,a in [('albedo',rgb),('roughness',rough)]:Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).save(C/(name+'.png'))
d=json.loads((A/'design.json').read_text());d.update(source='AB profile preserved with multiscale broken longitudinal fibers on raised formations and compressed knot endgrain',seed=161127,horizontal_core_continuity=True,major_grain_layout_preserved=True,fine_lamina_amplitude=.0009,local_core_horizontal_closure=True,normal_split=.0038,height_min=float(full.min()),core_center=[kx,ky]);(C/'design.json').write_text(json.dumps(d,indent=2));print('Prepared fine hierarchy',float(detail.min()),float(detail.max()),flush=True)
