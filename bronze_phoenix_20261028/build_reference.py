"""Trace reference silhouettes and sculpt closed, textured relief for Blender."""
from pathlib import Path
import sys,json,shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,distance_transform_edt,binary_closing,binary_fill_holes,label,map_coordinates
from scipy.spatial import Delaunay

ROOT=Path(__file__).resolve().parent
key=sys.argv[1];R=ROOT/key;C=R/((R/'candidate.txt').read_text().strip() if (R/'candidate.txt').exists() else 'candidate01');C.mkdir(parents=True,exist_ok=True)
(C/'textures').mkdir(exist_ok=True);(C/'mobile').mkdir(exist_ok=True)
cfg=json.loads((R/'design.json').read_text())
im=np.asarray(Image.open(R/'reference.png').convert('RGB'),float)/255
H,W=im.shape[:2];y,x=np.mgrid[:H,:W]
lum=im@np.array([.2126,.7152,.0722])
def sample(a,p):return map_coordinates(a,[p[:,1],p[:,0]],order=1,mode='nearest')
def poly(points):
 a=Image.new('L',(W,H));ImageDraw.Draw(a).polygon([tuple(p) for p in points],fill=255);return np.asarray(a)>0
def bezier_path(curves):
 parts=[]
 for curve in curves:
  a,b,c,d=np.array(curve,float);f=np.linspace(0,1,100)[:,None]
  parts.extend((1-f)**3*a+3*(1-f)**2*f*b+3*(1-f)*f*f*c+f**3*d)
 return parts
mask=(im.max(-1)>.08)&((im.max(-1)-im.min(-1)>.028)|(lum>.125))
if key=='crescent_ocean':
 mask=((im[...,2]>im[...,0]*1.12)&(im[...,2]>.033))|(lum>.18)|((lum>.10)&(im[...,2]>=im[...,0]*.95))
 # Remove the source image's faint blue halo above the thin upper crescent.
 strong=(im[...,2]>.30)&(im[...,2]>im[...,0]*1.45)&(y>105)&(y<440)
 for xx in range(370,840):
  rows=np.flatnonzero(strong[:,xx])
  if len(rows):
   edge=rows[0];mask[:max(0,edge-1),xx] &= ~((im[:max(0,edge-1),xx,2]>im[:max(0,edge-1),xx,0]*1.12)&(lum[:max(0,edge-1),xx]<.30))
if key=='mountain_crest':
 gold=(im[...,0]>im[...,2]*1.35)&(im[...,1]>im[...,2]*1.12)
 mask=(gold&(im[...,0]>.34))|(lum>.24)
 radius=np.sqrt((x-650)**2+(y-551)**2)
 mask |= (radius<482)&(radius>400)&(y<710)
 mask |= gold&(im[...,0]>.10)&(im[...,0]>im[...,2]*1.8)&(im[...,1]>im[...,2]*1.4)&(y>650)
if key=='winged_sword':
 mask=(lum>.18)|((im[...,2]>im[...,0]*1.025)&(im[...,2]>.105))
if key=='phoenix':
 bronze=((im[...,0]>im[...,1]*1.23)&(im[...,0]>im[...,2]*1.75)&(im[...,0]>.21))|(lum>.25)
 mask=bronze|(((x-655)/485)**2+((y-563)/485)**2<1)
 for feature in cfg['facets']:mask |= poly(feature['outline'])
mask=binary_closing(mask,iterations=cfg.get('close_iterations',1))
for p in cfg.get('include',[]):mask |= poly(p)
for p in cfg.get('exclude',[]):mask &= ~poly(p)
if key=='crescent_ocean':
 # The starry interior is an actual recessed navy surface, not the image background.
 field=((x-891)/253)**2+((y-479)/254)**2<1
 field &= x>632
 mask |= field
