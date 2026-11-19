"""Shared physical mesh construction for this three badge run."""
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,distance_transform_edt,map_coordinates
from scipy.spatial import Delaunay,ConvexHull
from scipy.interpolate import CubicSpline

def setup(root,center_x,top,bottom):
 global R,C,W,H,S,CX,TOP,im,yy,xx,groups,arrays
 R=Path(root);C=R/(R/'candidate.txt').read_text().strip()
 im=np.asarray(Image.open(R/'reference.png').convert('RGB'),float)/255
 H,W=im.shape[:2];yy,xx=np.mgrid[:H,:W]
 S=5.47/(bottom-top);CX=center_x;TOP=top;groups=[];arrays={}

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
def relief(name,p,t,z,role,smooth=True,side_role='side'):
 v=world(p,z);t=orient(v,t);back=v.copy();back[:,2]*=-1;n=len(p)
 faces=np.vstack([t,t[:,::-1]+n]);allv=np.vstack([v,back]);alluv=np.vstack([uv(p),uv(p)])
 e=np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);_,ids,cnt=np.unique(np.sort(e,axis=1),axis=0,return_index=True,return_counts=True)
 walls=[]
 for a,b in e[ids[cnt==1]]:walls.extend([(a,b+n,b),(a,a+n,b+n)])
 add(name,allv,faces,role,alluv,smooth)
 add(name+' finished side walls',allv,walls,side_role,alluv,True)
def ring(name,center,radii,profile,role,segments=256):
 # Closed section, wound consistently around both sides of the badge.
 theta=np.linspace(0,2*np.pi,segments,endpoint=False);pts=[]
 for rad,z in profile:
  p=np.c_[center[0]+radii[0]*rad*np.cos(theta),center[1]+radii[1]*rad*np.sin(theta)]
  pts.extend(world(p,z))
 m=len(theta);faces=[]
 for j in range(len(profile)):
  k=(j+1)%len(profile)
  for i in range(m):
   a=j*m+i;b=j*m+(i+1)%m;c=k*m+i;d=k*m+(i+1)%m
   faces.extend([(a,c,b),(b,c,d)])
 coords=[]
 for rad,z in profile:
  coords.extend(uv(np.c_[center[0]+radii[0]*rad*np.cos(theta),center[1]+radii[1]*rad*np.sin(theta)]))
 add(name,np.array(pts),faces,role,np.array(coords),smooth=True)
 groups[-1]['plain_vertical_walls']=True
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
 add(name,pts,faces,role,np.vstack([uv(p) for p,z in profiles]),smooth=False)
 groups[-1]['plain_vertical_walls']=True
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

def triangulate_curve(path,step=12,name='curve'):
 # Blender's constrained triangulation retains the actual smooth contour.
 # Removing unconstrained triangles near a raster border created tiny teeth.
 import sys
 sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'water_match_20261014'))
 from blender_live import command
 path=np.asarray(path,float)
 if np.linalg.norm(path[0]-path[-1])<.01:path=path[:-1]
 if np.cross(path,np.roll(path,-1,axis=0)).sum()<0:path=path[::-1]
 mask=poly(path);distance=distance_transform_edt(mask)
 gy,gx=np.mgrid[0:H:step,0:W:step];inside=distance[gy,gx]>3
 p=np.vstack([path,np.c_[gx[inside],gy[inside]]])
 source=C/('cdt_'+name+'.json');dest=C/('cdt_'+name+'.npz')
 source.write_text(json.dumps(dict(points=p.tolist(),count=len(path))))
 code='''import json,numpy as np
from pathlib import Path
from mathutils import Vector,geometry
d=json.loads(Path(SOURCE).read_text())
out=geometry.delaunay_2d_cdt([Vector(q) for q in d['points']],[],[list(range(d['count']))],1,1e-5,False)
assert all(len(face)==3 for face in out[2])
np.savez_compressed(DEST,points=np.array([q[:] for q in out[0]],float),triangles=np.array(out[2],np.int32))
print('Constrained contour',len(out[0]),len(out[2]))
'''.replace('SOURCE',repr(str(source))).replace('DEST',repr(str(dest)))
 result=command('execute_code',{'code':code});assert dest.exists(),result
 d=np.load(dest);return d['points'],d['triangles']

def ears(p):
 p=np.asarray(p,float);indices=list(range(len(p)));tri=[]
 area=np.cross(p,np.roll(p,-1,axis=0)).sum()
 if area<0:indices.reverse()
 while len(indices)>3:
  for k,b in enumerate(indices):
   a=indices[k-1];c=indices[(k+1)%len(indices)]
   ab=p[b]-p[a];ac=p[c]-p[a];det=np.cross(ab,ac)
   if det<=1e-8:continue
   other=[j for j in indices if j not in [a,b,c]];v=p[other]-p[a]
   u=(v[:,0]*ac[1]-v[:,1]*ac[0])/det;w=(ab[0]*v[:,1]-ab[1]*v[:,0])/det
   if ((u>1e-7)&(w>1e-7)&(u+w<1-1e-7)).any():continue
   tri.append([a,b,c]);indices.pop(k);break
  else:raise ValueError('Polygon needs a clean non intersecting contour')
 tri.append(indices);return np.asarray(tri,np.int32)

