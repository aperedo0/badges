"""Add physical gathered folds inside each existing crown arch sector."""
from pathlib import Path
import json,shutil,numpy as np
R=Path(__file__).resolve().parent;B=R/'ruby_crown/candidate13';C=R/'ruby_crown/candidate14'
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
D=np.load(B/'geometry.npz');G=json.loads((B/'groups.json').read_text());out={};changed=[]
for i,g in enumerate(G):
 p=D[f'{i}_points'].copy();t=D[f'{i}_triangles']
 if 'velvet cushion' in g['name']:
  N,M=g['cloth_grid'];p=p.reshape(M+1,N,3);u=np.arange(N)/N;s=np.arange(M+1)/(M);phase=(u*8)%1
  gathering=np.exp(-.5*((phase-.5)/.105)**2)[None,:]*np.sin(np.pi*s)[:,None]**.85;factor=1-.185*gathering
  xcenter=p[:,:,0].mean(1)[:,None];zcenter=p[:,:,2].mean(1)[:,None];oldz=p[:,:,2].copy();p[:,:,0]=xcenter+(p[:,:,0]-xcenter)*factor;p[:,:,2]=zcenter+(p[:,:,2]-zcenter)*factor;p[:,:,1]+=(p[:,:,2]-oldz)*np.tan(np.radians(3))/.9-.045*gathering
  p=p.reshape(-1,3);changed.append(g['name'])
 out[f'{i}_points']=p;out[f'{i}_triangles']=t
np.savez_compressed(C/'geometry.npz',**out);(C/'groups.json').write_text(json.dumps(G,indent=2));shutil.copy2(B/'materials.json',C/'materials.json');shutil.copy2(B/'textures/gold_roughness.png',C/'textures/gold_roughness.png')
(C/'fold_report.json').write_text(json.dumps(dict(source='candidate13',changed_only=changed,additional_physical_gathers=8,arch_contact_positions_preserved=True,gold_and_all_stones_unchanged=True,radial_gather_depth=.185),indent=2));print('Ruby14 extra physical gathers saved, all gold and optical geometry preserved')
