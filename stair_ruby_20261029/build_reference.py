"""Trace the actual crest contours and build continuous sculpted relief."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,distance_transform_edt,binary_closing,binary_fill_holes,label,map_coordinates
from scipy.spatial import Delaunay
ROOT=Path(__file__).resolve().parent;key=sys.argv[1];R=ROOT/key;C=R/(R/'candidate.txt').read_text().strip();C.mkdir(parents=True,exist_ok=True)
(C/'textures').mkdir(exist_ok=True);(C/'mobile').mkdir(exist_ok=True)
cfg=json.loads((R/'design.json').read_text());im=np.asarray(Image.open(R/'reference.png').convert('RGB'),float)/255;H,W=im.shape[:2];y,x=np.mgrid[:H,:W];lum=im@np.array([.2126,.7152,.0722])
def sample(a,p):return map_coordinates(a,[p[:,1],p[:,0]],order=1,mode='nearest')
def poly(points):
 a=Image.new('L',(W,H));ImageDraw.Draw(a).polygon([tuple(p) for p in points],fill=255);return np.asarray(a)>0
mask=(lum>cfg.get('threshold',.17))|((im[...,2]>im[...,0]*1.15)&(im[...,2]>cfg.get('blue_threshold',.38)))
if cfg.get('preserve_dark_metal'):
 allowed=np.zeros((H,W),bool)
 for region in cfg.get('regions',[]):allowed|=poly(region['outline'])
 if cfg.get('dark_metal_interior'):
  dcx,dcy,drx,dry=cfg['dark_metal_interior'];allowed|=((x-dcx)/drx)**2+((y-dcy)/dry)**2<=1
 warm=(im[...,0]-im[...,1]>.02)&(im[...,0]-im[...,2]>.045)&(im[...,0]>.045)
 mask|=warm&allowed
if cfg.get('disc'):
 cx,cy,rx,ry=cfg['disc'];disc_mask=((x-cx)/rx)**2+((y-cy)/ry)**2<1
 mask=disc_mask if cfg.get('clean_disc') else mask|disc_mask
for ring in cfg.get('solid_rings',[]):
 cx,cy,rx,ry=ring['ellipse'];rr=((x-cx)/rx)**2+((y-cy)/ry)**2;mask|=(rr<1)&(rr>ring.get('inner',.91)**2)
for points in cfg.get('include',[]):mask|=poly(points)
for points in cfg.get('holes',[]):mask&=~poly(points)
for feature in cfg.get('gems',[]):
 if feature.get('bezel'):
  mask|=poly(feature['bezel']['outline'])
  if feature['bezel'].get('inner'):mask&=~poly(feature['bezel']['inner'])
mask=binary_closing(mask,iterations=cfg.get('close_iterations',2))
if cfg.get('remove_upper_glow'):mask[(y<205)&(abs(x-627)<280)]=False
lo_x,lo_y,hi_x,hi_y=cfg['bounds'];mask&=(x>=lo_x)&(x<=hi_x)&(y>=lo_y)&(y<=hi_y)
if cfg.get('lower_clip'):mask&=(y<=950)|poly(cfg['lower_clip'])
components,n=label(mask);sizes=np.bincount(components.ravel());mask&=sizes[components]>=cfg.get('min_component',150)
holes=binary_fill_holes(mask)&~mask;hl,_=label(holes);hs=np.bincount(hl.ravel());mask|=holes&(hs[hl]<cfg.get('fill_holes',800))
dist=distance_transform_edt(mask);sdf=gaussian_filter(dist-distance_transform_edt(~mask),cfg.get('contour_smoothing',.55))
z=np.full((H,W),.075) if cfg.get('field') else .105+.085*(1-np.exp(-dist/20))
for ring in cfg.get('rings',[]):
 cx,cy,rx,ry=ring['ellipse'];rr=np.sqrt(((x-cx)/rx)**2+((y-cy)/ry)**2);band=ring['band'];d=np.maximum(0,1-abs(rr-1)/band);z+=ring['rise']*np.sin(d*np.pi/2)**1.5
for region in cfg.get('regions',[]):
 m=poly(region['outline'])
 for hole in region.get('holes',[]):m&=~poly(hole)
 dd=distance_transform_edt(m);target=region['seat']+region['rise']*(1-np.exp(-dd/region.get('width',20)));weight=gaussian_filter(m.astype(float),2);z=z*(1-weight)+target*weight
z=gaussian_filter(z,4.)
# Use true planar stone facets and step faces, not lighting in a normal map.
for feature in cfg.get('facets',[]):
 outline=np.array(feature['outline'],float);center=np.array(feature.get('center',outline.mean(0)),float)
 for a,b in zip(outline,np.roll(outline,-1,axis=0)):
  q=np.vstack([a,b,center]);zz=np.array([feature['seat'],feature['seat'],feature['crest']]);aa=q[1]-q[0];bb=q[2]-q[0];det=aa[0]*bb[1]-aa[1]*bb[0]
  if abs(det)<1e-8:continue
  gx=x-q[0,0];gy=y-q[0,1];u=(gx*bb[1]-gy*bb[0])/det;v=(aa[0]*gy-aa[1]*gx)/det;m=(u>=0)&(v>=0)&(u+v<=1)
  z[m]=(zz[0]*(1-u-v)+zz[1]*u+zz[2]*v)[m]
facet_points=[]
for feature in cfg.get('facets',[])+cfg.get('gems',[]):
 for outline in [feature['outline']]+([feature['bezel']['outline']] if feature.get('bezel') else []):
  polygon=np.array(outline,float)
  if 'center' in feature:facet_points.append(np.array(feature['center']))
  for a,b in zip(polygon,np.roll(polygon,-1,axis=0)):
   f=np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/3)))[:,None];facet_points.extend(a*(1-f)+b*f)
# Preserve the silhouette with subpixel marching square intersections.
a=sdf[:-1,:-1];b=sdf[:-1,1:];c=sdf[1:,1:];d=sdf[1:,:-1]
active=((a>=0)!=(b>=0))|((b>=0)!=(c>=0))|((c>=0)!=(d>=0))|((d>=0)!=(a>=0))
segments=[]
for yy,xx in zip(*np.nonzero(active)):
 vals=[a[yy,xx],b[yy,xx],c[yy,xx],d[yy,xx]];corners=[(xx,yy),(xx+1,yy),(xx+1,yy+1),(xx,yy+1)];cross=[]
 for i,j in [(0,1),(1,2),(2,3),(3,0)]:
  if (vals[i]>=0)!=(vals[j]>=0):
   f=vals[i]/(vals[i]-vals[j]);cross.append(np.array(corners[i])*(1-f)+np.array(corners[j])*f)
 if len(cross)==2:segments.append(cross)
 elif len(cross)==4:segments.extend([[cross[0],cross[1]],[cross[2],cross[3]]])
boundary=np.concatenate(segments);_,idx=np.unique(np.round(boundary/1.5).astype(int),axis=0,return_index=True);boundary=boundary[np.sort(idx)]
pts=[boundary]
for step,lo,hi in [(3.6,0,7),(6.,7,24),(8.,24,2000)]:
 yy,xx=np.mgrid[0:H:step,0:W:step];p=np.c_[xx.ravel(),yy.ravel()];dd=sample(dist,p)
 pts.append(p[(sample(sdf,p)>0)&(dd>=lo)&(dd<hi)])
if key=='crescent_ocean':pts.append(np.vstack([outer,[[894,477]]]))
if facet_points:pts.append(np.array(facet_points))
p=np.round(np.vstack(pts),2);_,idx=np.unique(p,axis=0,return_index=True);p=p[np.sort(idx)]
t=Delaunay(p).simplices;q=p[t]
tests=np.stack([q.mean(1),(q[:,0]+q[:,1])/2,(q[:,1]+q[:,2])/2,(q[:,2]+q[:,0])/2],1)
t=t[(sample(sdf,tests.reshape(-1,2)).reshape(-1,4)>-.40).all(1)]
q=p[t];a0=q[:,1]-q[:,0];b0=q[:,2]-q[:,0];t=t[abs(a0[:,0]*b0[:,1]-a0[:,1]*b0[:,0])>.002]
used=np.unique(t);lookup=np.full(len(p),-1);lookup[used]=np.arange(len(used));p=p[used];t=lookup[t]
# Separate contour fans that meet at only one point. Their physical walls must
# form individual closed loops rather than intersecting along a vertical edge.
edges=np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);_,ids,counts=np.unique(np.sort(edges,axis=1),axis=0,return_index=True,return_counts=True)
boundary_edges=edges[ids[counts==1]];degree=np.bincount(boundary_edges.ravel(),minlength=len(p));points=p.tolist()
for vertex in np.flatnonzero(degree>2):
 incident=np.flatnonzero((t==vertex).any(1));remaining=set(incident.tolist());fans=[]
 while remaining:
  seed=remaining.pop();fan={seed};queue=[seed]
  while queue:
   face=queue.pop();neighbors=set(t[face].tolist())-{int(vertex)}
   linked=[other for other in remaining if neighbors.intersection(set(t[other].tolist())-{int(vertex)})]
   for other in linked:remaining.remove(other);fan.add(other);queue.append(other)
  fans.append(sorted(fan))
 for fan in fans:
  center=np.array([points[int(index)] for index in np.unique(t[fan])]).mean(0);direction=center-p[vertex];direction/=max(np.linalg.norm(direction),1e-10)
  index=len(points);points.append((p[vertex]+direction*.008).tolist())
  for face in fan:t[face,t[face]==vertex]=index
p=np.array(points)
aa=p[t[:,1]]-p[t[:,0]];bb=p[t[:,2]]-p[t[:,0]];area=aa[:,0]*bb[:,1]-aa[:,1]*bb[:,0];t[area>0]=t[area>0,::-1]
lo=p.min(0);hi=p.max(0);scale=min(5.47/(hi[1]-lo[1]),6.6/(hi[0]-lo[0]));center=(hi+lo)/2
v=np.c_[(p[:,0]-center[0])*scale,3.015-(p[:,1]-lo[1])*scale,sample(z,p)]
# Real, continuous thickness with the same sculpting and reference marks on the rear.
edges=np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);_,ids,count=np.unique(np.sort(edges,axis=1),axis=0,return_index=True,return_counts=True);be=edges[ids[count==1]]
nv=len(v);back=v.copy();back[:,2]*=-1
front=np.vstack([v,back]);faces=np.vstack([t,t[:,::-1]+nv]);uv=np.vstack([np.c_[p[:,0]/W,1-p[:,1]/H]]*2)
walls=[];wallf=[];walluv=[];wallroles=[]
for i,(aa,bb) in enumerate(be):
 pa,pb=v[aa],v[bb];walls.extend([pa,pb,back[bb],back[aa]]);wallf.extend([(4*i,4*i+2,4*i+1),(4*i,4*i+3,4*i+2)])
 samplecolor=np.array([sample(im[...,k],p[[aa,bb]]).mean() for k in range(3)])
 role=1 if cfg.get('metal_hue')=='bronze' and samplecolor[0]>samplecolor[2]*1.35 and samplecolor[1]>samplecolor[2]*1.12 else 0
 if samplecolor[2]>samplecolor[0]*1.15:role=2
 wallroles.extend([role]*2)
np.savez_compressed(C/'geometry.npz',points=front,triangles=faces,uv=uv,wall_points=np.array(walls),wall_triangles=np.array(wallf),wall_roles=np.array(wallroles),reference_points=p,height=z,mask=mask,sdf=sdf)
Image.fromarray(np.uint8(mask)*255).save(C/'silhouette.png')
debug=np.uint8(im*255);debug[~mask]//=4;Image.fromarray(debug).save(C/'traced_shapes.png')
# Pad the atlas with nearby surface colors so filtering never introduces black borders.
color_mask=mask.copy()
for feature in cfg.get('gems',[]):color_mask|=poly(feature['outline'])
_,nearest=distance_transform_edt(~color_mask,return_indices=True);padded=im.copy();padded[~color_mask]=im[tuple(nearest[:,~color_mask])]
Image.fromarray(np.uint8(padded*255+.5)).resize((1024,1024),Image.Resampling.LANCZOS).save(C/'target_reference.png')
trace={'name':cfg['name'],'reference_size':[W,H],'reference_bounds':[lo.tolist(),hi.tolist()],'reference_scale':scale,'reference_center':center.tolist(),'front_triangles':len(t),'wall_triangles':len(wallf),'total_triangles':len(faces)+len(wallf),'bounds_min':np.vstack([front,walls]).min(0).tolist(),'bounds_max':np.vstack([front,walls]).max(0).tolist(),'preview_size':1,'preview_lift':0,'method':'Reference contours, curved sculpted relief, continuous edge walls, matching sculpted rear'}
(C/'trace.json').write_text(json.dumps(trace,indent=2)+'\n');print(json.dumps(trace,indent=2))
from prepare_sides import prepare
prepare(R,C)