components,n=label(mask);sizes=np.bincount(components.ravel());mask &= sizes[components]>=cfg.get('min_component',12)
holes=binary_fill_holes(mask)&~mask;hl,_=label(holes);hs=np.bincount(hl.ravel());mask |= holes&(hs[hl]<cfg.get('fill_holes',260))
dist=distance_transform_edt(mask);sdf=gaussian_filter(dist-distance_transform_edt(~mask),.55)
z=.115+.105*(1-np.exp(-dist/17))
detail=gaussian_filter(lum,1.7)-gaussian_filter(lum,9)
z += np.clip(detail,-.3,.3)*.075*(1-np.exp(-dist/3))
if key=='crescent_ocean':
 blue=(im[...,2]>im[...,0]*1.13)&(im[...,2]>im[...,1]*1.03)
 z=np.where(blue,z-.035,z+.035)
 z=np.where(field,.075,z)
 # Overlapping silver arcs rise well above their recessed celestial field.
 outer_silver=poly(bezier_path([
  [[610,70],[300,96],[131,310],[158,501]],
  [[158,501],[172,743],[401,917],[666,959]],
  [[666,959],[986,1018],[1177,800],[1154,500]],
  [[1154,500],[1154,784],[886,918],[657,834]],
  [[657,834],[435,760],[326,585],[327,431]],
  [[327,431],[316,253],[454,108],[610,70]]]))
 inner_silver=poly(bezier_path([
  [[1000,235],[779,66],[526,192],[446,382]],
  [[446,382],[359,591],[482,775],[691,797]],
  [[691,797],[867,826],[1049,714],[1083,591]],
  [[1083,591],[1017,726],[833,765],[713,672]],
  [[713,672],[566,551],[621,336],[758,259]],
  [[758,259],[835,214],[918,209],[1000,235]]]))
 for region,base,rise in [(outer_silver,.13,.16),(inner_silver,.13,.18)]:
  distance=distance_transform_edt(region)
  z=np.where(region,base+rise*(1-np.exp(-distance/24)),z)
 # Breaking waves have a deeper convex body and curled crests.
 waves=y>640
 z=np.where(waves,.14+.18*(1-np.exp(-dist/21))+.065*gaussian_filter(lum,5),z)
 for cx,cy,rx,ry in [(274,734,113,100),(508,861,103,80),(656,1030,128,103),(963,965,71,64)]:
  rr=((x-cx)/rx)**2+((y-cy)/ry)**2
  z+=np.maximum(0,1-rr)*.065*waves
 # The compass star has real eight primary planes and a raised central ridge.
 star=poly([[894,290],[933,438],[1047,477],[933,516],[894,665],[854,516],[738,477],[854,438]])
 outer=np.array([[894,290],[933,438],[1047,477],[933,516],[894,665],[854,516],[738,477],[854,438]],float)
 for a,b in zip(outer,np.roll(outer,-1,axis=0)):
  a0=np.array([894,477.]);aa=a-a0;bb=b-a0;det=np.linalg.det(np.stack([aa,bb]))
  u=((x-a0[0])*bb[1]-(y-a0[1])*bb[0])/det
  v=(aa[0]*(y-a0[1])-aa[1]*(x-a0[0]))/det
  inside=(u>=0)&(v>=0)&(u+v<=1)
  z=np.where(inside,.46*(1-u-v)+.20*(u+v),z)
elif key=='mountain_crest':
 # Snow ridges and rock faces retain large angular planes with distinct depth.
 radius=np.sqrt((x-650)**2+(y-551)**2)
 gold=((radius>400)&(radius<485))|((y>650)&(abs(x-650)>520-(y-650)*1.15))
 for feature in cfg.get('facets',[]):gold |= poly(feature['outline'])
 gold |= poly([[651,699],[817,880],[650,1106],[486,881]])
 z=np.where(gold,.16+.14*(1-np.exp(-dist/17)),z)
 peaks=cfg['peaks']
 rock=np.zeros_like(z)
 for cx,cy,base,width,height in peaks:
  v=np.clip((y-cy)/max(base-cy,1),0,1);half=width*np.maximum(v,.01)
  rise=height*np.maximum(0,1-abs(x-cx)/np.maximum(half,1))*(1-.25*v)
  active=(y>=cy)&(y<=base)&(abs(x-cx)<=half)
  rock=np.maximum(rock,np.where(active,rise,0))
 z=np.where(~gold,.13+rock,z)
 z+=np.clip(gaussian_filter(lum,3)-gaussian_filter(lum,15),-.3,.3)*.12
