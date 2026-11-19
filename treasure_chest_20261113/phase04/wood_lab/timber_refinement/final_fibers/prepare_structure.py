from pathlib import Path
import numpy as np,json,shutil
from PIL import Image
from scipy.ndimage import gaussian_filter,map_coordinates
D=Path(__file__).resolve().parent;W=D.parent;P=W.parent;root=P.parents[1];V=W/'V_lookdev_refinement';U=W/'U_scan_fibers'
base=np.load(U/'master_height.npz')['height'].astype(float);basegeo=np.load(U/'surface.npz')['height'].astype(float);R=np.load(W/'R_layers_full/master_height.npz')['height'].astype(float);oldadd=base-R;M=np.load(W/'grain_hierarchy/detail_layers.npz');L=np.load(W/'surface_fibers/surface_layers.npz');h,w=base.shape;dx,dy=5.1/(w-1),1.3775/(h-1);X,Y=np.meshgrid(np.linspace(-2.55,2.55,w),np.linspace(-.84,-2.2175,h));kx,ky=-1.31,-1.35;rx,ry=X-kx,Y-ky

def ss(a,b,v):
 q=np.clip((v-a)/(b-a),0,1);return q*q*(3-2*q)
def sample(a,x,y):return map_coordinates(a,[(y+.84)/-1.3775*(h-1),(x+2.55)/5.1*(w-1)],order=1,mode='reflect')
def norm(a,mask=None):
 region=a if mask is None else a[mask];return np.clip((a-np.median(region))/max(np.std(region),1e-8),-2.4,2.4)
flowY=Y-.145*np.tanh(ry/.115)*np.exp(-(rx/.44)**2)
plate=1-ss(.003,.014,-M['medium']-M['knot']);plate*=1-ss(.001,.012,-M['fractures']);core=1-ss(.80,1.12,np.hypot(rx/.145,ry/.17));plate*=1-core
edge=np.minimum.reduce([2.35-abs(X),Y+2.16,-.8625-Y]);boundary=ss(.012,.065,edge);plate*=boundary
# Preserve the broad height of every formation. Replace only the deficient internal band.
oldlow=gaussian_filter(oldadd,(.035/dy,.13/dx))
scan=np.load(W/'surface_fibers/normal_reconstruction.npz')['integrated'].astype(float)
scanband=gaussian_filter(scan,(.004/dy,.022/dx))-gaussian_filter(scan,(.038/dy,.17/dx));scanband=norm(sample(scanband,X,flowY))
# Build a nonperiodic directional detail library from visible wood in the owner's reference.
ref=np.asarray(Image.open(root/'reference.png').convert('RGB'),float)/255
boxes=[(930,650,1060,907),(480,645,615,780),(480,891,715,932)]
donors=[]
for x0,y0,x1,y1 in boxes:
 lum=ref[y0:y1,x0:x1]@np.array([.2126,.7152,.0722]);g=np.log(np.maximum(lum,.018));g=gaussian_filter(g,.65)-gaussian_filter(g,(3.5,8));donors.append(norm(g))
rng=np.random.default_rng(16117);ch,cw=174,612;acc=np.zeros((ch,cw));weights=np.zeros_like(acc)
for row in range(-12,ch+18,10):
 for col in range(-35,cw+40,24):
  donor=donors[int(rng.integers(len(donors)))];ph=int(rng.integers(14,26));pw=int(rng.integers(38,66));sy=int(rng.integers(0,donor.shape[0]-ph));sx=int(rng.integers(0,donor.shape[1]-pw));patch=donor[sy:sy+ph,sx:sx+pw].copy()
  if rng.random()<.5:patch=patch[:,::-1]
  yy=row+int(rng.integers(-3,4));xx=col+int(rng.integers(-7,8));a,b=max(0,yy),min(ch,yy+ph);c,d=max(0,xx),min(cw,xx+pw)
  if b<=a or d<=c:continue
  win=np.outer(np.hanning(ph+2)[1:-1],np.hanning(pw+2)[1:-1]);q=win[a-yy:b-yy,c-xx:d-xx];acc[a:b,c:d]+=patch[a-yy:b-yy,c-xx:d-xx]*q;weights[a:b,c:d]+=q
quilting=acc/np.maximum(weights,1e-7);quilting-=gaussian_filter(quilting,(3.5,12));coords=np.meshgrid(np.linspace(0,ch-1,h),np.linspace(0,cw-1,w),indexing='ij');referenceband=map_coordinates(quilting,coords,order=3,mode='reflect');referenceband=norm(sample(referenceband,X,flowY))
# Restrained end grain interpretation of the actual reference core, without its broad illumination.
lum=ref[:,:,0]*.2126+ref[:,:,1]*.7152+ref[:,:,2]*.0722;log=np.log(np.maximum(lum,.018));band=gaussian_filter(log,1.0)-gaussian_filter(log,4.3)
cu=590+rx/.145*30;cv=844-ry/.17*39;coreband=map_coordinates(band,[cv,cu],order=1,mode='nearest');coreband=norm(coreband,core>.8);corefine=.0017*coreband
# Retain and slightly define the existing approximately vertical check, never a new crack.
check=L['central_check'].astype(float);check_delta=.20*check
core_replacement=gaussian_filter(oldadd,(.024/dy,.024/dx))+corefine+check+check_delta
core_delta=core*(core_replacement-oldadd)*boundary
for key,field in [('W_scan_lamina',scanband),('X_reference_lamina',referenceband)]:
 # Uneven flat fiber plates at three scales, not sinusoidal inflated ridges.
 strata=.0020*ss(-1.2,-.80,field)+.0026*ss(-.18,.16,field)+.0020*ss(.70,1.05,field)-.0066
 strata=gaussian_filter(strata,(.0011/dy,.002/dx));strata-=gaussian_filter(strata,(.035/dy,.13/dx));strata+=oldlow
 delta=plate*(strata-oldadd)+core_delta;full=np.minimum(base+delta,0);delta=full-base;geometry=np.minimum(basegeo+gaussian_filter(delta,(.0038/dy,.0038/dx)),0)
 C=W/key;C.mkdir(exist_ok=True)
 np.savez_compressed(C/'surface.npz',height=geometry.astype('float32'));np.savez_compressed(C/'master_height.npz',height=full.astype('float32'),delta=delta.astype('float32'))
 for role in ['albedo','roughness']:shutil.copy2(V/(role+'.png'),C/(role+'.png'))
 (C/'design.json').write_text(json.dumps(dict(source='V foundation; secondary internal fiber band replaced, medium anatomy and primary fracture centers retained',detail_source='Cached CC0 normal assisted laminar plates' if key.startswith('W_') else 'Directional quilt of fine reference wood detail; artistic relief interpretation, not a scan',reference_donor_boxes=boxes,seed=16117,secondary_plate_steps=[.0020,.0026,.0020],core_source='Reference end grain band with broad illumination removed; existing center and proportions',core_center=[kx,ky],core_radii=[.145,.17],normal_split=.0038,normal_method='Transport baseline shading into new geometric tangent frame, add only new height derivatives',material='V albedo and roughness unchanged for structure control',height_min=float(full.min()),delta_min=float(delta.min()),delta_max=float(delta.max())),indent=2))
np.savez_compressed(D/'structure_layers.npz',scan=scanband.astype('float32'),reference=referenceband.astype('float32'),plate=plate.astype('float32'),core=core.astype('float32'),core_detail=corefine.astype('float32'))
print('Prepared two independent internal fiber sources with shared core and unchanged V material')
