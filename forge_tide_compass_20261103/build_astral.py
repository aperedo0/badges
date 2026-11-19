"""Build the gold celestial dial with nine independent optical sapphires."""
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter,distance_transform_edt,binary_fill_holes,label
from contourpy import contour_generator
from scipy.spatial import ConvexHull
import meshlib as m
from pace import work
work(3)
R=Path(__file__).resolve().parent/'astral_navigator';m.setup(R,627,48,1158)
for folder in ['source','mobile','textures','review']:(m.C/folder).mkdir(parents=True,exist_ok=True)
center=np.array([627,592]);outercenter=[623,603]

def rim(name,c,r,inner,outer,z0,z1):
 segments=256 if r>450 else (192 if r>250 else (128 if r>120 else (80 if r>50 else 48)))
 m.ring(name,c,[r,r],[(outer,z0),(outer-.004,z1-.014),(outer-.012,z1),(inner+.01,z1),(inner,z0),(inner,-z0),(inner+.01,-z1),(outer-.012,-z1),(outer-.004,-z1+.014),(outer,-z0)],'metal',segments)

rim('Engraved gold perimeter case',outercenter,555,.939,1,.12,.23)
rim('Fine gold perimeter lip',outercenter,555,.934,.942,.14,.247)
theta=np.linspace(0,2*np.pi,192,endpoint=False);outline=np.array(outercenter)+np.c_[np.cos(theta),np.sin(theta)]*522
# Complete recessed navy support, shared by the front and matching reverse.
p=np.vstack([outercenter]+[np.array(outercenter)+(outline-np.array(outercenter))*f for f in np.linspace(.08,1,12)])
t=[[0,1+i,1+(i+1)%192] for i in range(192)]
for j in range(11):
 for i in range(192):
  a=1+j*192+i;b=1+j*192+(i+1)%192;c=a+192;d=b+192;t.extend([[a,b,d],[a,d,c]])
m.relief('Engraved navy celestial chart and ornament field',p,np.array(t),.075,'field',True)
rim('Gold outer graduation surround',center,408,.977,1,.12,.20)
rim('Gold inner graduation surround',center,351,.981,1,.12,.183)
rim('Inner compass guide circle',center,190,.981,1,.115,.155)
rim('Inner fine concentric guide',center,177,.994,1,.10,.127)

# Closed raised graduation marks, with plain walls and no face texture on them.
def facet(name,xy,seat,crest,role='metal'):
 xy=np.asarray(xy,float);mid=xy.mean(0);p=np.vstack([xy,mid]);v=m.world(p,np.r_[[seat]*len(xy),crest]);n=len(p)
 tri=m.orient(v,[[len(xy),i,(i+1)%len(xy)] for i in range(len(xy))]);back=v.copy();back[:,2]*=-1;faces=list(tri)+list(tri[:,::-1]+n)
 for i in range(len(xy)):
  j=(i+1)%len(xy);faces.extend([[i,j,j+n],[i,j+n,i+n]])
 # Match the side winding to the front contour, whose image orientation flips.
 if np.cross(xy,np.roll(xy,-1,axis=0)).sum()<0:
  faces=np.array(faces);faces[2*len(xy):]=faces[2*len(xy):,::-1]
 i=m.add(name,np.vstack([v,back]),faces,role,np.vstack([m.uv(p),m.uv(p)]),False);m.groups[i]['plain_vertical_walls']=True
 return i

for i in range(180):
 a=-np.pi/2+2*np.pi*i/180;u=np.array([np.cos(a),np.sin(a)]);v=np.array([-u[1],u[0]])
 length=25 if i%5==0 else (16 if i%2==0 else 11);width=1.35 if i%5==0 else .8
 q=center+u*374;end=center+u*(374-length)
 facet('Raised scale graduation '+str(i+1),[q-v*width/2,q+v*width/2,end+v*width/2,end-v*width/2],.095,.126)

# Eight pointed compass. The four diagonal blades are below the cardinal arms.
for j in range(4):
 a=np.pi/4+j*np.pi/2;u=np.array([np.cos(a),np.sin(a)]);v=np.array([-u[1],u[0]])
 facet('Diagonal gold compass blade '+str(j+1),[center+u*320,center+u*82+v*46,center,center+u*82-v*46],.155,.245)
for j in range(4):
 a=-np.pi/2+j*np.pi/2;u=np.array([np.cos(a),np.sin(a)]);v=np.array([-u[1],u[0]])
 radius=379 if j%2==0 else 401
 facet('Gold and navy cardinal compass arm '+str(j+1),[center+u*radius,center+u*74+v*68,center,center+u*74-v*68],.24,.355)

# Gold faceted outer diagonal markers and four small circular axis buttons.
for j in range(4):
 a=-3*np.pi/4+j*np.pi/2;u=np.array([np.cos(a),np.sin(a)]);v=np.array([-u[1],u[0]]);c=center+u*379
 facet('Diagonal faceted graduation marker '+str(j+1),[c+u*24,c+v*12,c-u*22,c-v*12],.17,.235)

