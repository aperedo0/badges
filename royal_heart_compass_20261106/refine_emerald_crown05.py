"""Measured center setting, laurel and acanthus on the saved emerald crown."""
from pathlib import Path
import json,shutil
import numpy as np
from scipy.optimize import root
from reference_projection import CrownReference
from sculpted_gold import frame,leaf
import build_geometry as shape
R=Path(__file__).resolve().parent;B=R/'emerald_crown/candidate04';C=R/'emerald_crown/candidate12'
assert not (C/'geometry.npz').exists(),'Preserve an existing candidate'
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
D=np.load(B/'geometry.npz');G=json.loads((B/'groups.json').read_text());spec=json.loads((B/'materials.json').read_text())
projector=CrownReference(D,G,724,964,914)
gem_ids=[i for i,g in enumerate(G) if g['name']=='Large central emerald jewel independent gemstone'];assert len(gem_ids)==2
front=max(gem_ids,key=lambda i:D[f'{i}_points'][:,2].mean());back=next(i for i in gem_ids if i!=front)
original=D[f'{front}_points'].astype(float);cy=np.mean([original[:,1].min(),original[:,1].max()])
def trial(v):
 p=original.copy();p[:,0]*=v[0];p[:,1]=cy+(p[:,1]-cy)*v[1]+v[2];return p
def residual(v):
 p=projector.pixel(trial(v));return [np.ptp(p[:,0])-225,p[:,1].min()-478,p[:,1].max()-750]
solution=root(residual,[.95,.85,-.15]);assert solution.success,solution.message
newgem=trial(solution.x);mirror=np.linalg.lstsq(np.c_[original,np.ones(len(original))],D[f'{back}_points'],rcond=None)[0];assert np.max(abs(np.c_[original,np.ones(len(original))]@mirror-D[f'{back}_points']))<1e-5
plane=np.linalg.lstsq(np.c_[newgem[:4,:2],np.ones(4)],newgem[:4,2],rcond=None)[0]
parts=[];removed=[]
for i,g in enumerate(G):
 name=g['name']
 if name in ['Broad beveled central emerald jewel gold mount','Large central solid gold pave surround','Pave gold bead seat','Central border brilliant','Central laurel stem','Emerald laurel detailed leaf','Acanthus raised sculpted vein','Side fleur scroll'] or name.startswith('Reference flowing emerald') or name.startswith('Large central emerald jewel') and i not in gem_ids:
  removed.append(name);continue
 p=D[f'{i}_points'].copy();t=D[f'{i}_triangles'].copy();g=dict(g)
 if i==front:p=newgem.copy()
 if i==back:p=np.c_[newgem,np.ones(len(newgem))]@mirror
 if name in ['Top fleur curved petal','Top fleur lower curl']:p[:,0]*=.78
 parts.append((g,p,t))
def append(name,p,t,face,material='gold',smooth=True):
 if face<0:p=np.c_[p,np.ones(len(p))]@mirror
 if np.einsum('ij,ij->i',p[t[:,0]],np.cross(p[t[:,1]],p[t[:,2]])).sum()<0:t=t[:,::-1]
 parts.append((dict(name=name,mat=material,smooth=smooth),p.astype(np.float32),t))
def on_crown(p):
 # Preserve a round crown behind the measured face. Leaves unfold modestly
 # toward the viewer from their attached roots, rather than becoming panels.
 q=projector.surface(p,radius=2.75)
 return q
def pointed(base,tip,width,height=.12,layer=.035):
 width*=1.7
 base=np.array(base,float);tip=np.array(tip,float);d=tip-base;side=np.array([-d[1],d[0]]);side/=np.linalg.norm(side)
 a=[base,base+d*.28+side*width,base+d*.78+side*width*.55,tip]
 b=[base,base+d*.30-side*width,base+d*.80-side*width*.55,tip]
 return leaf(a,b,height,layer,N=28,M=10,camber=.40)
