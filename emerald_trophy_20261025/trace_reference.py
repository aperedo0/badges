"""Reconstruct the reference silhouettes and sculpted relief as an editable mesh."""
from pathlib import Path
import json,shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,distance_transform_edt,binary_closing,binary_fill_holes,label,map_coordinates
from scipy.spatial import Delaunay
R=Path(__file__).resolve().parent;OUT=R/'candidate05';OUT.mkdir(exist_ok=True)
(OUT/'textures').mkdir(exist_ok=True);(OUT/'mobile').mkdir(exist_ok=True)
TEMP=Path('/tmp/emerald_trophy_20261025');TEMP.mkdir(exist_ok=True)
im=np.asarray(Image.open(R/'reference.png').convert('RGB'),float)/255;H,W=im.shape[:2]
y,x=np.mgrid[:H,:W];S=2.42/490

def sample(a,p):
 return map_coordinates(a,[p[:,1],p[:,0]],order=1,mode='nearest')
def bez(c,n=30):
 t=np.linspace(0,1,n)[:,None];c=np.asarray(c,float)
 return (1-t)**3*c[0]+3*(1-t)**2*t*c[1]+3*(1-t)*t*t*c[2]+t**3*c[3]
def path(cs):return np.vstack([bez(c)[:-1] for c in cs]+[np.asarray(cs[-1][-1:])])
def polygon(p):
 a=Image.new('L',(W,H));ImageDraw.Draw(a).polygon([tuple(q) for q in p],fill=255);return np.asarray(a)>0
# Gold segmentation preserves every original leaf tip, stalk, berry, flame and carved contour.
gold=((im[...,0]>im[...,1]*.985)&(im[...,1]>im[...,2]*1.10)&(im[...,0]>.075))|((im[...,0]>.40)&(im[...,1]>.35)&(im[...,0]>im[...,1]*.94))
gold &= (x-627)**2+(y-590)**2<484**2
gold=binary_closing(gold,iterations=1)
components,n=label(gold);size=np.bincount(components.ravel());gold &= size[components]>=7
# The broad ribbon and its loose returns are traced separately, including the open rolled gap.
front=path([[[566,801],[510,798],[470,765],[429,777]],[[429,777],[393,782],[359,796],[366,818]],
 [[366,818],[375,850],[384,882],[394,898]],[[394,898],[404,915],[431,900],[442,905]],
 [[442,905],[459,896],[429,886],[403,889]],[[403,889],[400,875],[415,863],[440,859]],
 [[440,859],[473,850],[509,864],[555,872]],[[555,872],[563,854],[564,824],[566,801]]])
tail=path([[[371,846],[346,869],[309,891],[286,898]],[[286,898],[306,911],[328,918],[337,921]],
 [[337,921],[330,941],[328,958],[341,970]],[[341,970],[357,947],[406,948],[443,927]],
 [[443,927],[452,916],[449,903],[433,894]],[[433,894],[415,885],[391,864],[371,846]]])
ribbon=np.zeros_like(gold)
for p in [front,tail]:
 ribbon |= polygon(p);ribbon |= polygon(p*[-1,1]+[1254,0])
# The center of the banner passes behind the gold pedestal, as it does in the image.
mask=gold|ribbon
# Fill tiny dark inclusions in metal without filling the deliberate space inside a handle.
closed=binary_fill_holes(mask);holes=closed&~mask;hl,hn=label(holes);hs=np.bincount(hl.ravel());mask |= holes&(hs[hl]<100)
# All gemstone surfaces are built as explicit flat facets, independent of the metal relief.
gem_specs=[('Top emerald',627,206,43,65),('Pedestal emerald',627,907,24,34)]
gem_mask=np.zeros_like(mask)
for _,cx,cy,rx,ry in gem_specs:
 gem_mask |= (abs(x-cx)/rx+abs(y-cy)/ry)<1.015