elif key=='phoenix':
 radius=np.sqrt((x-655)**2+(y-563)**2)
 bronze=(im[...,0]>im[...,1]*1.23)&(im[...,0]>im[...,2]*1.75)&(im[...,0]>.14)
 z=np.full((H,W),.075)
 ring=(radius>425)&(radius<495)
 z=np.where(ring,.14+.12*np.sin(np.clip((radius-425)/70,0,1)*np.pi)**.65,z)
 # Swept feather vanes, separated by real depth while their reference
 # contours and fine bronze marks remain in the finish maps.
 feathers=[
 [[350,65],[244,143],[207,257],[221,364],[295,438],[416,493],[457,546],[500,503],[465,444],[360,387],[298,313],[296,201]],
 [[178,234],[137,321],[149,415],[203,474],[320,521],[418,544],[430,500],[309,449],[226,369],[191,302]],
 [[95,380],[96,472],[139,545],[228,583],[331,594],[421,577],[373,546],[259,534],[170,480]],
 [[90,555],[123,636],[213,692],[303,700],[422,638],[451,607],[360,629],[261,635],[161,603]],
 [[152,714],[218,776],[303,793],[376,768],[457,693],[464,667],[355,718],[260,744]],
 [[270,838],[354,864],[421,832],[488,731],[481,705],[390,792]],
 [[378,916],[443,884],[489,830],[518,760],[507,726],[455,812]],
 [[479,912],[517,943],[555,1001],[580,912],[600,813],[571,748],[546,834]]]
 for index,outline in enumerate(feathers):
  for side in [1,-1]:
   polygon=np.array(outline,float);polygon[:,0]=655+(polygon[:,0]-655)*side
   region=poly(polygon);dd=distance_transform_edt(region)
   z=np.where(region,.20+.012*index+.11*(1-np.exp(-dd/24)),z)
 # The raised inward return is a single continuous sculpted curve.
 frame=bezier_path([
  [[350,65],[261,159],[251,292],[337,361]],
  [[337,361],[393,403],[466,426],[512,463]],
  [[512,463],[464,479],[462,531],[499,559]],
  [[499,559],[524,584],[546,582],[559,577]],
  [[559,577],[559,611],[545,638],[526,652]],
  [[526,652],[453,640],[412,600],[408,545]],
  [[408,545],[401,503],[423,478],[407,460]],
  [[407,460],[336,415],[244,373],[219,296]],
  [[219,296],[183,199],[264,115],[350,65]]])
 for side in [1,-1]:
  polygon=np.array(frame,float);polygon[:,0]=655+(polygon[:,0]-655)*side;region=poly(polygon);dd=distance_transform_edt(region)
  z=np.where(region,.35+.11*(1-np.exp(-dd/22)),z)
 body=poly(bezier_path([
  [[724,251],[719,290],[650,288],[575,326]],
  [[575,326],[529,332],[519,353],[529,387]],
  [[529,387],[549,357],[575,363],[592,374]],
  [[592,374],[663,429],[620,499],[557,549]],
  [[557,549],[536,576],[526,600],[520,617]],
  [[520,617],[539,698],[592,748],[655,855]],
  [[655,855],[678,759],[749,692],[789,617]],
  [[789,617],[730,554],[741,475],[710,402]],
  [[710,402],[730,406],[745,413],[751,416]],
  [[751,416],[735,362],[704,345],[680,337]],
  [[680,337],[733,327],[757,308],[771,278]],
  [[771,278],[738,302],[710,310],[673,309]],
  [[673,309],[703,294],[718,277],[724,251]]]))
 bd=distance_transform_edt(body);z=np.where(body,.40+.14*(1-np.exp(-bd/26)),z)
 # Keep the cracked stone recessed. Fine cracks change the finish rather
 # than turning the metal into a crumpled height field.
 z=np.where(~bronze&~body&~ring,.075,z)