outer=np.array([[724,418],[884,620],[724,817],[565,620]],float)
inner=np.array([[724,478],[835,620],[724,750],[610,620]],float)
for face in [1,-1]:
 p,t=frame(outer,inner,.085);append(f'Emerald measured continuous pave setting {face}',projector.plane_surface(p,plane),t,face)
 corners=outer*.5+inner*.5
 for edge in range(4):
  for j,f in enumerate(np.linspace(.03,.97,14)):
   xy=corners[edge]*(1-f)+corners[(edge+1)%4]*f;c=projector.plane_surface(np.array([[*xy,.10]]),plane)[0];normal=shape.norm([-plane[0],-plane[1],1]);shape.PARTS=[]
   shape.sphere('Pave bead seat',c-normal*.011,.034,N=8,M=5,scale=(1,1,.45));shape.gem('Pave optical emerald',c,.028,.028,.041,'CrestGem_Emerald',normal)
   for a in shape.PARTS:append(f'Emerald fine pave {face} {edge} {j} '+a['name'],a['p'],a['t'],face,a['mat'],a['smooth'])
 # Counted and placed from the actual left laurel, repeated on the right.
 laurel=[((638,566),(635,516),17),((617,606),(553,548),18),((601,637),(518,596),18),((609,670),(501,644),18),((632,706),(522,691),20),((654,748),(500,732),19),((676,780),(569,751),15),((681,789),(589,776),12),((618,648),(607,581),14),((637,706),(633,649),16),((663,753),(654,699),15)]
 acanthus=[
  ([[557,788],[459,805],[386,772],[365,725]],[[557,788],[457,782],[397,764],[365,725]],.12,.035),
  ([[362,777],[300,758],[286,679],[297,654]],[[362,777],[318,729],[312,689],[297,654]],.16,.025),
  ([[362,777],[313,714],[323,611],[363,614]],[[362,777],[341,712],[341,649],[363,614]],.16,.045),
  ([[362,777],[336,724],[386,638],[417,656]],[[362,777],[362,715],[389,671],[417,656]],.17,.06),
  ([[363,777],[385,736],[452,710],[454,748]],[[363,777],[395,759],[436,730],[454,748]],.13,.05),
  ([[350,785],[305,799],[267,765],[280,725]],[[350,785],[305,786],[284,762],[280,725]],.13,.025),
  ([[294,776],[245,768],[235,714],[255,698]],[[294,776],[262,749],[254,720],[255,698]],.12,.035),
 ]
 for side in [-1,1]:
  stem=shape.bez([[688,795],[613,728],[565,613],[635,516]],64);shape.PARTS=[];shape.tube('Measured laurel stem',on_crown(np.c_[stem,np.full(len(stem),.035)]),.014,sides=8)
  for a in shape.PARTS:
   p=a['p'].copy()
   if side>0:p[:,0]=-p[:,0]
   append(f'Emerald measured laurel stem {face} {side}',p,a['t'],face)
  for j,(base,tip,width) in enumerate(laurel):
   p,t=pointed(base,tip,width)
   if side>0:p[:,0]=1448-p[:,0];t=t[:,::-1]
   append(f'Emerald measured laurel leaf {face} {side} {j}',on_crown(p),t,face)
  for j,(a,b,h,l) in enumerate(acanthus):
   a=np.array(a);b=np.array(b);mid=(a+b)/2
   p,t=leaf(mid+(a-mid)*1.55,mid+(b-mid)*1.55,h,l,N=32,M=12,camber=.42)
   if side>0:p[:,0]=1448-p[:,0];t=t[:,::-1]
   append(f'Emerald measured closed acanthus leaf {face} {side} {j}',on_crown(p),t,face)
out={};groups=[]
for i,(g,p,t) in enumerate(parts):out[f'{i}_points']=p.astype(np.float32);out[f'{i}_triangles']=t;groups.append(g)
allp=np.vstack([p for _,p,_ in parts]);assert allp[:,1].min()>=-2.45501 and allp[:,1].max()<=3.01501 and abs(allp[:,0]).max()<=3.35
np.savez_compressed(C/'geometry.npz',**out);(C/'groups.json').write_text(json.dumps(groups,indent=2));(C/'materials.json').write_text(json.dumps(spec,indent=2))
for p in (B/'textures').glob('*.png'):shutil.copy2(p,C/'textures'/p.name)
report=dict(source='candidate04',measured_projection=True,gem_scale_x=float(solution.x[0]),gem_scale_y=float(solution.x[1]),gem_shift_y=float(solution.x[2]),removed_generic_parts=len(removed),laurel_leaves=44,closed_acanthus_leaves=28,pave_stones=112,all_arches_and_hub_preserved=True,no_appearance_photos_in_gems_or_gold=True)
(C/'reference_geometry_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
