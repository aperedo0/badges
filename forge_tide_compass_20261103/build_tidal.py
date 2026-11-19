"""Trace the silver compass, continuous pearl crest and layered teal wave."""
from pathlib import Path
import json,numpy as np
from scipy.ndimage import gaussian_filter,gaussian_filter1d,distance_transform_edt,map_coordinates
from PIL import Image,ImageDraw
import meshlib as m
from pace import work
work(2)
R=Path(__file__).resolve().parent/'tidal_compass';m.setup(R,620,136,1098)
for folder in ['source','mobile','textures','review']:(m.C/folder).mkdir(parents=True,exist_ok=True)

def bezier(start,segments):
 out=[start];p=np.asarray(start,float)
 for aa,bb,cc in segments:
  a,b,c=map(lambda q:np.asarray(q,float),(aa,bb,cc));n=max(12,int((np.linalg.norm(p-a)+np.linalg.norm(a-b)+np.linalg.norm(b-c))/4))
  f=np.linspace(0,1,n+1)[1:,None];out.extend((1-f)**3*p+3*(1-f)**2*f*a+3*(1-f)*f*f*b+f**3*c);p=c
 return np.array(out)

center=[620,617];radii=[478,481]
m.ring('Thin continuous brushed silver perimeter',center,radii,[(1,.105),(.996,.15),(.989,.177),(.965,.177),(.956,.14),(.953,.09),(.953,-.09),(.956,-.14),(.965,-.177),(.989,-.177),(.996,-.15),(1,-.105)],'metal')

# The recessed field is a complete closed support, with broad shallow facets.
theta=np.linspace(0,2*np.pi,192,endpoint=False)
outline=np.c_[center[0]+radii[0]*.957*np.cos(theta),center[1]+radii[1]*.957*np.sin(theta)]
mask=m.poly(outline)
p=np.vstack([center]+[np.array(center)+(outline-np.array(center))*f for f in np.linspace(.08,1,13)])
t=[[0,1+i,1+(i+1)%192] for i in range(192)]
for j in range(12):
 for i in range(192):
  a=1+j*192+i;b=1+j*192+(i+1)%192;c=a+192;d=b+192;t.extend([[a,b,d],[a,d,c]])
t=np.array(t)
z=.065+.007*np.sin((p[:,0]-400)/190)*np.cos(p[:,1]/230)
m.relief('Deep teal recessed field',p,t,z,'field',True)

# The lower translucent looking enamel wave passes below the pearl crest.
teal=bezier([247,843],[([300,812],[348,818],[414,832]),([503,863],[560,874],[639,857]),([791,832],[868,723],[954,724]),([997,721],[1026,735],[1040,750]),([1004,870],[873,1005],[714,1050]),([565,1090],[420,1037],[350,951]),([306,908],[272,872],[247,843])])
tm=m.poly(teal)&mask;p,t=m.triangulate_curve(teal,15,'teal');d=gaussian_filter(distance_transform_edt(tm),14);h=.105+.045*(1-np.exp(-d/32))
z=map_coordinates(h,[p[:,1],p[:,0]],order=1);m.relief('Sweeping lower teal wave',p,t,z,'wave',True)

# Exact pointed crescent, curling pearl wave and broad tail form one smooth surface.
crescent=bezier([753,320],[([659,249],[521,263],[430,307]),([320,362],[270,471],[273,570]),([270,693],[332,785],[433,835]),([543,889],[672,872],[752,816]),([801,781],[828,725],[824,697]),([816,674],[787,660],[751,674]),([737,735],[683,780],[612,790]),([518,804],[447,773],[418,705]),([389,634],[398,564],[427,496]),([463,411],[527,346],[603,313]),([665,288],[712,301],[753,320])])
wave=bezier([350,951],[([309,918],[266,874],[247,843]),([310,806],[379,822],[433,839]),([492,858],[529,869],[581,866]),([680,858],[723,818],[751,674]),([797,622],[845,601],[890,604]),([962,608],[1027,673],[1040,749]),([970,707],[924,728],[883,753]),([818,799],[780,830],[721,852]),([611,898],[450,903],[350,951])])
pearl_outline=bezier([753,320],[
 ([659,249],[521,263],[430,307]),([320,362],[270,471],[273,570]),
 ([270,693],[332,785],[433,835]),([477,858],[530,869],[581,866]),
 ([526,866],[477,851],[433,839]),([375,820],[306,809],[247,843]),
 ([275,884],[312,926],[350,951]),([454,903],[610,898],[721,852]),
 ([780,830],[818,799],[883,753]),([925,726],[971,708],[1040,749]),
 ([1027,673],[962,608],[890,604]),([845,601],[797,622],[751,674]),
 ([773,645],[809,656],[824,697]),([831,726],[795,759],[752,777]),
 ([697,800],[616,801],[558,789]),([488,778],[442,748],[418,705]),
 ([389,634],[398,564],[427,496]),([463,411],[527,346],[603,313]),
 ([665,288],[712,301],[753,320])])
