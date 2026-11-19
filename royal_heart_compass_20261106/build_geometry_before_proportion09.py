"""Five complete, editable sculptural badges. All dimensions are scene units."""
from pathlib import Path
import json, shutil, sys
import numpy as np
from scipy.spatial import ConvexHull
from scipy.interpolate import CubicSpline

ROOT=Path(__file__).resolve().parent
PARTS=[]
MATERIALS={
 'gold':dict(color=[.57,.285,.067],metallic=1.,roughness=.245),
 'gold_satin':dict(color=[.43,.205,.043],metallic=1.,roughness=.34),
 'gold_recess':dict(color=[.18,.072,.013],metallic=1.,roughness=.43),
 'navy':dict(color=[.006,.019,.042],metallic=.4,roughness=.46),
 'purple_velvet':dict(color=[.034,.00065,.044],metallic=0.,roughness=.88,sheen=.65),
 'red_velvet':dict(color=[.052,.0004,.003],metallic=0.,roughness=.86,sheen=.65),
 'green_velvet':dict(color=[.0006,.024,.009],metallic=0.,roughness=.86,sheen=.65),
 'CrestGem_Rose':dict(color=[.75,.008,.15],metallic=0.,roughness=.03,ior=1.77),
 'CrestGem_Amethyst':dict(color=[.15,.006,.32],metallic=0.,roughness=.03,ior=1.55),
 'CrestGem_Ruby':dict(color=[.40,.002,.013],metallic=0.,roughness=.03,ior=1.77),
 'CrestGem_Emerald':dict(color=[.001,.19,.048],metallic=0.,roughness=.03,ior=1.58),
 'CrestGem_SapphireAstral':dict(color=[.002,.01,.10],metallic=0.,roughness=.03,ior=1.77),
 'CrestGem_Sapphire':dict(color=[.003,.02,.18],metallic=0.,roughness=.03,ior=1.77),
 'CrestGem_Ice':dict(color=[.44,.70,.79],metallic=0.,roughness=.025,ior=1.46),
}

def norm(v):
 v=np.asarray(v,float);return v/np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-12)

def add(name,p,t,mat='gold',smooth=True):
 p=np.asarray(p,float);t=np.asarray(t,np.int32)
 PARTS.append(dict(name=name,p=p,t=t,mat=mat,smooth=smooth));return len(PARTS)-1

def orient_hull(p):
 hull=ConvexHull(p);t=hull.simplices.copy()
 n=np.cross(p[t[:,1]]-p[t[:,0]],p[t[:,2]]-p[t[:,0]])
 flip=(n*hull.equations[:,:3]).sum(1)<0;t[flip]=t[flip,::-1]
 return t

def hull(name,p,mat='gold'):
 p=np.asarray(p,float);return add(name,p,orient_hull(p),mat,False)

def basis(n):
 n=norm(n);u=norm(np.cross([0,1,0],n))
 if np.linalg.norm(u)<.1:u=np.array([1.,0,0])
 return u,np.cross(n,u),n

def gem(name,c,rx,ry,depth,mat,n=(0,0,1),diamond=False):
 u,v,w=basis(n);c=np.asarray(c);N=8 if diamond else 16
 a=np.arange(N)*2*np.pi/N+(np.pi/2 if diamond else np.pi/16)
 if diamond:
  a=np.arange(4)*np.pi/2;N=4
  # Additional crown tiers create a genuine pointed cut, with flat facets.
 rings=[(1,0,0),(.57,depth*.46,0),(.30,depth*.68,np.pi/N),(1,-depth*.06,0),(.32,-depth*.60,np.pi/N)]
 p=[]
 for r,z,phase in rings:
  for angle in a+phase:p.append(c+u*(rx*r*np.cos(angle))+v*(ry*r*np.sin(angle))+w*z)
 p.append(c-w*depth*.77)
 return hull(name,p,mat)

def tube(name,pts,r=.025,mat='gold',sides=8,closed=False):
 pts=np.asarray(pts,float);N=len(pts);p=[];t=[]
 tangent=norm(np.roll(pts,-1,axis=0)-np.roll(pts,1,axis=0)) if closed else norm(np.gradient(pts,axis=0))
 prev=None
 for i,(c,d) in enumerate(zip(pts,tangent)):
  u=norm(np.cross(d,[0,0,1]))
  if np.linalg.norm(u)<.1:u=norm(np.cross(d,[0,1,0]))
  if prev is not None and np.dot(prev,u)<0:u=-u
  prev=u;v=np.cross(d,u);radius=r[i] if np.ndim(r) else r
  for a in np.arange(sides)*2*np.pi/sides:p.append(c+radius*(np.cos(a)*u+np.sin(a)*v))
 for i in range(N if closed else N-1):
  for j in range(sides):
   a=i*sides+j;b=i*sides+(j+1)%sides;c=((i+1)%N)*sides+(j+1)%sides;d=((i+1)%N)*sides+j;t.extend([[a,b,c],[a,c,d]])
 if not closed:
  p.extend([pts[0],pts[-1]])
  for j in range(sides):t.extend([[len(p)-2,(j+1)%sides,j],[len(p)-1,(N-1)*sides+j,(N-1)*sides+(j+1)%sides]])
 return add(name,p,t,mat)

def bez(control,N=40):
 control=np.asarray(control,float);s=np.linspace(0,1,N)
 if len(control)==4:
  return (1-s[:,None])**3*control[0]+3*(1-s[:,None])**2*s[:,None]*control[1]+3*(1-s[:,None])*s[:,None]**2*control[2]+s[:,None]**3*control[3]
 d=np.r_[0,np.cumsum(np.linalg.norm(np.diff(control,axis=0),axis=1))];return CubicSpline(d,control)(np.linspace(0,d[-1],N))