mask &= ~gem_mask
D=distance_transform_edt(mask);outside=distance_transform_edt(~mask)
sdf=gaussian_filter(D-outside,.58)
# A continuous relief with curved leaves, deeply rounded cup and actual folded ribbon surfaces.
z=.074+.080*(1-np.exp(-D/9))
flames=((x>245)&(x<388)|(x>867)&(x<1009))&(y>226)&(y<393)
z=np.where(flames,.092+.095*(1-np.exp(-D/11)),z)
# Fine reference channels are geometry, with their exact appearance retained in material maps.
lum=im@np.array([.2126,.7152,.0722]);detail=gaussian_filter(lum,1.7)-gaussian_filter(lum,8)
z += np.clip(detail,-.20,.20)*.035*(1-np.exp(-D/3))
# The cup body, stem and plinth remain a full rounded volume in relief.
left=bez([[488,408],[484,559],[526,656],[602,678]],100)
width=np.interp(y,left[:,1],627-left[:,0]);cw=np.maximum(width,1)
body=(y>=408)&(y<=678)&(abs(x-627)<=cw)
z=np.where(body,.115+.235*np.maximum(0,1-((x-627)/cw)**2)**.60+np.clip(detail,-.2,.2)*.027,z)
# Turned lip bands and stem collars follow the exact photo outlines.
collar=(y>357)&(y<416)&(x>469)&(x<785)
z=np.where(collar,.165+.17*np.sqrt(np.maximum(0,1-((x-627)/157)**2))+.012*np.cos((y-366)*.44),z)
stem=(y>=678)&(y<806)&(abs(x-627)<76)
z=np.where(stem,.115+.15*np.sqrt(np.maximum(0,1-((x-627)/np.maximum(25,65-(805-y)*.35))**2)),z)
foot=(y>=805)&(y<=1000)&(abs(x-627)<155)
z=np.where(foot,.105+.14*np.sqrt(np.maximum(0,1-((x-627)/156)**2))+.009*np.cos(y*.28),z)
# Cylindrical torch shafts and capitals have closed side contours and raised flutes.
for cx in [319,935]:
 shaft=(abs(x-cx)<19)&(y>477)&(y<724)
 z=np.where(shaft,.10+.09*np.sqrt(np.maximum(0,1-((x-cx)/19)**2))+.003*np.cos((x-cx)*1.05),z)
 capital=(abs(x-cx)<58)&(y>=389)&(y<=479)
 z=np.where(capital,.12+.10*np.sqrt(np.maximum(0,1-((x-cx)/58)**2))+.008*np.cos(y*.37),z)
# Each physical banner sheet has a different fold axis. The gold hem sits on that sheet.
for side in [0,1]:
 xx=x if not side else 1254-x
 fr=polygon(front if not side else front*[-1,1]+[1254,0])
 ta=polygon(tail if not side else tail*[-1,1]+[1254,0])
 fold=.115+.052*np.sin((xx-298)*np.pi/143+(y-850)*.012)
 z=np.where(ta&~gold,fold,z)
 roll=.23+.075*np.sin((xx-365)*np.pi/200)+.025*np.cos((y-830)*np.pi/100)
 z=np.where(fr&~foot,roll,z)
 # Place the traced gold hem onto the ribbon, never as a floating wire.
 near=(distance_transform_edt(~fr)<3)&gold&~foot
 z=np.where(near,roll+.006,z)
# The diamond settings are physically bevelled, with a low stone seat.
for _,cx,cy,rx,ry in gem_specs:
 d=abs(x-cx)/(rx/.66)+abs(y-cy)/(ry/.73)
 setting=(d<1.025)&(d>.64)
 z=np.where(setting,.215+.07*np.sin(np.clip((1-d)/.36,0,1)*np.pi),z)
z=gaussian_filter(z,.85)
# Smooth, accurately located contour samples from marching squares on the signed distance.
segments=[]
a=sdf[:-1,:-1];b=sdf[:-1,1:];c=sdf[1:,1:];d=sdf[1:,:-1]
active=((a>=0)!=(b>=0))|((b>=0)!=(c>=0))|((c>=0)!=(d>=0))|((d>=0)!=(a>=0))
for yy,xx in zip(*np.nonzero(active)):
 vals=[a[yy,xx],b[yy,xx],c[yy,xx],d[yy,xx]];corners=[(xx,yy),(xx+1,yy),(xx+1,yy+1),(xx,yy+1)];cross=[]
 for i,j in [(0,1),(1,2),(2,3),(3,0)]:
  if (vals[i]>=0)!=(vals[j]>=0):
   t=vals[i]/(vals[i]-vals[j]);cross.append(np.array(corners[i])*(1-t)+np.array(corners[j])*t)
 if len(cross)==2:segments.append(cross)
 elif len(cross)==4:segments += [[cross[0],cross[1]],[cross[2],cross[3]]]
# Thin curves keep all their samples. Broader contours are sampled about every two pixels.
boundary=np.concatenate(segments)
quant=np.round(boundary/1.9).astype(int);_,ids=np.unique(quant,axis=0,return_index=True);boundary=boundary[np.sort(ids)]
pts=[boundary]
for step,lo,hi in [(2.7,0,6),(5.,6,20),(7.,20,1000)]:
 yy,xx=np.mgrid[0:H:step,0:W:step];p=np.c_[xx.ravel(),yy.ravel()];dist=sample(D,p);inside=sample(sdf,p)>0
 pts.append(p[inside&(dist>=lo)&(dist<hi)])
