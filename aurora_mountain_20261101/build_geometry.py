"""Reference traced rock relief, physical metal frame and path, and a convex amethyst."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,distance_transform_edt,binary_closing,binary_fill_holes,label,map_coordinates
from scipy.spatial import Delaunay,ConvexHull
from scipy.interpolate import CubicSpline,LinearNDInterpolator
R=Path(__file__).resolve().parent;C=R/(R/'candidate.txt').read_text().strip();W=H=1254
im=np.asarray(Image.open(R/'reference.png').convert('RGB'),float)/255
yy,xx=np.mgrid[:H,:W];S=5.47/1195;CX=627.;TOP=10.
groups=[];arrays={}
def world(p,z):
 p=np.asarray(p);return np.c_[(p[:,0]-CX)*S,3.015-(p[:,1]-TOP)*S,np.broadcast_to(z,len(p))]
def uv(p):return np.c_[p[:,0]/W,1-p[:,1]/H]
def add(name,p,t,role,coords=None,smooth=False):
 i=len(groups);arrays[str(i)+'_points']=np.asarray(p,np.float32);arrays[str(i)+'_triangles']=np.asarray(t,np.int32)
 arrays[str(i)+'_uv']=np.asarray(coords if coords is not None else np.zeros((len(p),2)),np.float32)
 groups.append(dict(name=name,role=role,smooth=smooth));return i
def poly(points):
 a=Image.new('L',(W,H));ImageDraw.Draw(a).polygon([tuple(p) for p in points],fill=255);return np.asarray(a)>0
def smooth_loop(p,n=256):
 p=np.asarray(p,float);p=np.vstack([p,p[0]])
 d=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];return CubicSpline(d,p,bc_type='periodic')(np.linspace(0,d[-1],n,endpoint=False))
def orient(p,t):
 t=np.array(t,np.int32);cr=np.cross(p[t[:,1]]-p[t[:,0]],p[t[:,2]]-p[t[:,0]])
 t[cr[:,2]<0]=t[cr[:,2]<0,::-1];return t
def relief(name,p,t,z,role):
 v=world(p,z);t=orient(v,t);back=v.copy();back[:,2]*=-1;n=len(p)
 faces=np.vstack([t,t[:,::-1]+n]);allv=np.vstack([v,back]);alluv=np.vstack([uv(p),uv(p)])
 e=np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);_,ids,cnt=np.unique(np.sort(e,axis=1),axis=0,return_index=True,return_counts=True)
 walls=[]
 for a,b in e[ids[cnt==1]]:walls.extend([(a,b+n,b),(a,a+n,b+n)])
 add(name,allv,faces,role,alluv,True)
 add(name+' finished side walls',allv,walls,'rock_edge' if role=='rock' else 'gold_side',alluv,True)
def ring(name,center,radii,profile,role):
 # Closed section, wound consistently around both sides of the badge.
 theta=np.linspace(0,2*np.pi,256,endpoint=False);pts=[]
 for rad,z in profile:
  p=np.c_[center[0]+radii[0]*rad*np.cos(theta),center[1]+radii[1]*rad*np.sin(theta)]
  pts.extend(world(p,z))
 m=len(theta);faces=[]
 for j in range(len(profile)):
  k=(j+1)%len(profile)
  for i in range(m):
   a=j*m+i;b=j*m+(i+1)%m;c=k*m+i;d=k*m+(i+1)%m
   faces.extend([(a,c,b),(b,c,d)])
 add(name,np.array(pts),faces,role,smooth=True)
def band(name,inner,outer,seat,crest,role,ridge=False):
 # A real beveled, closed band with identical sculpted faces on the rear.
 inner=np.asarray(inner);outer=np.asarray(outer);m=len(inner)
 profiles=[(inner,seat),(inner*.86+outer*.14,crest),(inner*.14+outer*.86,crest),(outer,seat),
           (outer,-seat),(inner*.14+outer*.86,-crest),(inner*.86+outer*.14,-crest),(inner,-seat)]
 if ridge:
  mid=inner*.44+outer*.56
  profiles=[(inner,seat+.025),(mid,crest),(outer,seat),(outer,-seat),(mid,-crest),(inner,-seat-.025)]
 pts=np.vstack([world(p,z) for p,z in profiles]);faces=[]
 for j in range(len(profiles)):
  k=(j+1)%len(profiles)
  for i in range(m):
   a=j*m+i;b=j*m+(i+1)%m;c=k*m+i;d=k*m+(i+1)%m
   faces.extend([(a,b,d),(a,d,c)])
 add(name,pts,faces,role,smooth=False)
def triangulate_mask(mask,step=12):
 sdf=gaussian_filter(distance_transform_edt(mask)-distance_transform_edt(~mask),.65)
 a=sdf[:-1,:-1];b=sdf[:-1,1:];c=sdf[1:,1:];d=sdf[1:,:-1]
 active=((a>=0)!=(b>=0))|((b>=0)!=(c>=0))|((c>=0)!=(d>=0))|((d>=0)!=(a>=0))
 boundary=[]
 for y,x in zip(*np.nonzero(active)):
  vals=[a[y,x],b[y,x],c[y,x],d[y,x]];corners=[(x,y),(x+1,y),(x+1,y+1),(x,y+1)]
  for i,j in [(0,1),(1,2),(2,3),(3,0)]:
   if (vals[i]>=0)!=(vals[j]>=0):
    f=vals[i]/(vals[i]-vals[j]);boundary.append(np.array(corners[i])*(1-f)+np.array(corners[j])*f)
 boundary=np.asarray(boundary);_,index=np.unique(np.round(boundary/3),axis=0,return_index=True);boundary=boundary[index]
 gy,gx=np.mgrid[0:H:step,0:W:step];inside=mask[gy,gx]
 p=np.vstack([boundary,np.c_[gx[inside],gy[inside]]]);t=Delaunay(p).simplices
 q=p[t];tests=np.stack([q.mean(1),(q[:,0]+q[:,1])/2,(q[:,1]+q[:,2])/2,(q[:,2]+q[:,0])/2],1)
 good=(map_coordinates(sdf,[tests[:,:,1].ravel(),tests[:,:,0].ravel()],order=1).reshape(-1,4)>-.15).all(1);t=t[good]
 # A contour touching itself at one vertex needs separate physical wall fans.
 e=np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);_,ids,cnt=np.unique(np.sort(e,axis=1),axis=0,return_index=True,return_counts=True)
 boundary=e[ids[cnt==1]];degree=np.bincount(boundary.ravel(),minlength=len(p));points=p.tolist()
 for vertex in np.flatnonzero(degree>2):
  remaining=set(np.flatnonzero((t==vertex).any(1)).tolist());fans=[]
  while remaining:
   seed=remaining.pop();fan={seed};queue=[seed]
   while queue:
    face=queue.pop();neighbors=set(t[face].tolist())-{int(vertex)}
    linked=[other for other in remaining if neighbors.intersection(set(t[other].tolist())-{int(vertex)})]
    for other in linked:remaining.remove(other);fan.add(other);queue.append(other)
   fans.append(sorted(fan))
  for fan in fans:
   center=np.asarray([points[int(index)] for index in np.unique(t[fan])]).mean(0);direction=center-p[vertex];direction/=max(np.linalg.norm(direction),1e-10)
   index=len(points);points.append((p[vertex]+direction*.012).tolist())
   for face in fan:t[face,t[face]==vertex]=index
 p=np.asarray(points)
 return p,t
# Start with the complete approved template as a scale guide in Blender.
# The reference uses a custom double frame, so no coin casing names are reused.
theta=np.linspace(0,2*np.pi,512,endpoint=False)
circle=np.c_[627+550*np.cos(theta),602+550*np.sin(theta)]
p=np.vstack([circle,[[627,602]]]);t=np.array([(512,i,(i+1)%512) for i in range(512)])
relief('Aurora sky and purple channel',p,t,np.full(len(p),.055),'sky')
ring('Outer warm silver frame',(627,602),(591,591),[(1,.105),(.995,.155),(.986,.185),(.938,.185),(.930,.155),(.930,-.155),(.938,-.185),(.986,-.185),(.995,-.155),(1,-.105)],'silver')
for rad in [591.6,550]:
 ring('Fine gold perimeter '+str(rad),(627,602),(rad,rad),[(1,.14),(.999,.19),(.996,.205),(.993,.19),(.993,-.19),(.996,-.205),(.999,-.19),(1,-.14)],'gold_trim')
# The lower inward sweep is traced separately from the circular outer frame.
inner=smooth_loop([(627,83),(832,126),(1009,267),(1106,454),(1118,603),(1064,797),(951,907),(821,964),(706,1028),(627,1081),(546,1026),(403,966),(274,904),(176,791),(131,613),(149,438),(261,257),(430,130)])
direction=inner-np.array([627,590]);direction/=np.linalg.norm(direction,axis=1)[:,None]
width=5+29*np.clip((inner[:,1]-100)/950,0,1)**1.15
outer=inner+direction*width[:,None]
frame_mask=poly(outer)&~poly(inner)
band('Swept silver inner frame',inner,outer,.165,.218,'silver')
band('Inner frame gold inner fillet',inner-direction*2,inner+direction*1.4,.235,.242,'gold_trim')
band('Inner frame gold outer fillet',outer-direction*1.2,outer+direction*1.6,.235,.242,'gold_trim')
# The aurora is luminous atmospheric artwork. Metal and gemstone optics are separate.
mountain_outline=[(183,769),(268,712),(369,634),(412,657),(643,403),(876,628),(913,610),(1070,737),(1100,785),(1070,880),(950,960),(820,1000),(700,1062),(628,1090),(548,1055),(400,1008),(266,937),(191,851)]
mountain=poly(mountain_outline)&poly(inner)
p,t=triangulate_mask(mountain,12)
anchors=np.array([(183,769,.09),(369,634,.22),(412,657,.11),(643,403,.24),(645,529,.43),(570,518,.28),(490,600,.29),(876,628,.12),(913,610,.23),(1070,737,.11),(1100,785,.09),(1070,880,.09),(950,960,.12),(820,1000,.10),(700,1062,.09),(628,1090,.08),(548,1055,.09),(400,1008,.12),(266,937,.09),(191,851,.08),(495,746,.35),(384,855,.13),(732,730,.27),(853,840,.26),(638,800,.12),(550,960,.10)])
z=LinearNDInterpolator(anchors[:,:2],anchors[:,2],fill_value=.085)(p)
relief('Indigo mountain ridges and snow',p,t,z,'rock')
# The actual gold road contour is traced from its warm pixels, not substituted.
allowed=poly([(636,528),(658,528),(710,605),(709,632),(639,661),(662,678),(782,703),(861,735),(881,765),(858,800),(776,838),(632,879),(551,918),(557,952),(622,1008),(588,1035),(483,1004),(390,956),(393,917),(451,876),(602,826),(779,777),(811,758),(796,743),(721,716),(620,689),(599,675),(598,655),(619,636),(682,614),(681,594),(645,548)])
warm=(im[:,:,0]>im[:,:,1]*1.025)&(im[:,:,1]>im[:,:,2]*1.12)&(im[:,:,0]>.30)
path=binary_fill_holes(binary_closing(warm&allowed,iterations=7))
components,_=label(path);sizes=np.bincount(components.ravel());sizes[0]=0;path=components==sizes.argmax()
path=gaussian_filter(path.astype(float),2.0)>.45
p,t=triangulate_mask(path,5)
road_z=.55-(p[:,1]-530)*.00075
rounding=gaussian_filter(distance_transform_edt(path),3.0)
road_z+=.018*(1-np.exp(-map_coordinates(rounding,[p[:,1],p[:,0]],order=1)/12))
path_index=len(groups)
relief('Winding gold summit path',p,t,road_z,'gold')
# Evaluate the actual smooth ribbon gradient instead of averaging skinny edge triangles.
road_field=.55-(yy-530)*.00075+.018*(1-np.exp(-rounding/12))
dy,dx=np.gradient(road_field)
sample=lambda field:map_coordinates(field,[p[:,1],p[:,0]],order=1,mode='nearest')
hint=np.c_[-sample(dx)/S,sample(dy)/S,np.ones(len(p))];hint/=np.linalg.norm(hint,axis=1)[:,None]
rear=hint.copy();rear[:,2]*=-1
arrays[str(path_index)+'_normal_hints']=np.vstack([hint,rear]).astype(np.float32)
sdf=gaussian_filter(distance_transform_edt(path)-distance_transform_edt(~path),3)
dy,dx=np.gradient(sdf);wall_hint=np.c_[-sample(dx),sample(dy),np.zeros(len(p))];wall_hint/=np.maximum(np.linalg.norm(wall_hint,axis=1)[:,None],1e-8)
arrays[str(path_index+1)+'_normal_hints']=np.vstack([wall_hint,wall_hint]).astype(np.float32)
Image.fromarray(np.uint8(path)*255).save(C/'review/path_trace.png')
def star(name,cx,cy,rx,ry,seat=.13,crest=.23):
 outline=np.array([(cx,cy-ry),(cx+rx*.15,cy-ry*.15),(cx+rx,cy),(cx+rx*.15,cy+ry*.15),(cx,cy+ry),(cx-rx*.15,cy+ry*.15),(cx-rx,cy),(cx-rx*.15,cy-ry*.15)])
 p=np.vstack([outline,[[cx,cy]]]);z=np.r_[[seat]*8,crest];v=world(p,z);t=orient(v,[(8,i,(i+1)%8) for i in range(8)]);back=v.copy();back[:,2]*=-1
 faces=list(t)+list(t[:,::-1]+9)
 for i in range(8):j=(i+1)%8;faces.extend([(i,j,j+9),(i,j+9,i+9)])
 add(name,np.vstack([v,back]),faces,'star',np.vstack([uv(p),uv(p)]))
 return outline
mainstar=star('Four point guiding gold star',638,234,141,145,.15,.205)
star_outlines=[mainstar]
star('Luminous guiding star center',638,234,14,15,.213,.222)
groups[-1]['role']='star_core'
for i,(x,y,rx,ry) in enumerate([(407,221,24,28),(404,326,28,54),(230,583,22,25),(196,540,13,17),(487,165,6,7),(798,159,5,6),(860,230,7,9),(372,1027,24,26),(454,1063,19,25),(811,1061,19,27),(882,1027,24,26)]):
 star_outlines.append(star('Small gold star '+str(i),x,y,rx,ry,.10,.106))
 groups[-1]['role']='star_minor'
# A real beveled setting surrounds one closed faceted convex amethyst.
outer=np.array([(628,957),(721,1074),(628,1205),(533,1074)],float)
inner_gem=np.array([(628,1003),(682,1074),(628,1163),(574,1074)],float)
band('Gold amethyst diamond setting',inner_gem,outer,.22,.29,'gold',ridge=True)
center=np.array([628,1074]);table=center+(inner_gem-center)*.54
xy=np.vstack([inner_gem,table,center]);zz=np.r_[[.30]*4,[.49]*4,.55]
v=world(xy,zz);v=np.vstack([v,v*np.array([1,1,-1])]);hull=ConvexHull(v);t=hull.simplices.copy()
norm=np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]);flip=(norm*hull.equations[:,:3]).sum(1)<0;t[flip]=t[flip,::-1]
add('Closed faceted amethyst',v,t,'CrestGem_Amethyst',np.vstack([uv(xy),uv(xy)]))
# Remove all photographed foreground from the atmospheric layer.
sky=im.copy();erase=np.zeros((H,W),bool)
for outline in star_outlines:erase|=poly(outline)
for x,y,rx,ry in [(407,221,26,30),(404,326,30,56),(230,583,24,27),(196,540,15,19)]:
 erase|=((xx-x)/rx)**2+((yy-y)/ry)**2<1
known=~binary_closing(erase,iterations=3);_,near=distance_transform_edt(~known,return_indices=True);sky[~known]=sky[tuple(near[:,~known])]
sky[mountain]=[.018,.024,.08]
sky[frame_mask]=[.018,.012,.055]
sky[poly(outer)|poly(inner_gem)]=[.018,.012,.055]
# No photographed gold path remains on the mountain under the raised metal.
rock=im.copy();known=~binary_closing(path,iterations=3)
_,near=distance_transform_edt(~known,return_indices=True);rock[~known]=rock[tuple(near[:,~known])]
Image.fromarray(np.uint8(sky*255+.5)).resize((1024,1024),Image.Resampling.LANCZOS).save(C/'textures/sky_target.png')
Image.fromarray(np.uint8(rock*255+.5)).resize((1024,1024),Image.Resampling.LANCZOS).save(C/'textures/rock_target.png')
np.savez_compressed(C/'geometry.npz',**arrays)
(C/'groups.json').write_text(json.dumps(groups,indent=2)+'\n')
(R/'design.json').write_text(json.dumps(dict(name='Aurora Mountain',selection='auroraMountain',scale=S,reference_top=TOP,reference_center_x=CX,
 method='Reference traced rock relief and gold road, two physical metal frames, independent convex amethyst, luminous aurora artwork',custom_frame=True,
 triangle_count=sum(len(arrays[str(i)+'_triangles']) for i in range(len(groups)))),indent=2)+'\n')
print('Built',len(groups),'parts;',sum(len(arrays[str(i)+'_triangles']) for i in range(len(groups))),'triangles')
