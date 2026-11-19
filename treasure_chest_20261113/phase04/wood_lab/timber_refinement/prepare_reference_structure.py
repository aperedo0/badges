from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,gaussian_filter
from scipy.interpolate import PchipInterpolator
W=Path(__file__).resolve().parent;P=W.parent
data=np.load(W/'I_structure/master_height.npz');base=data['height'].astype(float)+data['fracture'];h,w=base.shape
dx,dy=5.1/(w-1),1.3775/(h-1)
X,Y=np.meshgrid(np.linspace(-2.55,2.55,w),np.linspace(-.84,-2.2175,h))
# Artist traced centerlines from the actual reference crop, not brightness as relief.
traces=[
 [(0,40),(90,40),(160,25),(240,15),(320,15),(430,32),(545,45)],
 [(10,75),(110,67),(200,44),(280,35),(360,48),(475,68)],
 [(0,112),(92,98),(166,77),(232,67),(290,65),(350,73),(460,101)],
 [(5,150),(75,139),(145,118),(220,95),(280,95),(360,111),(475,143)],
 [(0,183),(85,180),(135,153),(198,132),(255,122),(300,124),(395,148),(485,185)],
 [(0,218),(80,220),(140,189),(190,164),(253,153),(320,166),(430,199)],
 [(5,251),(88,253),(143,225),(192,201),(240,183),(300,187),(360,211),(470,247)],
 [(0,288),(85,290),(145,273),(205,260),(255,246),(315,237),(370,245),(444,266),(510,282)],
 [(0,328),(68,334),(133,322),(192,306),(225,279),(245,263)],
 [(0,365),(65,366),(122,351),(165,329),(185,301),(202,280)],
 [(412,282),(448,313),(450,360),(419,395),(382,418)],
 [(5,395),(80,396),(150,377),(202,391),(252,416),(310,426),(375,427),(440,416),(540,400)],
 [(0,426),(82,427),(142,421),(206,437),(270,453),(339,458),(418,450),(520,433)],
 [(0,465),(78,465),(154,456),(207,470),(290,485),(353,487),(421,482),(530,472)],
 [(2,495),(84,504),(172,492),(224,500),(300,516),(389,521),(465,506),(540,502)],
 [(0,534),(80,536),(180,525),(270,538),(350,539)],
 [(365,270),(375,320),(370,355),(390,385)],
 [(375,320),(345,335),(328,350)]]
paths=[]
for i,points in enumerate(traces):
    a=np.array(points,float);a[:,0]=(a[:,0]-350)/531-1.18;a[:,1]=-(a[:,1]-325)/531-1.38
    if i not in [10,16,17]:
        if i%3!=1:a=np.vstack([[-2.48,a[0,1]+(.012 if i%2 else -.014)],a])
        if i in [2,4,6,7,11,13,14]:
            a=np.vstack([a,[-.20,a[-1,1]+.025],[.35,a[-1,1]+.012],[.9,a[-1,1]+.035],[1.5,a[-1,1]+.015],[2.45,a[-1,1]+.03]])
    paths.append(a)