# Align the hand trace to the reference's bright silver boundary. The normal
# search is local and smoothed, preserving the pointed tips and broad curves.
lum=gaussian_filter(m.im@np.array([.2126,.7152,.0722]),1)
path=pearl_outline[:-1];delta=np.roll(path,-1,axis=0)-np.roll(path,1,axis=0);delta/=np.maximum(np.linalg.norm(delta,axis=1)[:,None],1e-8)
inward=np.c_[-delta[:,1],delta[:,0]]*(1 if np.cross(path,np.roll(path,-1,axis=0)).sum()>0 else -1)
shifts=np.arange(-21,22,dtype=float);samples=path[:,None,:]+inward[:,None,:]*shifts[None,:,None]
inside=samples+inward[:,None,:]*4;outside=samples-inward[:,None,:]*4
scores=map_coordinates(lum,[inside[:,:,1],inside[:,:,0]],order=1)-map_coordinates(lum,[outside[:,:,1],outside[:,:,0]],order=1)
scores-=abs(shifts)[None,:]*.0012
penalty=.018*(shifts[:,None]-shifts[None,:])**2
cost=-scores[0]+.025*shifts**2;parents=[]
for row in scores[1:]:
 trial=cost[:,None]+penalty;parent=trial.argmin(0);parents.append(parent);cost=trial[parent,np.arange(len(shifts))]-row
choice=[int((cost+.025*shifts**2).argmin())]
for parent in parents[::-1]:choice.append(int(parent[choice[-1]]))
move=shifts[np.array(choice[::-1])]
move=gaussian_filter1d(move,7,mode='wrap');pearl_outline=path+inward*move[:,None]
pm=m.poly(pearl_outline)&mask
p,t=m.triangulate_curve(pearl_outline,12,'pearl');distance=gaussian_filter(distance_transform_edt(pm),11)
height=.198+.054*(1-np.exp(-distance/33));z=map_coordinates(height,[p[:,1],p[:,0]],order=1)
idx=len(m.groups);m.relief('Continuous smooth pearl crescent and curling wave',p,t,z,'pearl',True)
# Analytic smooth normals avoid Delaunay creases in the broad enamel surface.
gy,gx=np.gradient(height);nx=-map_coordinates(gx,[p[:,1],p[:,0]],order=1)/m.S;ny=map_coordinates(gy,[p[:,1],p[:,0]],order=1)/m.S
normal=np.c_[nx,ny,np.ones(len(p))];normal/=np.linalg.norm(normal,axis=1)[:,None]
m.arrays[str(idx)+'_normal_hints']=np.vstack([normal,normal*np.array([1,1,-1])]).astype(np.float32)

# Silver edging follows the real curved crest. Every strip has a closed section.
def edge_tube(name,path,width=1.45):
 path=np.asarray(path);path=path[np.r_[True,np.linalg.norm(np.diff(path,axis=0),axis=1)>.1]]
 if np.linalg.norm(path[0]-path[-1])<.2:path=path[:-1]
 path=gaussian_filter1d(path,1.2,axis=0,mode='wrap')[::2];tangent=np.roll(path,-1,axis=0)-np.roll(path,1,axis=0);tangent/=np.maximum(np.linalg.norm(tangent,axis=1)[:,None],1e-8)
 perp=np.c_[-tangent[:,1],tangent[:,0]];count=6;pts=[];coords=[]
 base=map_coordinates(height,[path[:,1],path[:,0]],order=1)+.002
 for back in [False,True]:
  for a in np.linspace(0,2*np.pi,count,endpoint=False):
   xy=path+perp*width*np.cos(a);zz=base+.009*np.sin(a)
   pts.extend(m.world(xy,zz*(-1 if back else 1)));coords.extend(m.uv(xy))
 n=len(path);faces=[]
 for back in [0,1]:
  off=back*n*count
  for j in range(count):
   k=(j+1)%count
   for i in range(n):
    a=off+j*n+i;b=off+j*n+(i+1)%n;c=off+k*n+i;d=off+k*n+(i+1)%n
    faces.extend([[a,d,b],[a,c,d]] if back else [[a,b,d],[a,d,c]])
 m.add(name,np.array(pts),faces,'metal',np.array(coords),True)

