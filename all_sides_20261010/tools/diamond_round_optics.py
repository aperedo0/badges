from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
ROOT=Path(__file__).resolve().parents[1];w=Path(json.loads((ROOT/'manifest.json').read_text())['diamond']['work']);out=w/'candidates/04';S=1024
d=np.load(w/'candidates/03/optical_geometry.npz');p=d['source_points'];f=d['source_faces'];lo=p[f].reshape(-1,3).min(0);hi=p[f].reshape(-1,3).max(0)
theta=(np.arange(S)+.5)/S*2*np.pi-np.pi;y=2.34860635-(np.arange(S)+.5)/S*(2.34860635+2.455)
r=np.interp(y,[-2.455,-1.72,.78,.88,1.60,2.34860635],[0,.70,3.12,3.12,2.13,1.38])
# Each broad face uses the matching optical field from its nearest viewing quadrant.
# The transitions occur at real facet boundaries, never across a flat plane.
phi=np.floor(theta/(np.pi/2)+.5)*(np.pi/2);x=r[:,None]*np.sin(theta[None,:]-phi[None,:]);yy=np.broadcast_to(y[:,None],x.shape)
sx=(x-lo[0])/(hi[0]-lo[0])*(S-1);sy=(hi[1]-yy)/(hi[1]-lo[1])*(S-1)
for name in ['color.png','emissive.png']:
 im=np.asarray(Image.open(next((w/'candidates/03/usd').rglob(name))).convert('RGB'),float)/255;im=np.where(im<=.04045,im/12.92,((im+.055)/1.055)**2.4)
 field=np.stack([map_coordinates(im[...,k],[sy,sx],order=1,mode='nearest') for k in range(3)],-1)
 encoded=np.where(field<=.0031308,field*12.92,1.055*np.maximum(field,0)**(1/2.4)-.055)
 Image.fromarray(np.uint8(np.clip(encoded,0,1)*255+.5)).save(next((out/'usd').rglob(name)),optimize=True)
(out/'optics.json').write_text(json.dumps({'method':'Angular/height chart with reference optics oriented toward each of four quadrants. Quadrant transitions align with real facet boundaries; each side receives the full blue crystal field rather than a collapsed side-on projection.','source':'Installed blue optics, reprojected from candidate 03 field.','size':S},indent=2)+'\n')
print('Round optics generated without collapsed side projection.')