def ribbon(name,pts,width,depth=.035,mat='gold',normal=(0,0,1)):
 pts=np.asarray(pts,float);N=len(pts);tan=norm(np.gradient(pts,axis=0));ns=np.broadcast_to(normal,(N,3)).copy() if np.shape(normal)==(3,) else np.asarray(normal)
 u=norm(np.cross(tan,ns));ns=norm(np.cross(u,tan));p=[];t=[]
 profile=[(-1,0),(-.86,.75),(-.55,1),(.55,1),(.86,.75),(1,0),(.90,-.7),(-.90,-.7)]
 widths=np.broadcast_to(width,(N,)) if np.ndim(width)==0 else width
 for i,c in enumerate(pts):
  for x,z in profile:p.append(c+u[i]*widths[i]*x/2+ns[i]*depth*z)
 for i in range(N-1):
  for j in range(8):
   a=i*8+j;b=i*8+(j+1)%8;c=(i+1)*8+(j+1)%8;d=(i+1)*8+j;t.extend([[a,b,c],[a,c,d]])
 for j in range(1,7):t.extend([[0,j+1,j],[(N-1)*8,(N-1)*8+j,(N-1)*8+j+1]])
 return add(name,p,t,mat,True)

def petal(name,a,b,width=.16,lift=.08,mat='gold',normal=(0,0,1)):
 a=np.asarray(a,float);b=np.asarray(b,float);n=np.asarray(normal,float);d=b-a;u=norm(np.cross(d,n));p=[];t=[];N=14
 for i,s in enumerate(np.linspace(0,1,N)):
  c=a+d*s+n*(np.sin(np.pi*s)*lift*.35);w=width*np.sin(np.pi*s)**.78
  for x,h in [(-1,0),(-.55,.48),(0,1),(.55,.48),(1,0),(0,-.22)]:p.append(c+u*w*x+n*(lift*h*np.sin(np.pi*s)))
 for i in range(N-1):
  for j in range(6):
   a0=i*6+j;b0=i*6+(j+1)%6;c0=b0+6;d0=a0+6;t.extend([[a0,b0,c0],[a0,c0,d0]])
 return add(name,p,t,mat,True)

def sphere(name,c,r,mat='gold',N=12,M=8,scale=(1,1,1)):
 p=[];t=[];c=np.asarray(c);scale=np.asarray(scale)
 for j in range(M+1):
  a=np.pi*j/M
  for i in range(N):
   b=2*np.pi*i/N;p.append(c+r*np.array([np.sin(a)*np.cos(b),np.cos(a),np.sin(a)*np.sin(b)])*scale)
 for j in range(M):
  for i in range(N):
   a=j*N+i;b=j*N+(i+1)%N;t.extend([[a,b,b+N],[a,b+N,a+N]])
 return add(name,p,t,mat)

def ring_y(name,r,y,z=.0,profile=None,mat='gold',N=128):
 if profile is None:profile=[(-.08,-.04),(-.06,.04),(.06,.04),(.08,-.04)]
 p=[];t=[];K=len(profile)
 for i in range(N):
  a=i*2*np.pi/N
  for dr,dy in profile:p.append([(r+dr)*np.sin(a),y+dy,z+(r+dr)*np.cos(a)])
 for i in range(N):
  for j in range(K):
   a=i*K+j;b=i*K+(j+1)%K;c=((i+1)%N)*K+(j+1)%K;d=((i+1)%N)*K+j;t.extend([[a,b,c],[a,c,d]])
 return add(name,p,t,mat)

def circle_z(name,r,z,mat='gold',width=.025,c=(0,0),N=192):
 a=np.arange(N)*2*np.pi/N;pts=np.c_[c[0]+r*np.cos(a),c[1]+r*np.sin(a),np.full(N,z)]
 return tube(name,pts,width,mat,8,True)

def contour_band(name,xy,width,z,depth,mat='gold'):
 xy=np.asarray(xy);xy=xy if np.sum(xy[:,0]*np.roll(xy[:,1],-1)-np.roll(xy[:,0],-1)*xy[:,1])>0 else xy[::-1];p=np.c_[xy,np.full(len(xy),z)];tan=norm(np.roll(p,-1,axis=0)-np.roll(p,1,axis=0));u=norm(np.cross(tan,[0,0,1]));pts=[];t=[]
 prof=[(-.5,-.5),(-.5,.15),(-.40,.48),(-.28,.55),(.28,.55),(.40,.48),(.5,.15),(.5,-.5)]
 for i,c in enumerate(p):
  for w,h in prof:pts.append(c+u[i]*width*w+np.array([0,0,depth*h]))
 for i in range(len(p)):
  for j in range(8):
   a=i*8+j;b=i*8+(j+1)%8;c=((i+1)%len(p))*8+(j+1)%8;d=((i+1)%len(p))*8+j;t.extend([[a,b,c],[a,c,d]])
 return add(name,pts,t,mat)

def diamond_setting(name,c,rx,ry,depth,mat,n=(0,0,1),border=.045):
 u,v,w=basis(n);c=np.asarray(c);xy=np.array([[rx,0],[0,ry],[-rx,0],[0,-ry]])
 path=[]
 for i in range(4):
  for q in np.linspace(0,1,10,endpoint=False):path.append(c+u*(xy[i,0]*(1-q)+xy[(i+1)%4,0]*q)+v*(xy[i,1]*(1-q)+xy[(i+1)%4,1]*q))
 tube(name+' closed gold prong frame',path,border,'gold',8,True)
 gem(name+' independent gemstone',c,rx-border*.6,ry-border*.6,depth,mat,n,True)

