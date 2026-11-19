"""Keep corrected laurel attachments, replacing the rejected flat casting."""
from pathlib import Path
import json,shutil
import numpy as np
from reference_projection import CrownReference
from sculpted_gold import leaf
R=Path(__file__).resolve().parent;B=R/'emerald_crown/candidate13';C=R/'emerald_crown/candidate14'
assert not (C/'geometry.npz').exists()
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
D=np.load(B/'geometry.npz');G=json.loads((B/'groups.json').read_text());S=json.loads((B/'materials.json').read_text());P=CrownReference(D,G,724,964,914)
ids=[i for i,g in enumerate(G) if g['name']=='Large central emerald jewel independent gemstone'];front=max(ids,key=lambda i:D[f'{i}_points'][:,2].mean());back=next(i for i in ids if i!=front);a=D[f'{front}_points'];mirror=np.linalg.lstsq(np.c_[a,np.ones(len(a))],D[f'{back}_points'],rcond=None)[0]
parts=[]
for i,g in enumerate(G):
 if g['name'].startswith('Emerald rounded acanthus casting'):continue
 parts.append((dict(g),D[f'{i}_points'].copy(),D[f'{i}_triangles'].copy()))
outlines=[
 ([[352,775],[311,737],[331,656],[300,624]],[[352,775],[341,735],[350,647],[300,624]],.20,.040),
 ([[351,776],[300,742],[269,677],[288,662]],[[351,776],[327,732],[286,673],[288,662]],.18,.025),
 ([[353,775],[350,697],[364,614],[412,650]],[[353,775],[387,739],[359,664],[412,650]],.22,.050),
 ([[352,762],[346,716],[398,644],[398,677]],[[352,762],[375,716],[385,657],[398,677]],.18,.095),
 ([[553,780],[460,811],[420,729],[453,732]],[[553,780],[485,790],[438,748],[453,732]],.18,.045),
 ([[553,780],[423,798],[389,738],[343,728]],[[553,780],[437,777],[390,752],[343,728]],.14,.035),
 ([[322,778],[268,798],[237,737],[262,712]],[[322,778],[288,775],[256,745],[262,712]],.18,.025),
]
for face in [1,-1]:
 for side in [-1,1]:
  for j,(aa,bb,height,layer) in enumerate(outlines):
   aa=np.array(aa,float);bb=np.array(bb,float);mid=(aa+bb)/2;p,t=leaf(mid+(aa-mid)*1.30,mid+(bb-mid)*1.30,height,layer,N=48,M=14,camber=.60)
   if side>0:p[:,0]=1448-p[:,0];t=t[:,::-1]
   p=P.surface(p,radius=2.75)
   if face<0:p=np.c_[p,np.ones(len(p))]@mirror
   if np.einsum('ij,ij->i',p[t[:,0]],np.cross(p[t[:,1]],p[t[:,2]])).sum()<0:t=t[:,::-1]
   parts.append((dict(name=f'Emerald layered returning acanthus leaf {face} {side} {j}',mat='gold',smooth=True),p.astype(np.float32),t))
out={};groups=[]
for i,(g,p,t) in enumerate(parts):out[f'{i}_points']=p.astype(np.float32);out[f'{i}_triangles']=t;groups.append(g)
np.savez_compressed(C/'geometry.npz',**out);(C/'groups.json').write_text(json.dumps(groups,indent=2));(C/'materials.json').write_text(json.dumps(S,indent=2))
for p in (B/'textures').glob('*.png'):shutil.copy2(p,C/'textures'/p.name)
(C/'foliage_review.json').write_text(json.dumps(dict(source='candidate13',casting_rejected_before_export=True,reason='Blender inspection still showed a flat undivided gold sheet. No native export or installation of that casting.',separate_curled_leaf_bodies=28,corrected_laurel_retained=True,native_review_pending=True,cloth_ao_needs_refresh=True),indent=2));print('Emerald14 separate returned leaves prepared',len(groups),'parts')
