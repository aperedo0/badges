"""Apply fitted sculpted leaf boundaries while retaining real closed bodies."""
from pathlib import Path
import json,shutil
import numpy as np
from reference_projection import CrownReference
from sculpted_gold import leaf
R=Path(__file__).resolve().parent;B=R/'emerald_crown/candidate14';C=R/'emerald_crown/candidate15'
assert not (C/'geometry.npz').exists()
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
D=np.load(B/'geometry.npz');G=json.loads((B/'groups.json').read_text());S=json.loads((B/'materials.json').read_text());P=CrownReference(D,G,724,964,914)
ids=[i for i,g in enumerate(G) if g['name']=='Large central emerald jewel independent gemstone'];front=max(ids,key=lambda i:D[f'{i}_points'][:,2].mean());back=next(i for i in ids if i!=front);a=D[f'{front}_points'];mirror=np.linalg.lstsq(np.c_[a,np.ones(len(a))],D[f'{back}_points'],rcond=None)[0]
parts=[]
for i,g in enumerate(G):
 if g['name'].startswith('Emerald layered returning acanthus leaf'):continue
 parts.append((dict(g),D[f'{i}_points'].copy(),D[f'{i}_triangles'].copy()))
fitted=json.loads((B/'review/outline_fit/fitted_controls.json').read_text())
for face in [1,-1]:
 for side in [-1,1]:
  for j,item in enumerate(fitted):
   p,t=leaf(item['a'],item['b'],item['height'],item['layer'],N=56,M=16,camber=.55)
   if side>0:p[:,0]=1448-p[:,0];t=t[:,::-1]
   p=P.surface(p,radius=2.75)
   if face<0:p=np.c_[p,np.ones(len(p))]@mirror
   if np.einsum('ij,ij->i',p[t[:,0]],np.cross(p[t[:,1]],p[t[:,2]])).sum()<0:t=t[:,::-1]
   parts.append((dict(name=f'Emerald reference fitted closed curled leaf {face} {side} {j}',mat='gold',smooth=True),p.astype(np.float32),t))
out={};groups=[]
for i,(g,p,t) in enumerate(parts):out[f'{i}_points']=p.astype(np.float32);out[f'{i}_triangles']=t;groups.append(g)
np.savez_compressed(C/'geometry.npz',**out);(C/'groups.json').write_text(json.dumps(groups,indent=2));(C/'materials.json').write_text(json.dumps(S,indent=2))
for p in (B/'textures').glob('*.png'):shutil.copy2(p,C/'textures'/p.name)
shutil.copy2(B/'review/outline_fit/fitted_controls.json',C/'fitted_leaf_controls.json')
(C/'foliage_review.json').write_text(json.dumps(dict(source='candidate14',closed_separately_sculpted_leaves=28,actual_reference_silhouette_fit=True,no_appearance_photo_as_gold_material=True,casting_not_reintroduced=True,native_review_pending=True,cloth_ao_needs_refresh=True),indent=2));print('Emerald15 fitted closed leaves prepared',len(groups),'parts')