# Unequal partial longitudinal fractures on the quieter right panel.
paths += [np.array(a) for a in [[(.45,-.99),(.83,-1.0),(1.15,-.98),(1.52,-1.01),(2.30,-.99)],[(.65,-1.36),(1.02,-1.34),(1.25,-1.38),(1.8,-1.37),(2.35,-1.4)],[(1.2,-1.86),(1.5,-1.83),(1.9,-1.85),(2.4,-1.82)],[(.6,-2.04),(.85,-2.02),(1.24,-2.05),(1.65,-2.03)]]]
fract=np.zeros_like(base);shoulders=np.zeros_like(base);seed_widths=[.010,.009,.012,.010,.014,.011,.012,.019,.013,.010,.012,.015,.011,.014,.010,.012,.006,.005]
overlay=Image.open(P.parents[1]/'phase03/wood_sample44/reference_wood_close.png').convert('RGB');draw=ImageDraw.Draw(overlay)
for a in traces:draw.line(a,fill=(20,230,200),width=2)
overlay.save(W/'reference_fracture_trace.png')
for i,a in enumerate(paths):
    length=np.r_[0,np.cumsum(np.linalg.norm(np.diff(a,axis=0),axis=1))]
    t=np.linspace(0,1,max(40,int(length[-1]/.0025)))
    xy=PchipInterpolator(length/length[-1],a,axis=0)(t)
    tangent=np.gradient(xy,axis=0);tangent/=np.maximum(np.linalg.norm(tangent,axis=1)[:,None],1e-9)
    px=np.round((xy[:,0]+2.55)/5.1*(w-1)).astype(int);py=np.round((-.84-xy[:,1])/1.3775*(h-1)).astype(int)
    valid=(px>=0)&(px<w)&(py>=0)&(py<h);px,py,t,xy,tangent=px[valid],py[valid],t[valid],xy[valid],tangent[valid]
    if not len(px):continue
    seed=np.ones((h,w),bool);seed[py,px]=False
    distance,indices=distance_transform_edt(seed,sampling=(dy,dx),return_indices=True)
    phase=np.zeros((h,w));phase[py,px]=t;phase=phase[tuple(indices)]
    width=seed_widths[i] if i<len(seed_widths) else [.010,.014,.011,.009][i-len(seed_widths)]
    width=width*(.65+.45*np.sin(phase*12+i)**2)
    taper=np.sin(np.pi*phase)**.35
    interruption=1-.94*np.exp(-((phase-(.26+.12*(i%4)))/.022)**4) if i%3!=0 else 1
    prof=np.clip(1-distance/np.maximum(width,1e-6),0,1)
    depth=[.012,.010,.016,.013,.019,.014,.017,.025,.015,.012,.018,.022,.014,.018,.014,.018,.021,.012][i] if i<18 else [.013,.018,.014,.012][i-18]
    fract=np.maximum(fract,depth*prof**.72*taper*interruption)
    tx=np.zeros((h,w));ty=tx.copy();cx=tx.copy();cy=tx.copy()
    tx[py,px]=tangent[:,0];ty[py,px]=tangent[:,1];cx[py,px]=xy[:,0];cy[py,px]=xy[:,1]
    side=tx[tuple(indices)]*(Y-cy[tuple(indices)])-ty[tuple(indices)]*(X-cx[tuple(indices)])
    # A broad broken shoulder, with genuinely flatter wood between selected cuts.
    lip=np.clip(1-abs((distance-width*1.9)/(width*1.15)),0,1)
    lip*=side>0 if i%2 else side<0
    shoulders=np.maximum(shoulders,.003*lip*taper*interruption)
full=np.minimum(base-fract+shoulders,0)
# Broad medium detail stays geometric; complementary fine detail remains normal.
low=gaussian_filter(full,(.004/dy,.004/dx));res=full-low;gy,gx=np.gradient(res,dy,dx);normal=np.stack([-gx,gy,np.ones_like(gx)],2);normal/=np.linalg.norm(normal,axis=2)[:,:,None]
out=W/'K_reference_fractures';out.mkdir(exist_ok=True)
rgb=np.asarray(Image.open(W/'I_structure/albedo.png').convert('RGB'),float)[16:-16,16:-16]/255
rough=np.asarray(Image.open(W/'I_structure/roughness.png').convert('L'),float)[16:-16,16:-16]/255
rgb*=(1-.08*np.clip(fract/.022,0,1))[:,:,None];rough=np.clip(rough+.04*np.clip(fract/.022,0,1),.55,.85)
def save(name,a):
    pads=((16,16),(16,16))+(((0,0),) if a.ndim==3 else ())
    Image.fromarray(np.uint8(np.clip(np.pad(a,pads,mode='edge'),0,1)*255+.5)).save(out/name)
save('albedo.png',rgb);save('roughness.png',rough);save('normal.png',normal*.5+.5)
np.savez_compressed(out/'surface.npz',height=low.astype('float32'));np.savez_compressed(out/'master_height.npz',height=full.astype('float32'),fracture=fract.astype('float32'))
(out/'design.json').write_text(json.dumps(dict(source='Manually interpreted reference fracture centerlines with rebuilt cross sections, cached scanned supporting timber',paths=len(paths),depth_min=float(full.min()),normal_split=.004,not_reference_brightness_height=True),indent=2))
print('Prepared reference structural reconstruction',len(paths),float(full.min()),flush=True)
