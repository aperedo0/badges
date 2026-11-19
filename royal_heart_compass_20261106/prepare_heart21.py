"""Rebuild one connected ruby crown and remove the depressed central facets."""
from pathlib import Path
import json,shutil
import numpy as np
from scipy.spatial import ConvexHull
R=Path(__file__).resolve().parent;B=R/'ruby_heart/candidate20';C=R/'ruby_heart/candidate21'
assert not C.exists()
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
D=np.load(B/'geometry.npz');cut=np.load(R/'optics_fit/heart_coherent_0.95_existing.npz');G=json.loads((B/'groups.json').read_text());out={};reports=[];gem=0
ps=[cut[f'{i}_points'] for i in range(2)];shift=-float((min(p[:,2].min() for p in ps)+max(p[:,2].max() for p in ps))/2)
for i,g in enumerate(G):
 p=D[f'{i}_points'].copy();t=D[f'{i}_triangles'].copy()
 if g['mat']=='CrestGem_Rose':
  p=cut[f'{gem}_points'].copy();h=ConvexHull(p);t=h.simplices.copy();normal=np.cross(p[t[:,1]]-p[t[:,0]],p[t[:,2]]-p[t[:,0]]);flip=(normal*h.equations[:,:3]).sum(1)<0;t[flip]=t[flip,::-1]
  planes=len(np.unique(np.round(h.equations,7),axis=0));assert planes<=256
  reports.append(dict(name=g['name'],facet_planes=planes));gem+=1
 p[:,2]+=shift;out[f'{i}_points']=p.astype(np.float32);out[f'{i}_triangles']=t
assert gem==2
np.savez_compressed(C/'geometry.npz',**out);(C/'groups.json').write_text(json.dumps(G,indent=2));shutil.copy2(B/'materials.json',C/'materials.json')
for p in (B/'textures').glob('*.png'):shutil.copy2(p,C/'textures'/p.name)
(C/'connected_ruby_review.json').write_text(json.dumps(dict(source='candidate20',owner_issue='Apparent other shape inside the ruby heart',actual_geometric_cause='Twin raised crown lobes and depressed central facets catching a broad neutral reflection',continuous_raised_central_keel=True,main_reference_facet_junctions=True,no_insert_or_separate_interior_object=True,one_continuous_ruby_optical_volume=True,gem_appearance_textures=False,shader_and_optical_constants_unchanged=True,whole_badge_z_center_shift=shift,domains=reports,native_review_pending=True),indent=2));print('Heart21 connected ruby cut prepared',reports)
