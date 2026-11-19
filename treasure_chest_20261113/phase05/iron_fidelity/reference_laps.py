from pathlib import Path
import numpy as np,json
from scipy.ndimage import gaussian_filter
from PIL import Image
D=Path(__file__).resolve().parent;F=D/'reference_laps';F.mkdir(exist_ok=True);w,h=8192,256;L,H=18.04,.5035;U,Y=np.meshgrid(np.linspace(0,L,w,dtype=np.float32),np.linspace(-1.714,-2.2175,h,dtype=np.float32));X=U-2.73;height=np.zeros((h,w),np.float32);wear=height.copy()
# Artist guided open forging laps from the corresponding reference bays. Depth is an artistic calibration.
paths=[([[-2.05,-1.91],[-1.88,-1.945],[-1.70,-1.87],[-1.56,-1.925],[-1.42,-1.895]],.00080,.010),([[-2.04,-2.10],[-1.87,-2.08],[-1.73,-2.11],[-1.56,-2.025],[-1.43,-2.045]],.00085,.009),([[-.94,-2.13],[-.81,-2.06],[-.65,-2.075],[-.44,-1.97]],.00085,.010),([[.49,-1.84],[.64,-1.865],[.79,-1.915],[.93,-1.86]],.00065,.008),([[.50,-2.11],[.72,-2.075],[.89,-2.13],[1.02,-2.085]],.00075,.009),([[1.41,-2.105],[1.59,-2.08],[1.72,-1.985],[1.90,-2.01],[2.08,-1.915]],.00090,.010)]
for points,depth,width in paths:
 p=np.array(points);lengths=np.linalg.norm(np.diff(p,axis=0),axis=1);total=lengths.sum();prior=0.;nearest=np.full_like(height,1e6);signed=np.zeros_like(height);progress=np.zeros_like(height)
 for a,b,length in zip(p[:-1],p[1:],lengths):
  v=b-a;t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/(length*length),0,1);dx=X-(a[0]+t*v[0]);dy=Y-(a[1]+t*v[1]);dist=np.hypot(dx,dy);choose=dist<nearest;nearest[choose]=dist[choose];signed[choose]=((v[0]*dy-v[1]*dx)/length)[choose];progress[choose]=((prior+t*length)/total)[choose];prior+=length
 taper=np.maximum(0,np.sin(np.pi*np.clip(progress,0,1)))**.65;broken=np.interp(progress,[0,.18,.36,.55,.73,.88,1],[0,.85,.25,1,.38,.7,0]);variation=.65+.35*np.interp(progress,[0,.25,.6,1],[.7,1,.8,.5]);ww=width*variation;cut=-depth*np.exp(-(nearest/np.maximum(ww,.001))**2)*taper*broken;lip=depth*.26*np.exp(-((nearest-ww*.95)/(ww*.48))**2)*np.exp(-(nearest/(ww*2))**8)*taper*broken;height+=cut+lip;wear=np.maximum(wear,np.maximum(lip,0)/max(depth*.26,1e-8)*.65)
for xc in [-1.1277,1.1234]:
 r=np.hypot(X-xc,Y+1.96575);t=np.clip((r-.105)/.065,0,1);t=t*t*(3-2*t);height*=t;wear*=t
height=gaussian_filter(height,(.6,.5));assert np.isfinite(height).all() and np.isfinite(wear).all();Image.fromarray(np.uint16(np.clip((height+.002)/.004,0,1)*65535+.5)).save(F/'height16.png');Image.fromarray(np.uint8(np.clip(wear,0,1)*255+.5)).save(F/'exposed_lips.png');np.savez_compressed(F/'fields.npz',height=height,exposed=wear);(F/'design.json').write_text(json.dumps(dict(paths=paths,source='Visual reference guided open shallow forge laps, not measured physical depth',uniform_patterns=False,hardware_contacts_protected=True,representation='Independent shallow normal relief and exposed convex lip mask'),indent=2));print('Prepared limited reference guided forge laps')