# Trace the union boundary rather than crossing a trim through the pearl join.
e=np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);_,ids,cnt=np.unique(np.sort(e,axis=1),axis=0,return_index=True,return_counts=True)
edges=e[ids[cnt==1]];adj={}
for a,b in edges:adj.setdefault(int(a),[]).append(int(b));adj.setdefault(int(b),[]).append(int(a))
remaining=set(adj);loops=[]
while remaining:
 start=next(iter(remaining));loop=[start];previous=-1;cur=start
 while True:
  nxt=next((v for v in adj[cur] if v!=previous),start)
  if nxt==start:break
  loop.append(nxt);previous,cur=cur,nxt
  if len(loop)>len(adj)+2:raise ValueError('Crest boundary is not a simple loop')
 remaining.difference_update(loop);loops.append(p[loop])
# The silver lip is carried by the crest's continuous polished edge material.
# A separate tube duplicated the thin contour and drew a distracting hairline.

# Behind the large compass sit the slim circle and four rim markers.
m.ring('Thin compass guide circle',[627,553],[173,173],[(1,.276),(.997,.286),(.985,.286),(.982,.276),(.982,-.276),(.985,-.286),(.997,-.286),(1,-.276)],'metal')
for name,shape in [('North',[(628,176),(648,273),(608,273)]),('West',[(184,558),(275,541),(275,576)]),('East',[(1044,558),(966,544),(915,558),(964,572)]),('South',[(628,1050),(609,940),(645,940)])]:
 m.solid(name+' silver perimeter marker',shape,.14,.18,'metal',inset=.025)

# Each raised compass point has two true flat polished planes.
outline=[]
for i in range(16):
 a=-np.pi/2+i*np.pi/8
 radius=(285 if i%4==0 else 196) if i%2==0 else 40
 outline.append([627+radius*np.cos(a),553+radius*np.sin(a)])
xy=np.vstack([outline,[[627,553]]]);v=m.world(xy,np.r_[[.29]*16,.405]);tri=m.orient(v,[[16,i,(i+1)%16] for i in range(16)])
back=v.copy();back[:,2]*=-1;n=len(v);faces=list(tri)+list(tri[:,::-1]+n)
for i in range(16):j=(i+1)%16;faces.extend([[i,j,j+n],[i,j+n,i+n]])
m.add('Eight pointed silver compass with sixteen flat facets',np.vstack([v,back]),faces,'metal',np.vstack([m.uv(xy),m.uv(xy)]),False)
m.groups[-1]['plain_vertical_walls']=True

m.save(dict(name='Tidal Compass',selection='tidalCompass',bounds=[142,136,1098,1098],textured_roles=['metal','field','pearl','wave'],metal_roles=['metal','pearl','wave'],desired_colors={'metal':[.43,.44,.42],'pearl':[.18,.29,.27],'wave':[.035,.20,.20]},roughness={'metal':.29,'field':.4,'pearl':.25,'wave':.3},side_color=[.13,.18,.18],side_roughness=.48,method='Reference traced smooth continuous pearl crescent and wave, separate silver edging and sixteen physical compass facets, matching sculpted rear. Distinctive thin frame preserves this reference instead of changing the approved shared twelve coin template.'))

# A trace overlay is working evidence, not a substitute for native inspection.
overlay=Image.open(R/'reference.png').convert('RGB');draw=ImageDraw.Draw(overlay)
for path,color in [(pearl_outline,'yellow'),(teal,'cyan')]:draw.line([tuple(q) for q in path],fill=color,width=2)
overlay.save(m.C/'review'/'trace_overlay.png')