def shield_setting(name,c,rx,ry,depth,mat,n=(0,0,1)):
 from reference_gold_relief import central_mask,relief
 u,v,w=basis(n);c=np.asarray(c);reference=ROOT/'amethyst_crown/reference.png'
 gem_pixels=np.array([[768,468],[816,506],[812,581],[768,674],[722,581],[721,506]])
 xy=np.c_[(gem_pixels[:,0]-768)*rx/88,(550-gem_pixels[:,1])*ry/160]
 center=xy.mean(0);local=xy-center;points=[]
 for scale,z in [(1,0),(.60,depth*.48),(.30,depth*.65),(1,-depth*.06),(.30,-depth*.60)]:
  points.extend([c+u*(center[0]+x*scale)+v*(center[1]+y*scale)+w*(z+.055) for x,y in local])
 points.append(c+u*center[0]+v*center[1]-w*depth*.77)
 hull(name+' independent gemstone',points,mat)
 from sculpted_gold import frame,leaf,central_leaves
 outer=np.array([[768,390],[856,491],[851,572],[768,710],[685,572],[680,491]],float)
 inner=gem_pixels
 pp,tt=frame(outer,inner,.19)
 def place(pp):
  x=(pp[:,0]-768)*rx/88;y=(550-pp[:,1])*ry/160
  z=pp[:,2]+np.sqrt(np.maximum(2.65**2-x*x,.10))-2.65
  return c+u[None,:]*x[:,None]+v[None,:]*y[:,None]+w[None,:]*z[:,None]
 add(name+' clean faceted gold shield setting',place(pp),tt,'gold',True)
 for side in [-1,1]:
  for j,(aa,bb,height,layer) in enumerate(central_leaves()):
   pp,tt=leaf(aa,bb,height,layer)
   if side>0:pp[:,0]=1536-pp[:,0];tt=tt[:,::-1]
   add(name+' separately sculpted gold leaf '+str(side)+' '+str(j),place(pp),tt,'gold',True)

def reference_finial(c,n):
 from reference_gold_relief import finial_mask,relief
 u,v,w=basis(n);c=np.asarray(c);scale=.22/47
 xy=np.array([[768,80],[815,172],[768,244],[721,172]],float)
 xy=np.c_[(xy[:,0]-768)*scale,(172-xy[:,1])*scale];center=xy.mean(0);local=xy-center;points=[]
 for size,z in [(1,0),(.56,.095),(.28,.13),(1,-.014),(.30,-.11)]:
  points.extend([c+u*(center[0]+x*size)+v*(center[1]+y*size)+w*(z+.05) for x,y in local])
 points.append(c+u*center[0]+v*center[1]-w*.15)
 hull('Amethyst pointed finial measured independent gemstone',points,'CrestGem_Amethyst')
 from sculpted_gold import frame,leaf,top_leaves
 outer=np.array([[768,30],[810,100],[815,128],[832,175],[768,272],[704,175],[721,128],[726,100]],float)
 inner=np.array([[768,80],[797,137],[807,156],[815,172],[768,244],[721,172],[729,156],[739,137]],float)
 pp,tt=frame(outer,inner,.16)
 def place(pp):
  x=(pp[:,0]-768)*scale;y=(172-pp[:,1])*scale
  return c+u[None,:]*x[:,None]+v[None,:]*y[:,None]+w[None,:]*pp[:,2,None]
 add('Top fleur clean faceted gold finial frame',place(pp),tt,'gold',True)
 for side in [-1,1]:
  for j,(aa,bb,height,layer) in enumerate(top_leaves()):
   pp,tt=leaf(aa,bb,height,layer)
   if side>0:pp[:,0]=1536-pp[:,0];tt=tt[:,::-1]
   add('Top fleur separately sculpted gold leaf '+str(side)+' '+str(j),place(pp),tt,'gold',True)
 # The stem physically joins the setting and the same central arch hub.
 ribbon('Top fleur solid joining stem',[c+v*y-w*.03 for y in np.linspace(-.59,-.41,8)],.16,.075,'gold',n)

def scroll(name,x,y,z,s=.5,sign=1,mat='gold'):
 a=np.linspace(0,2.05*np.pi,65);r=np.linspace(s,.025,len(a));pts=np.c_[x+sign*r*np.cos(a),y+r*np.sin(a),np.full(len(a),z)]
 ribbon(name,pts,np.linspace(.16*s/.5,.008,len(a)),.038,mat)

def save(key,name,reference,meta):
 global PARTS
 R=ROOT/key;C=R/'candidate09'
 for f in ['source','mobile','review','textures']:(C/f).mkdir(parents=True,exist_ok=True)
 shutil.copy2(reference,R/'reference.png')
 p=np.vstack([a['p'] for a in PARTS]);low=p.min(0);high=p.max(0)
 # Normalize the finished complete model once, not its individual parts.
 scale=min(6.35/(high[0]-low[0]),5.43/(high[1]-low[1]))
 center=np.array([(high[0]+low[0])/2,low[1],(high[2]+low[2])/2]);data={};groups=[]
 for i,a in enumerate(PARTS):
  q=(a['p']-center)*scale;q[:,1]-=2.455
  data[str(i)+'_points']=q.astype(np.float32);data[str(i)+'_triangles']=a['t'];groups.append({k:v for k,v in a.items() if k not in ['p','t']})
 np.savez_compressed(C/'geometry.npz',**data);(C/'groups.json').write_text(json.dumps(groups,indent=2)+'\n');(C/'materials.json').write_text(json.dumps(MATERIALS,indent=2)+'\n')
 (R/'design.json').write_text(json.dumps(dict(key=key,name=name,source_reference=str(reference),**meta),indent=2)+'\n')
 print(key,len(PARTS),'pieces',sum(len(a['t']) for a in PARTS),'triangles',flush=True);PARTS=[]