p=np.vstack(pts);_,ids=np.unique(np.round(p,3),axis=0,return_index=True);p=p[np.sort(ids)]
t=Delaunay(p).simplices
# Every triangle and its edge midpoints must remain within the exact traced silhouette.
q=p[t];tests=np.stack([q.mean(1),(q[:,0]+q[:,1])/2,(q[:,1]+q[:,2])/2,(q[:,2]+q[:,0])/2],1)
valid=(sample(sdf,tests.reshape(-1,2)).reshape(-1,4)>-.43).all(1);t=t[valid]
used=np.unique(t);reindex=np.full(len(p),-1);reindex[used]=np.arange(len(used));p=p[used];t=reindex[t]
# Orient the front toward +Z after converting reference Y to model Y.
aa=p[t[:,1]]-p[t[:,0]];bb=p[t[:,2]]-p[t[:,0]];area=aa[:,0]*bb[:,1]-aa[:,1]*bb[:,0];t[area>0]=t[area>0,::-1]
v=np.c_[(p[:,0]-627)*S,(590-p[:,1])*S,sample(z,p)]
# Freeze the original source coordinates for texture sampling and front calibration.
front_vertex_count=len(v);front_faces=len(t)
# Boundary walls extend to the field. Their separate plain metal avoids texture streaks on a side view.
edges=np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);sorted_edges=np.sort(edges,axis=1)
_,ii,counts=np.unique(sorted_edges,axis=0,return_index=True,return_counts=True);be=edges[ii[counts==1]]
wallp=[];wallt=[]
for i,(aa,bb) in enumerate(be):
 a,b=v[aa],v[bb];wallp += [a,b,[*b[:2],.062],[*a[:2],.062]];wallt += [(i*4,i*4+1,i*4+2),(i*4,i*4+2,i*4+3)]
arrays={'relief_points':v,'relief_triangles':t,'wall_points':np.array(wallp),'wall_triangles':np.array(wallt,np.int32),
 'reference_points':p,'height':z,'mask':mask,'sdf':sdf,'gold':gold,'ribbon':ribbon,'gem_mask':gem_mask}
# Twenty explicit gemstone facets align with the primary cuts in the reference.
for index,(_,cx,cy,rx,ry) in enumerate(gem_specs):
 outer=np.array([[cx,cy-ry],[cx+rx,cy],[cx,cy+ry],[cx-rx,cy]],float)
 middle=np.array([[cx,cy-ry*.58],[cx+rx*.55,cy],[cx,cy+ry*.58],[cx-rx*.55,cy]])
 # Alternate broad triangular shoulders and central table planes, preserving a clean diamond cut.
 gp=np.vstack([outer,middle,[[cx,cy]]]);gz=np.array([.255]*4+[.325]*4+[.342])
 gf=[]
 for i in range(4):
  j=(i+1)%4;gf += [(i,j,4+i),(j,4+j,4+i),(4+i,4+j,8)]
 gv=np.c_[(gp[:,0]-627)*S,(590-gp[:,1])*S,gz]
 arrays['gem'+str(index)+'_points']=gv;arrays['gem'+str(index)+'_triangles']=np.array(gf)[:,::-1]
np.savez_compressed(TEMP/'reference_relief.npz',**arrays)
# A numeric target in the same UV atlas as the full coin. Only relief samples use it.
N=1024;ty,tx=np.mgrid[:N,:N]
rx=627+((tx+.5)/N-.5)*6.03/S;ry=590-((1-(ty+.5)/N)-.5)*6.03/S
samplep=np.c_[rx.ravel(),ry.ravel()]
target=np.stack([sample(im[...,k],samplep) for k in range(3)],-1).reshape(N,N,3)
Image.fromarray(np.uint8(np.clip(target*255+.5,0,255))).save(OUT/'target_reference.png')
for suffix in ['color','roughness']:
 shutil.copyfile(R.parent/'emerald_archer_20261023/candidate02/textures'/('field_'+suffix+'.png'),OUT/'textures'/('field_'+suffix+'.png'))
Image.fromarray(np.full((N,N,3),188,np.uint8)).save(OUT/'textures/relief_color.png')
Image.fromarray(np.zeros((N,N,3),np.uint8)).save(OUT/'textures/relief_emission.png')
# Save a mask overlay for internal tracing review, without modifying the owner's image.
debug=np.uint8(im*255);debug[~(mask|gem_mask)]=debug[~(mask|gem_mask)]//4
Image.fromarray(debug).save(OUT/'traced_shapes.png')
meta={'reference_inner_radius':490,'reference_center':[627,590],'reference_to_world_scale':S,
 'front_surface_vertices':front_vertex_count,'front_surface_triangles':front_faces,'wall_triangles':len(wallt),
 'method':'Reference contours with true curved relief, folded sheet depth, explicit gem facets, calibrated material maps'}
(OUT/'trace.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta,indent=2))
