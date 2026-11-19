"""Measured shield jewel, gold setting and front foliage on the saved crown."""
from pathlib import Path
import json,shutil
import numpy as np
from scipy.optimize import root
from reference_projection import CrownReference
from sculpted_gold import frame,leaf,central_leaves,top_leaves
from ocean_reference import radial
R=Path(__file__).resolve().parent;B=R/'amethyst_crown/candidate21';C=R/'amethyst_crown/candidate22'
assert not (C/'geometry.npz').exists()
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
D=np.load(B/'geometry.npz');G=json.loads((B/'groups.json').read_text());S=json.loads((B/'materials.json').read_text());P=CrownReference(D,G,768,900,895)
gem_ids=[i for i,g in enumerate(G) if g['name']=='Large central amethyst jewel independent gemstone'];front=max(gem_ids,key=lambda i:D[f'{i}_points'][:,2].mean());back=next(i for i in gem_ids if i!=front);old=D[f'{front}_points'].astype(float);cy=(old[:,1].min()+old[:,1].max())/2
def trial(v):
 p=old.copy();p[:,0]*=v[0];p[:,1]=cy+(p[:,1]-cy)*v[1]+v[2];return p
def residual(v):
 xy=P.pixel(trial(v));return [np.ptp(xy[:,0])-95,xy[:,1].min()-468,xy[:,1].max()-674]
solution=root(residual,[.94,.84,.08]);assert solution.success;newgem=trial(solution.x)
mirror=np.linalg.lstsq(np.c_[old,np.ones(len(old))],D[f'{back}_points'],rcond=None)[0];assert np.max(abs(np.c_[old,np.ones(len(old))]@mirror-D[f'{back}_points']))<1e-5
plane=np.linalg.lstsq(np.c_[newgem[:6,:2],np.ones(6)],newgem[:6,2],rcond=None)[0]
parts=[];removed=[]
for i,g in enumerate(G):
 name=g['name']
 if name.startswith('Large central amethyst jewel') and i not in gem_ids:removed.append(name);continue
 p=D[f'{i}_points'].copy();t=D[f'{i}_triangles'].copy()
 if i==front:p=newgem
 if i==back:p=np.c_[newgem,np.ones(len(newgem))]@mirror
 parts.append((dict(g),p,t))
def append(name,p,t,face):
 if face<0:p=np.c_[p,np.ones(len(p))]@mirror
 if np.einsum('ij,ij->i',p[t[:,0]],np.cross(p[t[:,1]],p[t[:,2]])).sum()<0:t=t[:,::-1]
 parts.append((dict(name=name,mat='gold',smooth=True),p.astype(np.float32),t))
outer=np.array([[768,390],[800,437],[856,491],[851,572],[815,641],[768,710],[721,641],[685,572],[680,491],[735,437]],float)
inner=np.array([[768,468],[816,506],[812,581],[768,674],[722,581],[721,506]],float)
outer=radial(outer,[768,550],N=96);inner=radial(inner,[768,550],N=96)
for face in [1,-1]:
 p,t=frame(outer,inner,.125);append(f'Amethyst measured continuous shield jewel setting {face}',P.plane_surface(p,plane),t,face)
 for side in [-1,1]:
  for j,(aa,bb,height,layer) in enumerate(central_leaves()):
   aa=np.array(aa,float);bb=np.array(bb,float);mid=(aa+bb)/2
   # The reference has broad continuous petals, with a second small returning
   # leaf. Keep the photographed root and tip positions while widening the face.
   p,t=leaf(mid+(aa-mid)*1.25,mid+(bb-mid)*1.25,height,layer,N=40,M=12,camber=.42)
   if side>0:p[:,0]=1536-p[:,0];t=t[:,::-1]
   if j>=2:p[:,2]-=.07
   append(f'Amethyst measured separately sculpted central leaf {face} {side} {j}',P.plane_surface(p,plane),t,face)
out={};groups=[]
for i,(g,p,t) in enumerate(parts):out[f'{i}_points']=p.astype(np.float32);out[f'{i}_triangles']=t;groups.append(g)
allp=np.vstack([p for _,p,_ in parts]);assert allp[:,1].min()>=-2.45501 and allp[:,1].max()<=3.01501 and abs(allp[:,0]).max()<=3.35
np.savez_compressed(C/'geometry.npz',**out);(C/'groups.json').write_text(json.dumps(groups,indent=2));(C/'materials.json').write_text(json.dumps(S,indent=2))
for p in (B/'textures').glob('*.png'):shutil.copy2(p,C/'textures'/p.name)
fit=B/'review/cloth_fit_diagnostic/proposed_cloth_appearance_fit.png';assert fit.is_file();shutil.copy2(fit,C/'textures/velvet_fold_color.png')
(C/'cloth_appearance_fit.json').write_text(json.dumps(dict(source='candidate21',cloth_reference_appearance_fit=True,physical_albedo_not_proven=True,reference_illumination_not_removed_exactly=True,no_emission_used=True,gemstones_and_metal_excluded=True,actual_native_motion_review_required=True,unaccepted_trial=True),indent=2))
(C/'reference_setting.json').write_text(json.dumps(dict(source='candidate21',measured_actual_reference=True,old_generic_parts_removed=removed,gem_y_scale=float(solution.x[1]),gem_x_scale=float(solution.x[0]),gem_y_shift=float(solution.x[2]),front_jewel_reference_bounds=[468,674],arch_and_hub_geometry_unchanged=True),indent=2));print('Amethyst22 measured main setting prepared',len(groups),'parts',flush=True)