def heart():
 # Two genuinely convex lobes meet along the center facet ridge. No concave
 # stone is passed to the convex optical renderer.
 left=bez([[0,1.65],[-1.1,3.65],[-3.30,2.9],[-2.95,.75]],55)
 lower=bez([[-2.95,.75],[-2.75,-.55],[-.8,-2.25],[0,-2.95]],70)
 half=np.vstack([left,lower[1:]])
 outline=np.vstack([half,half[-2:0:-1]*[-1,1]])
 contour_band('Wide sculpted heart gold bezel',outline,.43,.03,.30)
 contour_band('Inner polished heart gold seat',outline*.945,.048,.19,.055)
 contour_band('Rear matching gold heart bead',outline,.055,-.24,.08)
 for side in [-1,1]:
  xy=half*np.array([side,1])*.925
  p=[]
  outline_sample=xy[np.unique(np.linspace(0,len(xy)-1,48).astype(int))]
  p.extend(np.c_[outline_sample,np.full(len(outline_sample),.10)])
  p.extend(np.c_[outline_sample,np.full(len(outline_sample),-.06)])
  # Broad triangular crown facets meet at a raised center ridge.
  # Front cut landmarks measured from the owner's heart reference.
  # They control actual closed gemstone facets, never an appearance map.
  reference_xy=np.array([[627,389],[627,493],[627,784],[627,970],[420,232],[282,291],[369,371],[455,328],[209,453],[274,622],[421,656],[453,814],[386,850]])
  xy_inner=np.c_[(reference_xy[:,0]-627)/165,(620-reference_xy[:,1])/165]
  depth=1.18-.11*xy_inner[:,0]**2-.10*xy_inner[:,1]**2
  xy_inner[:,0]*=side;p.extend(np.c_[xy_inner,depth])
  p.extend(np.c_[xy_inner,-depth*.72])
  hull('Ruby heart '+('left' if side<0 else 'right')+' optical lobe',p,'CrestGem_Rose')
 save('ruby_heart','Ruby Heart',Path('/Users/antonioperedo/Downloads/Faceted Ruby Heart Emblem.png'),dict(gem_strategy='Two adjacent closed convex rose ruby lobes, real crown and pavilion facets, no appearance photographs.'))