elif key=='winged_sword':
 # Each feather arches across its own vane instead of lying on a flat card.
 z=.13+.09*(1-np.exp(-dist/18))
 feathers=[
  [[117,127],[112,288],[189,407],[352,482],[482,546],[494,493],[344,398],[212,304]],
  [[83,316],[83,469],[170,560],[341,618],[473,634],[456,573],[307,523],[178,420]],
  [[90,542],[123,650],[236,712],[382,705],[482,677],[424,644],[266,636],[159,588]],
  [[169,726],[267,816],[390,800],[502,711],[444,705],[331,755],[250,758]],
  [[265,859],[364,915],[466,858],[527,741],[469,776],[381,850]],
  [[389,941],[471,957],[529,868],[551,777],[512,810],[455,909]],
  [[473,980],[531,988],[566,896],[559,807],[538,870],[510,948]]]
 for index,outline in enumerate(feathers):
  for side in [1,-1]:
   polygon=np.array(outline,float);polygon[:,0]=626+(polygon[:,0]-626)*side;region=poly(polygon);dd=distance_transform_edt(region)
   z=np.where(region,.14+.014*index+.095*(1-np.exp(-dd/15)),z)
 # The inner swept wing frames follow the actual curved return around each opening.
 frame=bezier_path([
  [[286,294],[348,372],[464,426],[511,520]],
  [[511,520],[473,545],[466,622],[508,655]],
  [[508,655],[523,671],[540,681],[558,685]],
  [[558,685],[558,698],[558,713],[558,727]],
  [[558,727],[477,709],[424,669],[416,612]],
  [[416,612],[409,571],[442,541],[438,519]],
  [[438,519],[415,475],[320,441],[286,294]]])
 for side in [1,-1]:
  polygon=np.array(frame,float);polygon[:,0]=626+(polygon[:,0]-626)*side;region=poly(polygon);dd=distance_transform_edt(region)
  z=np.where(region,.265+.10*(1-np.exp(-dd/9)),z)
 blade=(abs(x-626)<70)&(y>420)&(y<986)
 z=np.where(blade,.25+.20*np.maximum(0,1-abs(x-626)/70),z)
 guard=poly([[626,230],[670,273],[744,289],[761,278],[803,334],[775,365],[754,345],[698,362],[677,428],[668,390],[626,422],[584,389],[574,428],[552,370],[495,343],[477,366],[447,335],[489,278],[506,289],[583,273]])
 z=np.where(guard,.28+.10*(1-np.exp(-distance_transform_edt(guard)/12)),z)
 handle=(abs(x-626)<38)&(y>139)&(y<260)
 z=np.where(handle,.17+.09*np.sqrt(np.maximum(0,1-((x-626)/38)**2))+.008*np.cos((y-140)*.26+(x-626)*.09),z)
z=gaussian_filter(z,4.5 if key in ['crescent_ocean','phoenix'] else (2.5 if key=='winged_sword' else .70))
facet_points=[]
for feature in cfg.get('facets',[]):
 center=np.array(feature['center'],float);outer=np.array(feature['outline'],float)
 for a,b in zip(outer,np.roll(outer,-1,axis=0)):
  aa=a-center;bb=b-center;det=np.linalg.det(np.stack([aa,bb]))
  u=((x-center[0])*bb[1]-(y-center[1])*bb[0])/det
  v=(aa[0]*(y-center[1])-aa[1]*(x-center[0]))/det
  inside=(u>=0)&(v>=0)&(u+v<=1)
  if key!='phoenix':z=np.where(inside,feature['crest']*(1-u-v)+feature['seat']*(u+v),z)
  for p0,p1 in [(center,a),(a,b)]:
   f=np.linspace(0,1,max(2,int(np.linalg.norm(p1-p0)/3)))[:,None];facet_points.extend(p0*(1-f)+p1*f)
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
 role=1 if key in ['mountain_crest','phoenix'] and samplecolor[0]>samplecolor[2]*1.35 and samplecolor[1]>samplecolor[2]*1.12 else 0
 if key in ['crescent_ocean','winged_sword'] and samplecolor[2]>samplecolor[0]*1.15:role=2
 wallroles.extend([role]*2)
np.savez_compressed(C/'geometry.npz',points=front,triangles=faces,uv=uv,wall_points=np.array(walls),wall_triangles=np.array(wallf),wall_roles=np.array(wallroles),reference_points=p,height=z,mask=mask,sdf=sdf)
Image.fromarray(np.uint8(mask)*255).save(C/'silhouette.png')
debug=np.uint8(im*255);debug[~mask]//=4;Image.fromarray(debug).save(C/'traced_shapes.png')
# Pad the atlas with nearby surface colors so filtering never introduces black borders.
_,nearest=distance_transform_edt(~mask,return_indices=True);padded=im.copy();padded[~mask]=im[tuple(nearest[:,~mask])]
Image.fromarray(np.uint8(padded*255+.5)).resize((1024,1024),Image.Resampling.LANCZOS).save(C/'target_reference.png')
trace={'name':cfg['name'],'reference_size':[W,H],'reference_bounds':[lo.tolist(),hi.tolist()],'reference_scale':scale,'reference_center':center.tolist(),'front_triangles':len(t),'wall_triangles':len(wallf),'total_triangles':len(faces)+len(wallf),'bounds_min':np.vstack([front,walls]).min(0).tolist(),'bounds_max':np.vstack([front,walls]).max(0).tolist(),'preview_size':1,'preview_lift':0,'method':'Reference contours, curved sculpted relief, continuous edge walls, matching sculpted rear'}
(C/'trace.json').write_text(json.dumps(trace,indent=2)+'\n');print(json.dumps(trace,indent=2))
from prepare_sides import prepare
prepare(R,C)
