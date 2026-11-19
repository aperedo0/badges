"""A broad gently crowned gold face replaces the rejected double rail bezel."""
from pathlib import Path
import json,shutil
import numpy as np
R=Path(__file__).resolve().parent;B=R/'ruby_heart/candidate16';C=R/'ruby_heart/candidate17'
assert not (C/'geometry.npz').exists()
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
D=np.load(B/'geometry.npz');G=json.loads((B/'groups.json').read_text());S=json.loads((B/'materials.json').read_text());out={}
for i,g in enumerate(G):
 p=D[f'{i}_points'].copy();t=D[f'{i}_triangles'].copy()
 if g['name']=='Wide sculpted heart gold bezel':
  p=p.reshape(246,19,3)
  for j in range(3,14):p[:,j,2]=.033382539+.008*np.sin(np.pi*(j-3)/10)
  p=p.reshape(-1,3)
 out[f'{i}_points']=p;out[f'{i}_triangles']=t
np.savez_compressed(C/'geometry.npz',**out);(C/'groups.json').write_text(json.dumps(G,indent=2));(C/'materials.json').write_text(json.dumps(S,indent=2))
for p in (B/'textures').glob('*.png'):shutil.copy2(p,C/'textures'/p.name)
(C/'bezel_review.json').write_text(json.dumps(dict(source='candidate16',broad_front_band_replaces_concave_double_rail=True,outer_silhouette_and_gem_geometry_unchanged=True,gem_optics_unchanged=True,not_complete=True),indent=2));print('Heart17 broad bezel face prepared, actual gem cut unchanged')