def crown(kind):
 mat={'amethyst':'CrestGem_Amethyst','ruby':'CrestGem_Ruby','emerald':'CrestGem_Emerald'}[kind];velvet={'amethyst':'purple_velvet','ruby':'red_velvet','emerald':'green_velvet'}[kind]
 base=-1.85;radius=2.48;hub=1.68
 ring_y('Continuous solid crown base',radius,base,profile=[(-.10,-.26),(-.11,.23),(.06,.24),(.11,.19),(.11,-.20),(.065,-.26)],mat='gold_recess')
 ring_y('Embossed velvet base band',radius+.115,base,profile=[(-.012,-.18),(-.012,.18),(.009,.18),(.009,-.18)],mat=velvet if kind=='amethyst' else 'gold_recess')
 for y in [base-.275,base-.22,base+.225,base+.28]:ring_y('Rolled polished gold crown rim',radius+.1,y,profile=[(.045*np.cos(a),.035*np.sin(a)) for a in np.arange(10)*2*np.pi/10])
 # A full cloth cushion, not a front drape. Folds are actual geometry.
 N=288;M=56;p=[];t=[]
 for j in range(M+1):
  s=j/M;y=base+.13+(hub-base-.09)*(.98 if kind=='amethyst' else 1.)*np.sin(s*np.pi/2)
  r=radius*(.95 if kind=='amethyst' else .91)*np.cos(s*np.pi/2)**(.60 if kind=='amethyst' else .48)
  for i in range(N):
   a=i*2*np.pi/N;fold=1-.195*np.cos(8*a+.35*np.sin(s*4))*(np.sin(np.pi*s)**.6)+.028*np.cos(16*a+.7*np.sin(3*s))*np.sin(np.pi*s)+.012*np.cos(24*a)*np.sin(np.pi*s)
   local=(a/(np.pi/4))%1
   gathered=(.095*np.exp(-((local-(.27+.04*np.sin(s*6)))/.09)**2)+.080*np.exp(-((local-(.70+.05*np.sin(s*4)))/.10)**2))*np.exp(-((s-.52)/.31)**2)
   fold-=gathered
   height=y-.45*gathered+(-.18 if kind=='amethyst' else .23)*np.cos(8*a+.45*np.sin(s*5))*np.sin(np.pi*s)**1.1
   if kind=='amethyst':height=min(height,hub-.10)
   p.append([r*np.sin(a)*fold,height,r*np.cos(a)*fold])
 for j in range(M):
  for i in range(N):
   a=j*N+i;b=j*N+(i+1)%N;t.extend([[a,b,b+N],[a,b+N,a+N]])
 MATERIALS[velvet.replace('_velvet','_fold_velvet')]=dict(MATERIALS[velvet])
 add('Complete deeply folded '+kind+' velvet cushion',p,t,velvet.replace('_velvet','_fold_velvet'))
 PARTS[-1]['cloth_grid']=[N,M]
 # Eight uninterrupted arches land at exactly the same central hub. The
 # front and rear arches carry the same relief language and finished edges.
 for k in range(8):
  a=k*np.pi/4;u=np.array([np.sin(a),0,np.cos(a)]);s=np.linspace(0,1,65)
  side_arch=k in [2,6]
  profile=bez([[radius*1.01,base+.25],[radius*(1.42 if side_arch else 1.18),hub+.08],[radius*(.44 if kind=='amethyst' else .72),hub+(-.12 if kind=='amethyst' else .43)],[0,hub+.055]],len(s))
  rad=profile[:,0];ys=profile[:,1]
  pts=rad[:,None]*u+ys[:,None]*[0,1,0]
  ns=norm(rad[:,None]*u+np.c_[np.zeros(len(s)),np.full(len(s),1.8),np.zeros(len(s))])
  if side_arch:
   ns=norm(ns*.23+np.array([0,.12,1.]))
  pts+=ns*.07
  width=.46 if k%2 else .52
  if side_arch:width=.22
  ribbon('Continuous '+str(k+1)+' crown arch to central hub',pts,width,.06,'gold_satin',ns)
  tangent=norm(np.gradient(pts,axis=0));across=norm(np.cross(tangent,ns))
  for sign in [-1,1]:tube('Polished arch raised edge',pts+across*width*.43*sign+ns*.035,.018,'gold',8)
  # Repeated sculpted ornament leaves run with the arched band.
  for j in range(7,54,6):
   c=pts[j]+ns[j]*.07;d=tangent[j];cross=across[j]
   for sign in [-1,1]:
    if kind=='emerald':petal('Arch relief '+kind+' leaf',c-d*.06,c+d*.18+cross*.085*sign,.042,.026,'gold',ns[j])
    else:
     q=bez([[0,-.08],[sign*.13,-.04],[sign*.14,.15],[sign*.05,.20]],24)
     curve=c+q[:,0,None]*cross+q[:,1,None]*d
     ribbon('Arch curled floral engraving',curve,np.linspace(.038,.004,len(curve)),.018,'gold',ns[j])
     petal('Arch sculpted floral side lobe',c-d*.04,c+d*.075+cross*.11*sign,.032,.023,'gold',ns[j])
     petal('Arch engraved floral tip',curve[-1],curve[-1]+d*.06+cross*.025*sign,.025,.016,'gold',ns[j])
  if True:
   for j in ([10] if kind=='amethyst' and k not in [0,4] else [] if kind=='amethyst' else [10,36]):
    c=pts[j]+ns[j]*.085
    diamond_setting('Arch '+str(k+1)+' '+kind+' stone',c,.16 if j==10 else .10,.32 if j==10 else .17,.14,mat,ns[j],.022)
  if kind=='ruby' and k in [0,1,3,4,5,7]:
   for j in [10,23,29,34,47]:gem('Arch small brilliant',pts[j]+ns[j]*.075,.038,.038,.042,'CrestGem_Ice',ns[j])
 sphere('Gold central joining hub',(0,hub+.09,0),.34,N=24,M=12,scale=(1,.60,1))
 ring_y('Central arch joining collar',.23,hub+.06,profile=[(.03*np.cos(a),.03*np.sin(a)) for a in np.arange(8)*2*np.pi/8],N=48)
 # Complete circlet ornaments repeat around the real round band.
 for k in (range(0,12,2) if kind=='amethyst' else range(12)):
  a=({0:0,2:.67,4:np.pi-.67,6:np.pi,8:np.pi+.67,10:2*np.pi-.67}[k] if kind=='amethyst' else k*2*np.pi/12);n=np.array([np.sin(a),0,np.cos(a)]);u=np.array([np.cos(a),0,-np.sin(a)]);c=n*(radius+.16)+[0,base,0]
  if kind=='amethyst' and k not in [0,6]:
   gem('Base circlet faceted gold kite',c,.13,.14,.12,'gold',n,True)
  elif k%2==0:diamond_setting('Base circlet '+kind+' diamond '+str(k),c,.16,.21,.15,mat,n,.027)
  else:
   circle=[c+u*.12*np.cos(q)+[0,.12*np.sin(q),0] for q in np.arange(32)*2*np.pi/32];tube('Round circlet gold bezel',circle,.025,closed=True);gem('Round circlet '+kind+' stone',c,.10,.10,.10,mat,n)
  # Relief follows the circlet around its whole circumference.
  for side in ([] if kind=='amethyst' else [-1,1]):
   if kind=='emerald':
    start=c+u*.19*side-[0,.06,0];end=c+u*.50*side+[0,.07,0]
    petal('Base laurel relief',start,end,.055,.035,'gold',n)
    petal('Base laurel relief',start+u*.1*side,end+[0,-.14,0],.05,.035,'gold',n)
   else:
    if kind=='amethyst':
     curves=[([[.18,-.10],[.65,.24],[1.17,.19],[1.03,-.015]],.12),([[.30,-.10],[.90,-.23],[1.13,.02],[.84,.015]],.08)]
    else:curves=[([[.15,-.09],[.38,.16],[.61,.18],[.54,.02]],.085),([[.22,-.08],[.52,-.19],[.59,-.06],[.46,-.02]],.06)]
    for controls,width in curves:
     q=bez(controls,44);angle=a+q[:,0]*side/(radius+.16)
     pp=np.c_[np.sin(angle)*(radius+.185),base+q[:,1],np.cos(angle)*(radius+.185)]
     nn=np.c_[np.sin(angle),np.zeros(len(q)),np.cos(angle)]
     ribbon('Circlet sculpted returning gold scroll',pp,np.linspace(width,.008,len(q)),.034,'gold',nn)
 # Fine milgrain is real gold geometry, with no painted sparkle.
 for y in [base-.19,base+.19]:
  for a in np.arange(144)*2*np.pi/144:sphere('Circlet milgrain bead',[np.sin(a)*(radius+.14),y,np.cos(a)*(radius+.14)],.014,N=6,M=4)
 # Four fleur ornaments face out from the base; front and back are complete.
 for a in [0,np.pi/2,np.pi,3*np.pi/2]:
  n=np.array([np.sin(a),0,np.cos(a)]);u=np.array([np.cos(a),0,-np.sin(a)]);center=n*(radius+.16)+[0,base+.30,0]
  def tr(x,y,z=0):return center+u*x+[0,y,0]+n*z
  if abs(np.sin(a))<.1:
   ry=1.02 if kind!='amethyst' else .82;rx=.60 if kind!='amethyst' else .46
   if kind=='amethyst':shield_setting('Large central '+kind+' jewel',tr(0,.79,.15),rx*.90,ry*.90,.38,mat,n)
   else:diamond_setting('Large central '+kind+' jewel',tr(0,.79,.15),rx*.78,ry*.83,.38,mat,n,.028)
   outer=np.array([[rx+.05,0],[0,ry+.07],[-rx-.05,0],[0,-ry-.07]])
   inner=np.array([[rx*.78,0],[0,ry*.83],[-rx*.78,0],[0,-ry*.83]])
   mount=[];faces=[]
   for contour,dz in [(outer,-.025),(outer,.08),(inner,.11),(inner,-.025)]:
    mount.extend([tr(x,y+.79,.15+dz) for x,y in contour])
   for ring in range(4):
    for j in range(4):
     aa=ring*4+j;bb=ring*4+(j+1)%4;cc=((ring+1)%4)*4+(j+1)%4;dd=((ring+1)%4)*4+j
     faces.extend([[aa,bb,cc],[aa,cc,dd]])
   if kind!='amethyst':add('Broad beveled central '+kind+' jewel gold mount',mount,faces,'gold',False)
   if kind in ['ruby','emerald']:
    # A solid stepped gold mount supports the entire pave border.
    cy=base+.30+.79
    outline=np.array([[rx+.085,cy],[0,cy+ry+.11],[-rx-.085,cy],[0,cy-ry-.11]])
    band=contour_band('Large central solid gold pave surround',outline,.19,(radius+.16+.15)*n[2],.12)
    # Pavé follows all four sloping sides of the central mount.
    corners=np.array([[rx+.085,.79],[0,.79+ry+.11],[-rx-.085,.79],[0,.79-ry-.11]])
    for k in range(4):
     for q in np.linspace(.06,.94,8):
      x,y=corners[k]*(1-q)+corners[(k+1)%4]*q;c=tr(x,y,.25)
      sphere('Pave gold bead seat',c,.042,N=8,M=5,scale=(1,1,.6));gem('Central border brilliant',c+n*.02,.031,.031,.042,'CrestGem_Ice' if kind=='ruby' else mat,n)
   for side in [-1,1]:
    # Flowing upward foliage and curling bases frame the central jewel.
    path=bez([[side*.10,0],[side*1.15,-.18],[side*1.45,.88],[side*.70,.66]],45)
    ribbon('Gold fleur lower curled sweep',[tr(x,y,.10) for x,y in path],np.linspace(.29,.018,len(path)),.055,'gold',n)
    for j in range(3):
     petal('Fleur raised gold lobed leaf',tr(side*(.32+j*.18),.28+j*.13,.13),tr(side*(.75+j*.19),.95+j*.13,.14),.115,.08,'gold',n)
    if kind=='emerald':
     path=bez([[side*.10,.0],[side*.80,.24],[side*1.04,.85],[side*.72,1.35]],40)
     tube('Central laurel stem',[tr(x,y,.12) for x,y in path],.017)
     for j in range(7):
      c=path[5+j*4]
      for sign in [-1,1]:petal('Emerald laurel detailed leaf',tr(*c,.14),tr(c[0]+side*(.25 if sign>0 else -.14),c[1]+.25,.15),.075,.055,'gold',n)
  else:
   for side in [-1,1]:
    q=bez([[0,0],[side*.5,.05],[side*.7,.65],[side*.25,.75]],36)
    ribbon('Side fleur scroll',[tr(x,y,.06) for x,y in q],np.linspace(.13,.025,len(q)),.045,'gold',n)
 # A double sided fleur finial rises from the structural hub. All stones on
 # the red crown, including both upper stones, use the ruby profile.
 for face in [1,-1]:
  z=face*.06;n=(0,0,face)
  if kind=='amethyst':
   reference_finial([0,hub+.85,face*.12],n)
   continue
  petal('Top fleur central gold spear',[0,hub+.18,z],[0,hub+1.28,z],.20,.08,'gold',n)
  for side in [-1,1]:
   q=bez([[0,hub+.26,z],[side*.18,hub+1.05,z],[side*1.05,hub+1.04,z],[side*.68,hub+.55,z]],45)
   ribbon('Top fleur curved petal',q,(.055+.34*np.sin(np.linspace(0,np.pi,len(q)))**.7),.08,'gold',n)
   q=bez([[0,hub+.25,z],[side*.31,hub+.10,z],[side*.47,hub+.20,z],[side*.40,hub+.32,z]],30)
   ribbon('Top fleur lower curl',q,np.linspace(.10,.018,len(q)),.04,'gold',n)
  if kind=='amethyst':diamond_setting('Amethyst pointed finial',[0,hub+.85,face*.12],.22,.52,.18,mat,n,.045)
  else:
   gem('Top fleur '+kind+' round stone',[0,hub+.50,face*.18],.105,.105,.12,mat,n)
   diamond_setting('Upper arch '+kind+' diamond',[0,hub+.05,face*.23],.13,.15,.12,mat,n,.022)
 # The leaf centerlines follow the reference crop's actual branching,
 # including the lobes that curl back into the stem instead of a radial fan.
 for side in [-1,1]:
  for back in [False,True]:
   face=-1 if back else 1
   def photo_path(control):
    xy=bez(control,56);sx,sy,rootx={'amethyst':(.0018,.0036,.48),'ruby':(.00265,.0041,.68),'emerald':(.0021,.0033,.85)}[kind]
    q=np.c_[side*(rootx+(580-xy[:,0])*sx),base+.40+(435-xy[:,1])*sy,np.full(len(xy),face*(radius+.22))]
    q[:,2]+=face*.045*np.sin(np.linspace(0,np.pi,len(q)));return q
   if kind=='amethyst':
    paths=[([[570,410],[420,260],[96,105],[35,280]],.26),([[570,405],[435,128],[340,33],[145,20]],.21),([[18,440],[360,460],[456,392],[430,320]],.11)]
   else:
    paths=[([[575,435],[175,355],[137,150],[195,27]],.24),([[190,310],[55,210],[12,205],[35,285]],.21),([[176,260],[56,190],[13,150],[69,188]],.20),([[169,190],[60,116],[32,118],[60,144]],.17),([[175,270],[198,145],[347,68],[349,137]],.24),([[170,210],[190,66],[319,56],[297,88]],.20),([[160,170],[160,0],[253,-6],[223,38]],.22),([[575,435],[220,420],[315,140],[392,230]],.18)]
    if kind=='emerald':paths=[paths[j] for j in [0,1,3,4,6,7]]
   for j,(control,peak) in enumerate(paths):
    path=photo_path(control);f=np.linspace(0,1,len(path));width=(.045+peak*np.sin(np.pi*f)**.72)*(1-f**12)
    ribbon('Reference flowing '+kind+' acanthus lobe '+str(j+1),path,width,.065,'gold',(0,0,face))
    tube('Acanthus raised sculpted vein',path+np.array([0,0,face*.064]),np.linspace(.013,.002,len(path)),'gold',6)
 if kind=='amethyst':
  from reference_gold_relief import side_mask,relief
  for sign in [-1,1]:
   mask,box=side_mask(ROOT/'amethyst_crown/reference.png',sign);p,t=relief(mask,box)
   count=len(p)//2;p[count:,2]=-p[:count,2]
   x=(p[:,0]-768)*(.46*.90)/88
   shift=.18*np.sin(np.clip((p[:,1]-400)/315,0,1)*np.pi)**.6
   x+=sign*shift
   y=-.76+(550-p[:,1])*(.82*.90)/160
   add('Large central reference outer sculpted gold crest',np.c_[x,y,p[:,2]],t,'gold',True)
 if kind=='amethyst':
  from reference_gold_relief import circlet_mask,relief
  mask,box=circlet_mask(ROOT/'amethyst_crown/reference.png');p,t=relief(mask,box)
  for face in [1,-1]:
   x=(p[:,0]-768)*(.46*.90)/88
   y=base+(790-p[:,1])*(.46*.90)/88/(.65*2.15)
   radius_band=radius+.19+p[:,2]
   z=face*np.sqrt(np.maximum(radius_band**2-x*x,.10))
   q=np.c_[x,y,z]
   add('Circlet reference sculpted returning gold scrollwork',q,t if face>0 else t[:,::-1],'gold',True)
 # Restore the tall cut and sculpted detail proportions while bringing the
 # structural dome down to the reference's broad crown silhouette.
 for part in PARTS:
  if any(token in part['name'] for token in ['Large central','Broad beveled central','Central border','Pave gold','Fleur','Central laurel','Emerald laurel','Reference sculpted']):
   part['p'][:,1]=(part['p'][:,1]+.76)/.65-.76+.30
   if kind=='amethyst':part['p'][:,1]=(part['p'][:,1]+1.50)*1.13-1.50+.30
  if any(token in part['name'] for token in ['Circlet','circlet','Continuous solid crown base','Embossed velvet base band','Rolled polished gold crown rim','Base laurel']):
   part['p'][:,1]=base+(part['p'][:,1]-base)*(2.15 if kind=='amethyst' else 1.6)
 PARTS[:]=[p for p in PARTS if p['name'] not in ['Gold fleur lower curled sweep','Fleur raised gold lobed leaf'] and not (kind=='amethyst' and (p['name'].startswith('Reference flowing amethyst') or p['name']=='Acanthus raised sculpted vein'))]
 for part in PARTS:
  if any(token in part['name'] for token in ['Top fleur','Amethyst pointed finial']):part['p'][:,1]=(part['p'][:,1]-hub-.18)/.65+hub+.18
 # A slight fixed display lean reveals the domed cushion and round circlet.
 angle=np.radians(1.5 if kind=='amethyst' else -3);rot=np.array([[1,0,0],[0,np.cos(angle),-np.sin(angle)],[0,np.sin(angle),np.cos(angle)]])
 for part in PARTS:
  part['p'][:,1]*={'amethyst':.65,'ruby':.75,'emerald':.70}[kind];part['p']=part['p']@rot.T;part['p'][:,2]*=.90
 refs={'amethyst':'download.png','ruby':'ChatGPT Image Nov 6, 2026, 04_38_51 PM.png','emerald':'ChatGPT Image Nov 6, 2026, 04_39_00 PM.png'}
 save(kind+'_crown',kind.title()+' Crown',Path('/Users/antonioperedo/Downloads')/refs[kind],dict(connected_arches=8,upper_stone_color=kind,construction='Full round crown, continuous structural arches into shared central hub, real velvet folds, relief ornament, independent convex stones.'))