def round_gem(name,c,r,seat,crest):
 # Opposed real brilliant cuts have pavilion facets instead of a long prism.
 # The two culets remain separated inside the gold mount.
 source=np.load(R.parent/'brilliant_reference.npz');raw=source['points'];tri=source['triangles']
 unique,inverse=np.unique(np.round(raw,7),axis=0,return_inverse=True);tri=inverse[tri]
 s=r*m.S/3.12;xycenter=m.world([c],0)[0]
 p=np.c_[unique[:,0]*s+xycenter[0],unique[:,2]*s+xycenter[1],crest-(2.349-unique[:,1])*s]
 assert p[:,2].min()>0
 for back in [False,True]:
  q=p.copy();faces=tri[:,::-1].copy()
  if back:q[:,2]*=-1;faces=faces[:,::-1]
  m.add(name+(' reverse brilliant' if back else ' front brilliant'),q,faces,'CrestGem_SapphireAstral')

def diamond_gem(name,outline,c,seat,crest):
 outline=np.asarray(outline);c=np.asarray(c);xy=np.vstack([outline,c+(outline-c)*.49,c]);z=np.r_[[seat]*4,[crest]*4,seat-.28]
 p=m.world(xy,z);hull=ConvexHull(p);tri=hull.simplices.copy();norm=np.cross(p[tri[:,1]]-p[tri[:,0]],p[tri[:,2]]-p[tri[:,0]]);flip=(norm*hull.equations[:,:3]).sum(1)<0;tri[flip]=tri[flip,::-1]
 for back in [False,True]:
  q=p.copy();faces=tri.copy()
  if back:q[:,2]*=-1;faces=faces[:,::-1]
  m.add(name+(' reverse cut' if back else ' front cut'),q,faces,'CrestGem_SapphireAstral')

rim('Central sapphire stepped gold bezel',center,87,.80,1,.34,.46)
rim('Central sapphire fine inner lip',center,72,.96,1.02,.40,.477)
round_gem('Central round faceted sapphire',center,69,.405,.61)

for j,c in enumerate([[297,281],[958,281],[297,907],[958,907]]):
 rim('Outer sapphire gold setting '+str(j+1),c,31,.72,1,.115,.20)
 round_gem('Outer round sapphire '+str(j+1),c,22,.17,.28)

for j in range(4):
 a=-np.pi/2+j*np.pi/2;u=np.array([np.cos(a),np.sin(a)]);v=np.array([-u[1],u[0]]);c=center+u*204
 long=41 if j%2==0 else 38;short=18
 outer=np.array([c+u*(long+6),c+v*(short+6),c-u*(long+6),c-v*(short+6)])
 inner=np.array([c+u*long,c+v*short,c-u*long,c-v*short])
 m.band('Cardinal sapphire gold diamond setting '+str(j+1),inner,outer,.36,.40,'metal',True)
 diamond_gem('Cardinal marquise sapphire '+str(j+1),inner,c,.375,.475)

# Trace the actual gold scrollwork, crescents, tiny stars and studs in the
# reference annulus. This preserves their asymmetry and small leaf tips.
rr=np.sqrt((m.xx-center[0])**2+(m.yy-center[1])**2);rgb=m.im
gold=(rgb[...,0]>rgb[...,2]*1.29)&(rgb[...,0]>rgb[...,1]*1.035)&(rgb[...,0]>.28)
orn=gold&(rr>425)&(rr<506)
for x,y in [[297,281],[958,281],[297,907],[958,907]]:orn&=(m.xx-x)**2+(m.yy-y)**2>37**2
orn=gaussian_filter(orn.astype(float),.55)>.40
components,count=label(orn);areas=np.bincount(components.ravel());orn&=areas[components]>10
orn=binary_fill_holes(orn)
loops=contour_generator(z=orn.astype(float)).lines(.5)
parts=[]
for loop in loops:
 if len(loop)<8 or np.linalg.norm(loop[0]-loop[-1])>.1:continue
 # Subsample smooth contours without replacing the actual ornament with repeats.
 loop=loop[::2]
 if len(loop)<4:continue
 area=abs(np.cross(loop,np.roll(loop,-1,axis=0)).sum())/2
 if area<10:continue
 parts.append(loop)
for i,loop in enumerate(parts):
 p,t=m.triangulate_curve(loop,7,'ornament_'+str(i));mask=m.poly(loop);d=gaussian_filter(distance_transform_edt(mask),1.5)
 h=.105+.022*(1-np.exp(-d/3));z=m.map_coordinates(h,[p[:,1],p[:,0]],order=1)
 m.relief('Reference traced gold scroll and celestial ornament '+str(i+1),p,t,z,'metal',True)

# Four cardinal studs overlap the scale borders just as in the reference.
for i,c in enumerate([[627,196],[1026,589],[627,987],[221,589]]):
 a=np.linspace(0,2*np.pi,12,endpoint=False);facet('Circular cardinal stud '+str(i+1),np.array(c)+np.c_[np.cos(a),np.sin(a)]*9,.15,.195)

m.save(dict(name='Astral Navigator',selection='astralNavigator',bounds=[68,48,1178,1158],textured_roles=['metal','field'],metal_roles=['metal'],desired_colors={'metal':[.48,.245,.067]},roughness={'metal':.30,'field':.52},side_color=[.19,.115,.045],side_roughness=.49,method='Concentric engraved gold dial, 180 physical scale marks, eight raised compass blades, reference traced scrolls and crescent ornaments, nine front Sapphire stones with nine matching reverse stones. Each is independently closed and convex with real crown and pavilion facets. Reference thin frame is local to this design and preserves all approved shared coin assets.'))
print('Traced ornament components:',len(parts))