def solid(name,outline,seat,crest,role='metal',inset=.05,smooth=False):
 outline=np.asarray(outline,float);signed=np.cross(outline,np.roll(outline,-1,axis=0)).sum()
 edges=np.roll(outline,-1,axis=0)-outline;length=np.linalg.norm(edges,axis=1)
 inward=np.c_[-edges[:,1],edges[:,0]]/length[:,None]*(1 if signed>0 else -1)
 distance=min(float(np.ptp(outline,axis=0).min())*inset,float(length.min())*.45)
 inner=[]
 for i,p in enumerate(outline):
  matrix=np.vstack([inward[i-1],inward[i]])
  if abs(np.linalg.det(matrix))<1e-7:delta=inward[i]*distance
  else:delta=np.linalg.solve(matrix,np.array([distance,distance]))
  delta*=min(1,distance*5/max(np.linalg.norm(delta),1e-10));inner.append(p+delta)
 inner=np.asarray(inner)
 n=len(outline);p=np.vstack([outline,inner]);v=world(p,np.r_[[seat]*n,[crest]*n]);cap=ears(inner)+n
 if signed<0:cap=cap[:,::-1]
 t=[]
 for i in range(n):
  j=(i+1)%n;t.extend([[i,j,n+j],[i,n+j,n+i]])
 t=np.vstack([t,cap]);
 if signed>0:t=t[:,::-1]
 back=v.copy();back[:,2]*=-1;nv=len(v)
 faces=np.vstack([t,t[:,::-1]+nv]);walls=[]
 # All original contour edges are clockwise in image coordinates.
 signed=np.cross(outline,np.roll(outline,-1,axis=0)).sum()
 for i in range(n):
  a,b=(i,(i+1)%n) if signed<0 else ((i+1)%n,i)
  walls.extend([[a,b+nv,b],[a,a+nv,b+nv]])
 vertices=np.vstack([v,back]);coords=np.vstack([uv(p),uv(p)]);idx=add(name,vertices,faces,role,coords,smooth)
 add(name+' side walls',vertices,walls,'side',coords,True)
 return idx

def star(name,x,y,rx,ry,seat=.18,crest=.22,role='metal',diagonal=False):
 outline=[]
 count=16 if diagonal else 8
 for i in range(count):
  angle=-np.pi/2+2*np.pi*i/count;factor=1 if i%2==0 else .18
  outline.append([x+rx*np.cos(angle)*factor,y+ry*np.sin(angle)*factor])
 p=np.vstack([outline,[[x,y]]]);v=world(p,np.r_[[seat]*count,crest]);t=orient(v,[[count,i,(i+1)%count] for i in range(count)])
 n=len(p);back=v.copy();back[:,2]*=-1;faces=list(t)+list(t[:,::-1]+n)
 for i in range(count):j=(i+1)%count;faces.extend([[i,j,j+n],[i,j+n,i+n]])
 return add(name,np.vstack([v,back]),faces,role,np.vstack([uv(p),uv(p)]))

def gem(name,outline,center,seat,crest,style='Sapphire',table=.55):
 outline=np.asarray(outline);center=np.asarray(center);xy=np.vstack([outline,center+(outline-center)*table,center]);z=np.r_[[seat]*len(outline),[seat+(crest-seat)*.76]*len(outline),crest]
 p=world(xy,z);p=np.vstack([p,p*np.array([1,1,-1])]);hull=ConvexHull(p);t=hull.simplices.copy()
 normals=np.cross(p[t[:,1]]-p[t[:,0]],p[t[:,2]]-p[t[:,0]]);flip=(normals*hull.equations[:,:3]).sum(1)<0;t[flip]=t[flip,::-1]
 return add(name,p,t,'CrestGem_'+style,np.vstack([uv(xy),uv(xy)]))

def save(cfg):
 allpoints=np.vstack([arrays[str(i)+'_points'] for i in range(len(groups))]);center_x=float((allpoints[:,0].min()+allpoints[:,0].max())/2)
 for i in range(len(groups)):arrays[str(i)+'_points'][:,0]-=center_x
 np.savez_compressed(C/'geometry.npz',**arrays);(C/'groups.json').write_text(json.dumps(groups,indent=2)+'\n')
 cfg.update(reference_size=[W,H],scale=S,reference_center_x=CX+center_x/S,reference_top=TOP,triangle_count=sum(len(arrays[str(i)+'_triangles']) for i in range(len(groups))))
 (R/'design.json').write_text(json.dumps(cfg,indent=2)+'\n')
 print(cfg['name'],len(groups),'parts,',cfg['triangle_count'],'triangles',flush=True)