def compass():
 from ocean_reference import waves,setting,UNIT
 MATERIALS['navy'].update(metallic=.12,roughness=.68,ior=1.1)
 MATERIALS['ocean_water']=dict(color=[.0018,.014,.045],metallic=.28,roughness=.48,ior=1.1)
 MATERIALS['CrestGem_SapphireOcean']=dict(color=[.002,.01,.10],metallic=0.,roughness=.03,ior=1.77)
 # Custom ornamental frame, never a renamed common coin shell.
 a=np.arange(256)*2*np.pi/256
 ring=np.c_[np.cos(a)*2.94,np.sin(a)*2.94]
 contour_band('Custom gold ocean navigator frame',ring,.19,0,.27)
 for z in [-.13,.13]:
  for r,w in [(2.83,.025),(2.68,.035),(2.38,.022)]:circle_z('Concentric engraved gold frame',r,z,width=w)
 # Physical navy drum with a finished back and edge.
 p=np.vstack([np.c_[ring*.934,np.full(256,z)] for z in [-.10,.10]]);t=[]
 p=np.vstack([p,[[0,0,-.10],[0,0,.10]]])
 for i in range(256):
  j=(i+1)%256;t.extend([[512,j,i],[513,i+256,j+256],[i,j,j+256],[i,j+256,i+256]])
 add('Double sided navy nautical chart body',p,t,'navy',False)
 for face in [-1,1]:
  z=face*.15
  # Twisted rope border winds continuously around the entire frame.
  for phase in [0,2*np.pi/3,4*np.pi/3]:
   a=np.linspace(0,2*np.pi,1152,endpoint=False);r=2.57+.040*np.sin(a*58+phase)
   tube('Continuous twisted gold rope',np.c_[r*np.cos(a),r*np.sin(a),z+face*.040*np.cos(a*58+phase)],.045,'gold',8,True)
  # Coastlines are traced from the owner's chart reference, then inset into
  # the navy field as material colored geography by make_chart.py.
  for k in range(8):
   angle=k*np.pi/4;u=np.array([np.sin(angle),np.cos(angle),0]);v=np.array([u[1],-u[0],0]);L=2.48 if k%2==0 else 1.78;w=.30 if k%2==0 else .21
   c=np.array([0,0,z+face*.055]);q=np.array([c+u*L,c+u*.23+v*w,c-u*.15,c+u*.23-v*w,c+u*.32+[0,0,face*.10]])
   hull('Real raised compass '+str(k+1)+' blade',q,'gold')
  circle_z('Central deep gold sapphire bezel',.29,z+face*.30,width=.052)
  gem('Central round ocean sapphire',[0,0,z+face*.31],.245,.245,.22,'CrestGem_SapphireOcean',(0,0,face))
  for k in range(4):
   center,p,t=setting(k);q=np.c_[(p[:,0]-627)*UNIT,(570-p[:,1])*UNIT,face*(.15+p[:,2])]
   add('Reference sculpted cardinal gold setting '+str(k),q,t if face>0 else t[:,::-1],'gold',True)
   c=np.array([(center[0]-627)*UNIT,(570-center[1])*UNIT,face*.30])
   circle_z('Cardinal round gold brilliant seat',.132,c[2]-.025,width=.022,c=c[:2],N=64)
   gem('Cardinal pale blue brilliant',c,.122,.122,.14,'CrestGem_Ice',(0,0,face))
  for name,p,t,material in waves(ROOT/'ocean_navigator/reference.png'):
   base=.27 if material=='gold' else .21
   q=np.c_[(p[:,0]-627)*UNIT,(570-p[:,1])*UNIT,face*(base+p[:,2])]
   add(name,q,t if face>0 else t[:,::-1],material,True)
  for side in [-1,1]:
   pts=bez([[side*.22,2.75,z+face*.09],[side*.46,2.52,z+face*.09],[side*.74,2.83,z+face*.09],[side*.54,2.82,z+face*.09]],44)
   ribbon('Upper cardinal curled gold flourish',pts,np.linspace(.055,.008,len(pts)),.03,'gold',(0,0,face))
  for k in range(120):
   a=k*2*np.pi/120;u=np.array([np.cos(a),np.sin(a),0]);p0=u*2.365+[0,0,z];p1=u*(2.405 if k%5 else 2.435)+[0,0,z]
   tube('Fine engraved nautical dial tick',[p0,p1],.006,'gold',6)
 save('ocean_navigator','Ocean Navigator',Path('/Users/antonioperedo/Downloads/ChatGPT Image Nov 6, 2026, 10_10_54 AM.png'),dict(construction='Custom complete medallion, raised compass, real twisted rope, inset world chart, sculpted layered waves, independent sapphire and pale blue brilliant cuts.'))

if __name__=='__main__':
 todo=sys.argv[1:] or ['heart','amethyst','ruby','emerald','compass']
 for task in todo:
  if task=='heart':heart()
  elif task=='compass':compass()
  else:crown(task)
