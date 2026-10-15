"""Reference-shaped smooth loft definitions for the water reliefs."""
from pathlib import Path
import numpy as np,json
from scipy.ndimage import gaussian_filter1d
R=Path(__file__).resolve().parent
helper=R.parent/'achievement_coins_20261014/prepare.py'
ns={'__file__':str(helper)};exec(helper.read_text().split('def prepare(')[0],ns)
b=R/'clean';m=json.loads((b/'design.json').read_text());cx,cy,rad=m['circle'];scale=3.015/rad
outline=ns['bezier']((627,276),[
 ((647,277),(668,391),(724,464)),((783,545),(839,607),(836,702)),
 ((833,814),(756,891),(639,897)),((514,898),(418,813),(414,703)),
 ((403,608),(475,523),(530,453)),((591,369),(605,277),(627,276))],samples=120)
yy=np.linspace(276.03,896.96,110)
segments=[[(627,276),(647,277),(668,391),(724,464)],[(724,464),(783,545),(839,607),(836,702)],[(836,702),(833,814),(756,891),(639,897)],[(639,897),(514,898),(418,813),(414,703)],[(414,703),(403,608),(475,523),(530,453)],[(530,453),(591,369),(605,277),(627,276)]]
cc=[];rr=[]
for row in yy:
 xs=[]
 for controls in segments:
  q=np.asarray(controls,float);coeff=np.array([-q[0]+3*q[1]-3*q[2]+q[3],3*q[0]-6*q[1]+3*q[2],-3*q[0]+3*q[1],q[0]])
  poly=coeff[:,1].copy();poly[-1]-=row
  for root in np.roots(poly):
   if abs(root.imag)<1e-7 and -.000001<=root.real<=1.000001:
    t=root.real;xs.append(float(np.polyval(coeff[:,0],t)))
 cc.append((min(xs)+max(xs))/2);rr.append((max(xs)-min(xs))/2)
cc=np.array(cc);rr=np.array(rr)
m['features'][0]['blender_lathe']={'profile':np.c_[(cy-yy)*scale,(cc-cx)*scale,rr*scale][::-1].tolist(),'base':.09,'zscale':.57/(rr.max()*scale)}
for i,x,y,r,d in [(1,401,429,77,.31),(2,335,613,47,.20)]:
 yy=np.linspace(y-r+.08,y+r-.08,64);rr=np.sqrt(np.maximum(0,r*r-(yy-y)**2))
 m['features'][i]['blender_lathe']={'profile':np.c_[(cy-yy)*scale,np.full(len(yy),(x-cx)*scale),rr*scale][::-1].tolist(),'base':.09,'zscale':d/(r*scale)}
(b/'design.json').write_text(json.dumps(m,indent=2))
print('Smooth water and bubble profiles prepared on a working copy.')
