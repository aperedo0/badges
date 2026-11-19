"""Use the measured upper reference triangles instead of a broad flat cap."""
from pathlib import Path
import json,shutil
import numpy as np
from scipy.spatial import ConvexHull
R=Path(__file__).resolve().parent;B=R/'ruby_heart/candidate19';C=R/'ruby_heart/candidate20';assert not C.exists()
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
D=np.load(B/'geometry.npz');cut=np.load(R/'optics_fit/heart_literal_0.035.npz');G=json.loads((B/'groups.json').read_text());out={};reports=[];gem=0
for i,g in enumerate(G):
 p=D[f'{i}_points'].copy();t=D[f'{i}_triangles'].copy()
 if g['mat']=='CrestGem_Rose':
  p=cut[f'{gem}_points'];h=ConvexHull(p);t=h.simplices.copy();normal=np.cross(p[t[:,1]]-p[t[:,0]],p[t[:,2]]-p[t[:,0]]);flip=(normal*h.equations[:,:3]).sum(1)<0;t[flip]=t[flip,::-1];planes=len(np.unique(np.round(h.equations,3),axis=0));assert planes<=256;reports.append(dict(name=g['name'],approximate_planes=planes));gem+=1
 out[f'{i}_points']=p.astype(np.float32);out[f'{i}_triangles']=t
assert gem==2
np.savez_compressed(C/'geometry.npz',**out);(C/'groups.json').write_text(json.dumps(G,indent=2));shutil.copy2(B/'materials.json',C/'materials.json')
for p in (B/'textures').glob('*.png'):shutil.copy2(p,C/'textures'/p.name)
(C/'physical_cut_review.json').write_text(json.dumps(dict(source='candidate19',measured_upper_facet_vertices=[[282,291],[420,232],[369,371],[455,328]],true_closed_convex_cut=True,not_an_appearance_texture=True,exposure_and_absorption_unchanged=True,domains=reports,native_review_pending=True),indent=2));print('Heart20 measured upper triangles prepared')
