from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import gaussian_filter,map_coordinates
D=Path(__file__).resolve().parent;OLD=D.parent/'lower_iron';old=np.load(OLD/'surface09/fields.npz');h,w=old['coarse'].shape;L,H=18.04,.5035;X,Y=np.meshgrid(np.linspace(0,L,w,dtype=np.float32),np.linspace(H,0,h,dtype=np.float32))
def ss(a,b,z):t=np.clip((z-a)/(b-a),0,1);return t*t*(3-2*t)
coarse=old['coarse'];fine=.60*old['fine']-.0009*old['pits'];raw=np.asarray(Image.open(D/'resources/BatteredMetal02/Height.png').convert('L'),dtype=np.float32)/255;raw=gaussian_filter(raw,1.2,mode='wrap');u=((X+.024*np.sin(X*4.5+Y*7))/.95%1)*(raw.shape[1]-1);v=((Y+.015*np.sin(X*3.1))/.95%1)*(raw.shape[0]-1);professional=map_coordinates(raw,[v,u],order=1,mode='wrap');professional=(professional-professional.mean())/max(float(professional.std()),1e-8)*float(coarse.std())+float(coarse.mean());professional=np.clip(professional,float(coarse.min()),float(coarse.max()))
# Identical contact protection is used in bump and physical displacement comparisons.
dist=np.minimum.reduce([abs(X-p) for p in [0,5.46,9.02,14.48,18.04]]);mask=ss(.17,.45,dist)*ss(.035,.075,np.minimum(Y,H-Y))
for seat in [2.73-1.1277,2.73+1.1234,9.02+2.73+1.1233,9.02+2.73-1.1277,7.24,16.26]:mask*=ss(.105,.17,np.hypot(X-seat,Y-.25175))
for name,medium in [('relief_old',coarse),('relief_battered',professional)]:
 F=D/name;F.mkdir(exist_ok=True);medium=medium*mask
 Image.fromarray(np.uint16(np.clip((medium+.008)/.010,0,1)*65535+.5)).save(F/'coarse16.png');Image.fromarray(np.uint16(np.clip((fine+.002)/.004,0,1)*65535+.5)).save(F/'fine16.png');Image.fromarray(np.uint8(mask*255+.5)).save(F/'contact_mask.png');np.savez_compressed(F/'fields.npz',coarse=medium,fine=fine,mask=mask);(F/'design.json').write_text(json.dumps(dict(source='Existing medium field' if name=='relief_old' else 'Official Battered Metal 02 1K height, 8 bit source interpolated into float field',coarse_encoding=[-.008,.010],fine_encoding=[-.002,.004],coarse_std_before_protection=float(coarse.std()),amplitude_matched_to_existing=True,tertiary_source_retained=True,tertiary_grain_fraction=.60,original_pits_unchanged=True,contact_protected=True),indent=2))
print('Prepared amplitude matched medium sources and independent fine relief')
