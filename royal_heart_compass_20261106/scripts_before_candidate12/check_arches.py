"""Prove the metal arch ends enter the same solid joining hub."""
from pathlib import Path
import json,numpy as np
from scipy.spatial import ConvexHull
R=Path(__file__).resolve().parent;report={};state=json.loads((R/'schedule.json').read_text())
for key in ['amethyst_crown','ruby_crown','emerald_crown']:
 C=(R/key/'candidate11') if key=='amethyst_crown' else Path(state['badges'][key]['candidate']);g=json.loads((C/'groups.json').read_text());D=np.load(C/'geometry.npz')
 i=next(i for i,a in enumerate(g) if a['name']=='Gold central joining hub');planes=ConvexHull(D[str(i)+'_points']).equations
 rows=[]
 for i,a in enumerate(g):
  if not (a['name'].startswith('Continuous ') and 'crown arch to central hub' in a['name']):continue
  p=D[str(i)+'_points'][-8:];inside=np.all(p@planes[:,:3].T+planes[:,3]<=1e-5,axis=1)
  assert inside.any(),(key,a['name'],'Arch misses joining hub')
  rows.append(dict(arch=a['name'],end_vertices_inside_solid_hub=int(inside.sum())))
 assert len(rows)==8
 if key=='ruby_crown':
  upper=[a for a in g if a['name'] in ['Top fleur ruby round stone','Upper arch ruby diamond independent gemstone']]
  assert len(upper)==4 and all(a['mat'] in ['CrestGem_Ruby','CrestGem_CrownRuby'] for a in upper)
 report[key]=dict(all_eight_arches_overlap_same_hub=True,arches=rows,upper_stones_red=key=='ruby_crown')
(R/'arch_connections.json').write_text(json.dumps(report,indent=2)+'\n');print('All 24 arches physically enter their central hubs. Red crown upper stones use ruby.')
