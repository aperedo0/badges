"""Measured laurel attachments and a closed rounded acanthus casting."""
from pathlib import Path
import json,shutil,sys
import numpy as np
from PIL import Image
from scipy.ndimage import binary_closing,binary_fill_holes,label,gaussian_filter,distance_transform_edt,map_coordinates
from reference_projection import CrownReference
from reference_gold_relief import gold_pixels,relief,polygon
from sculpted_gold import leaf
import build_geometry as shape
R=Path(__file__).resolve().parent;B=R/'emerald_crown/candidate12';C=R/'emerald_crown/candidate13'
assert not (C/'geometry.npz').exists() or ('--update-prepared' in sys.argv and not (C/'source/emerald_crown.blend').exists())
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
D=np.load(B/'geometry.npz');G=json.loads((B/'groups.json').read_text());S=json.loads((B/'materials.json').read_text());P=CrownReference(D,G,724,964,914)
ids=[i for i,g in enumerate(G) if g['name']=='Large central emerald jewel independent gemstone'];front=max(ids,key=lambda i:D[f'{i}_points'][:,2].mean());back=next(i for i in ids if i!=front);a=D[f'{front}_points'];mirror=np.linalg.lstsq(np.c_[a,np.ones(len(a))],D[f'{back}_points'],rcond=None)[0]
parts=[]
for i,g in enumerate(G):
 if g['name'].startswith(('Emerald measured laurel','Emerald measured closed acanthus')):continue
 parts.append((dict(g),D[f'{i}_points'].copy(),D[f'{i}_triangles'].copy()))
def append(name,p,t,face,mat='gold',smooth=True):
 if face<0:p=np.c_[p,np.ones(len(p))]@mirror
 if np.einsum('ij,ij->i',p[t[:,0]],np.cross(p[t[:,1]],p[t[:,2]])).sum()<0:t=t[:,::-1]
 parts.append((dict(name=name,mat=mat,smooth=smooth),p.astype(np.float32),t))
image=np.asarray(Image.open(R/'emerald_crown/reference.png').convert('RGB'),float)/255
envelope=[[240,650],[260,640],[283,623],[305,610],[343,620],[356,630],[381,625],[421,630],[431,655],[411,693],[480,727],[560,760],[565,790],[444,790],[375,780],[318,791],[276,781],[245,756]]
mask=gold_pixels(image)&polygon(image.shape[:2],envelope);mask=binary_closing(mask,iterations=2);holes=binary_fill_holes(mask)&~mask;lab,_=label(holes);sizes=np.bincount(lab.ravel());mask|=holes&(sizes[lab]<90)
box=(235,606,568,795);crop=mask[box[1]:box[3],box[0]:box[2]];Image.fromarray(np.uint8(crop)*255).save(C/'review/acanthus_geometry_mask.png');cast,tcast=relief(crop,box,step=2);K=len(cast)//2;dist=gaussian_filter(distance_transform_edt(crop),1.5);d=map_coordinates(dist,[cast[:K,1]-box[1],cast[:K,0]-box[0]],order=1);cast[:K,2]=.03+.18*(1-np.exp(-d/10));cast[K:,2]=-.075
from scipy.spatial import cKDTree
for controls,height,width in [([[350,778],[312,745],[330,665],[302,635]],.065,9),([[350,778],[382,727],[374,653],[408,653]],.065,9),([[554,778],[467,795],[432,744],[452,735]],.055,8),([[315,774],[263,773],[260,730],[251,707]],.045,7)]:
 curve=shape.bez(controls,160);distance=cKDTree(curve).query(cast[:K,:2])[0];cast[:K,2]+=height*np.exp(-.5*(distance/width)**2)*np.minimum(d/4,1)
# These attachment points follow the actual fan. Earlier trial roots were
# too far right, which made the leaves look like horizontal bars.
leaves=[((576,592),(635,516),25),((563,635),(554,550),25),((552,677),(510,590),27),((595,728),(485,655),28),((646,750),(510,737),25),((676,785),(583,777),18),((565,634),(612,601),18),((594,729),(589,634),24),((646,750),(607,667),25)]
for face in [1,-1]:
 for side in [-1,1]:
  p=cast.copy();t=tcast.copy()
  if side>0:p[:,0]=1448-p[:,0];t=t[:,::-1]
  append(f'Emerald rounded acanthus casting with open curls {face} {side}',P.surface(p,radius=2.75),t,face)
  stem=shape.bez([[709,805],[652,754],[540,672],[635,516]],72);shape.PARTS=[];shape.tube('Measured connected laurel stem',P.surface(np.c_[stem,np.full(len(stem),.045)],radius=2.75),.014,sides=8)
  for part in shape.PARTS:
   p=part['p'].copy()
   if side>0:p[:,0]=-p[:,0]
   append(f'Emerald corrected laurel stem {face} {side}',p,part['t'],face)
  for j,(base,tip,width) in enumerate(leaves):
   base=np.array(base,float);tip=np.array(tip,float);delta=tip-base;normal=np.array([-delta[1],delta[0]]);normal/=np.linalg.norm(normal)
   aa=[base,base+.25*delta+normal*width,base+.74*delta+normal*width*.60,tip];bb=[base,base+.30*delta-normal*width,base+.78*delta-normal*width*.56,tip]
   p,t=leaf(aa,bb,.12,.045,N=32,M=12,camber=.42)
   if side>0:p[:,0]=1448-p[:,0];t=t[:,::-1]
   append(f'Emerald corrected measured laurel leaf {face} {side} {j}',P.surface(p,radius=2.75),t,face)
  xy=np.array([[374 if side<0 else 1074,759,.14]]);center=P.surface(xy,radius=2.75)[0];normal=shape.norm([center[0],.05,center[2]]);shape.PARTS=[]
  shape.gem('Acanthus oval independent emerald',center,.060,.087,.11,'CrestGem_Emerald',normal)
  for part in shape.PARTS:append(f'Emerald acanthus oval jewel {face} {side}',part['p'],part['t'],face,part['mat'],part['smooth'])
out={};groups=[]
for i,(g,p,t) in enumerate(parts):out[f'{i}_points']=p.astype(np.float32);out[f'{i}_triangles']=t;groups.append(g)
points=np.vstack([p for _,p,_ in parts]);assert points[:,1].min()>=-2.45501 and points[:,1].max()<=3.01501 and abs(points[:,0]).max()<=3.35
np.savez_compressed(C/'geometry.npz',**out);(C/'groups.json').write_text(json.dumps(groups,indent=2));(C/'materials.json').write_text(json.dumps(S,indent=2))
for p in (B/'textures').glob('*.png'):shutil.copy2(p,C/'textures'/p.name)
(C/'foliage_review.json').write_text(json.dumps(dict(source='candidate12',previous_leaf_attachments_corrected=True,measured_laurel_leaves=36,closed_rounded_castings=4,open_curls_retained=True,appearance_image_not_used_as_material=True,arch_and_hub_unchanged=True,cloth_ao_needs_refresh=True,native_review_pending=True),indent=2));print('Emerald13 reference sculpture prepared',len(groups),'parts',flush=True)
