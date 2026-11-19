from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import gaussian_filter,maximum_filter,map_coordinates
W=Path(__file__).resolve().parent;P=W.parent;out=W/'L_sculpt_repair';out.mkdir(exist_ok=True)
original=np.load(P/'H_resolved/master_height.npz')['height'].astype(float)
h,w=original.shape;dx,dy=5.1/(w-1),1.3775/(h-1)
X,Y=np.meshgrid(np.linspace(-2.55,2.55,w),np.linspace(-.84,-2.2175,h))
scan=np.load(P/'C_scan/surface.npz')['height'].astype(float)
def ss(a,b,v):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
# Replace the closed core rings locally; preserve successful outer wood anatomy.
cx,cy=-1.18,-1.38
theta=np.arctan2((Y-cy)/.30,(X-cx)/.38)
r=np.sqrt(((X-cx+.14*(Y-cy))/.38)**2+((Y-cy)/.30)**2)
r/=1+.10*np.sin(3*theta)+.05*np.cos(5*theta)
repair=1-ss(.65,1.18,r)
replacement=-.005+.24*(scan-gaussian_filter(scan,(.025/dy,.11/dx)))
full=original*(1-repair)+replacement*repair

# Restore selected narrow bridges across existing channels, with irregular edges.
bridge=np.zeros_like(full)
patches=[(-2.04,-1.04,.13,.035),(-1.73,-1.13,.10,.038),(-.72,-1.14,.14,.040),(-2.11,-1.38,.12,.045),(-1.78,-1.53,.10,.034),(-.70,-1.64,.16,.043),(-1.96,-1.84,.13,.036),(-1.39,-1.88,.12,.038),(-.61,-2.0,.13,.045),(.65,-1.04,.14,.043),(1.23,-1.14,.12,.037),(1.86,-1.31,.17,.04),(.76,-1.48,.13,.04),(1.38,-1.64,.16,.035),(2.10,-1.83,.13,.043),(1.12,-1.98,.13,.035)]
for i,(x,y,rx,ry) in enumerate(patches):
 xx=(X-x)/rx;yy=(Y-y-.13*(X-x))/ry
 mask=np.clip(1-abs(xx)**2.5-abs(yy)**2,0,1)
 mask*=.78+.15*np.tanh(gaussian_filter(scan,(.012/dy,.022/dx))/.01)
 bridge=np.maximum(bridge,mask)
nearby=maximum_filter(full,size=(max(3,int(.065/dy)),max(3,int(.035/dx))))
full=full*(1-.82*bridge)+gaussian_filter(nearby,(.006/dy,.012/dx))*(.82*bridge)

# Irregular localized shear chips across ridge shoulders, not new continuous lines.
damage=np.zeros_like(full)
chips=[(-1.94,-1.20,.18,.033,.010,.16),(-1.67,-1.73,.20,.038,.014,-.18),(-.65,-1.09,.13,.028,.009,.11),(-1.77,-1.91,.15,.035,.011,.07),(.83,-1.15,.23,.035,.011,-.11),(1.52,-1.56,.24,.038,.014,.08),(2.05,-1.91,.19,.03,.009,-.10)]
for x,y,rx,ry,depth,slant in chips:
 xx=(X-x)/rx;yy=(Y-y-slant*(X-x))/ry
 footprint=np.clip(1-abs(xx),0,1)
 cut=np.clip(1-abs(yy),0,1)**.6*footprint
 damage=np.maximum(damage,depth*cut)
full-=damage
# One asymmetric checked pith with a small fork; no annular cut.
for a,b,width,depth in [((-1.21,-1.28),(-1.16,-1.40),.006,.014),((-1.16,-1.40),(-1.19,-1.50),.008,.018),((-1.16,-1.40),(-1.07,-1.45),.004,.009)]:
 a=np.array(a);v=np.array(b)-a;t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/np.dot(v,v),0,1);d=np.sqrt((X-a[0]-t*v[0])**2+(Y-a[1]-t*v[1])**2)
 full-=depth*np.clip(1-d/width,0,1)*np.sin(np.pi*t)**.7
full=np.minimum(full,0)
low=gaussian_filter(full,(.0045/dy,.0045/dx));res=full-low;gy,gx=np.gradient(res,dy,dx);n=np.stack([-gx,gy,np.ones_like(gx)],2);n/=np.linalg.norm(n,axis=2)[:,:,None]
rgb=np.asarray(Image.open(P/'H_resolved/albedo.png').convert('RGB'),float)[16:-16,16:-16]/255
rough=np.asarray(Image.open(P/'H_resolved/roughness.png').convert('L'),float)[16:-16,16:-16]/255
nearcolor=np.stack([gaussian_filter(rgb[:,:,i],(.03/dy,.08/dx)) for i in range(3)],2)
mask=np.maximum(repair*.5,bridge*.5)
rgb=rgb*(1-mask[:,:,None])+nearcolor*mask[:,:,None]
# Natural broad pigment variation stays independent of relief and lighting.
stain=.09*np.exp(-((X+1.88)/.3)**2-((Y+1.88)/.14)**2)-.06*np.exp(-((X-.72)/.42)**2-((Y+1.15)/.17)**2)
rgb*= (1-stain-.08*np.clip(damage/.014,0,1))[:,:,None]
rough=np.clip(rough+.035*np.clip(damage/.014,0,1),.55,.85)
def save(name,a):
 pads=((16,16),(16,16))+(((0,0),) if a.ndim==3 else ())
 Image.fromarray(np.uint8(np.clip(np.pad(a,pads,mode='edge'),0,1)*255+.5)).save(out/name)
save('albedo.png',rgb);save('normal.png',n*.5+.5);save('roughness.png',rough)
np.savez_compressed(out/'surface.npz',height=low.astype('float32'));np.savez_compressed(out/'master_height.npz',height=full.astype('float32'),repair=repair.astype('float32'),bridges=bridge.astype('float32'),damage=damage.astype('float32'))
(out/'design.json').write_text(json.dumps(dict(foundation='Preserved H master with local ring removal, channel bridges and shear chips',normal_split=.0045,ring_repair_area=float(np.mean(repair>.1)),bridge_area=float(np.mean(bridge>.1)),depth_min=float(full.min()),all_other_source_work_preserved=True),indent=2))
print('Local sculpt repair',float(full.min()),flush=True)
