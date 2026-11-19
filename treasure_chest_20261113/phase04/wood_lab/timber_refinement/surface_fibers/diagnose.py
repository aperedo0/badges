from pathlib import Path
import numpy as np,json,hashlib
from scipy.ndimage import gaussian_filter
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;W=D.parent;P=W.parent
L=np.load(W/'grain_hierarchy/detail_layers.npz');H=np.load(W/'R_layers_full/master_height.npz')['height'];h,w=H.shape;dx,dy=5.1/(w-1),1.3775/(h-1)
X,Y=np.meshgrid(np.linspace(-2.55,2.55,w),np.linspace(-.84,-2.2175,h));core=np.hypot(X+1.31,Y+1.35)<.28
bay=(X>-2.12)&(X<-.35)&(Y>-1.98)&(Y<-.90)&~core
plate=bay&(L['medium']>-.0001)&(L['fractures']>-.001)&(L['knot_mask']<.05)
proof={'baseline_file_sha256':hashlib.sha256((W/'R_layers_full/master.blend').read_bytes()).hexdigest(),'shape':list(H.shape),'geometry_height_min_max':np.percentile(np.load(W/'R_layers_full/surface.npz')['height'],[0,50,100]).tolist(),'exposed_bay_quiet_plate_fraction':float(plate.sum()/bay.sum()),'quiet_plate_height_range_5_95':np.percentile(H[plate],[5,95]).tolist(),'fine_layer_rms_on_plates':float(np.std(L['fine'][plate])),'cause':'The recovered medium layer clips all positive band values to zero. Broad base is weak and H fine residual retained at 0.30. Large fractures have real geometry; shader normal strength is already one. Missing structure is source height on plateau regions, not merely normal strength or light.','limits':'Numerical values describe implementation and this approximate visible mask, not physical measurements inferred from the reference.'}
(D/'diagnosis.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
# Data sheets are diagnostics, not a texture authored from lit reference pixels.
ims=[]
for label,arr in [('Full height',H),('Medium layer',L['medium']),('Fine layer',L['fine']),('Cached wood surface',np.load(P/'C_scan/surface.npz')['height'])]:
 crop=arr[40:670,120:980];lo,hi=np.percentile(crop,[2,98]);g=np.uint8(np.clip((crop-lo)/max(hi-lo,1e-8),0,1)*255)
 im=Image.fromarray(g).convert('RGB').resize((600,440));ims.append((label,im))
out=Image.new('RGB',(1200,940),'#202020');draw=ImageDraw.Draw(out)
for i,(label,im) in enumerate(ims):x=(i%2)*600;y=(i//2)*470;out.paste(im,(x,y+28));draw.text((x+10,y+8),label,fill='white')
out.save(D/'height_diagnosis.jpg',quality=94)
