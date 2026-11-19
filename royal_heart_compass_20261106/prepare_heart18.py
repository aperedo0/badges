"""Join the broad bezel and a measured upper crown facet correction."""
from pathlib import Path
import json,shutil
import numpy as np
from scipy.spatial import ConvexHull
R=Path(__file__).resolve().parent;B=R/'ruby_heart/candidate17';C=R/'ruby_heart/candidate18'
assert not (C/'geometry.npz').exists()
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
D=np.load(B/'geometry.npz');cut=np.load(R/'optics_fit/heart_crown_bias_0.15.npz');G=json.loads((B/'groups.json').read_text());out={};reports=[];gem=0
for i,g in enumerate(G):
 p=D[f'{i}_points'].copy();t=D[f'{i}_triangles'].copy()
 if g['mat']=='CrestGem_Rose':
  p=cut[f'{gem}_points'].copy();h=ConvexHull(p);t=h.simplices.copy();n=np.cross(p[t[:,1]]-p[t[:,0]],p[t[:,2]]-p[t[:,0]]);flip=(n*h.equations[:,:3]).sum(1)<0;t[flip]=t[flip,::-1];planes=len(np.unique(np.round(h.equations,3),axis=0));assert planes<=256;reports.append(dict(name=g['name'],approximate_planes=planes,upper_crown_bias=.15,key_facet_gradient=[.35,-.35]));gem+=1
 out[f'{i}_points']=p.astype(np.float32);out[f'{i}_triangles']=t
assert gem==2
np.savez_compressed(C/'geometry.npz',**out);(C/'groups.json').write_text(json.dumps(G,indent=2));shutil.copy2(B/'materials.json',C/'materials.json')
for p in (B/'textures').glob('*.png'):shutil.copy2(p,C/'textures'/p.name)
(C/'physical_cut_review.json').write_text(json.dumps(dict(source_bezel='candidate17',source_cut='candidate16',geometry_only=True,actual_studio_key_measured=True,appearance_maps_on_gem=False,exposure_and_optical_shader_unchanged=True,domains=reports,native_review_pending=True),indent=2));print('Heart18 actual physical cut and broad gold bezel prepared',flush=True)
