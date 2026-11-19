from pathlib import Path
import numpy as np,json,shutil
from scipy.ndimage import gaussian_filter
from PIL import Image
D=Path(__file__).resolve().parent;old=np.load(D/'surface/fields.npz');angular=np.load(D/'surface03/fields.npz')['hammer'];h,w=angular.shape;dx,dy=18.04/(w-1),.5035/(h-1);rng=np.random.default_rng(261119);hy,hx=np.gradient(gaussian_filter(angular,(.0015/dy,.002/dx)),dy,dx);edge=np.hypot(hx,hy);edge=np.clip((edge-.018)/.12,0,1)
mask=gaussian_filter(rng.standard_normal((h,w)).astype(np.float32),(5,24));mask=(mask-mask.mean())/max(float(mask.std()),1e-8);mask=np.clip((mask+.15)/.8,0,1);broken=edge*mask;broken=gaussian_filter(broken,(.0012/dy,.0012/dx));fine=old['fine']*.16
for name,etched,forming in [('surface05',.0006,.16),('surface06',0,.38)]:
 F=D/name;F.mkdir(exist_ok=True);full=old['hammer']*forming-float(etched)*broken+fine
 for file in ['albedo.png','roughness.png','metallic.png','wear.png']:shutil.copy2(D/'surface04'/file,F/file)
 Image.fromarray(np.uint16(np.clip((full+.012)/.016,0,1)*65535+.5)).save(F/'height16.png');np.savez_compressed(F/'fields.npz',coarse=old['hammer']*forming,broken_scale=-float(etched)*broken,fine=fine,height=full,wear=old['wear']);(F/'design.json').write_text(json.dumps(dict(change='Quiet forged planes with sparse surface damage',broken_scale_depth=etched,forming_fraction=forming,fine_rms=float(fine.std()),no_closed_stamp_faces=True,source='Existing fields and free professional fine pitting'),indent=2))
print('Prepared broken shallow scale and quiet hammer alternatives')
