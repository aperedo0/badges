"""Apply the measured finish with true wall normals and planar grass faces."""
from pathlib import Path
import numpy as np,json,sys
C=Path(sys.argv[1]);D=dict(np.load(C/'parts.npz'));M=json.loads((C/'parts.json').read_text())
for p in M['parts']:
 name=p['name'];nf=p['front'];N=D[name+'_n'];wall=N[2*nf:];length=np.linalg.norm(wall[...,:2],axis=2);assert (length>1e-8).all();wall[...,:2]/=length[...,None];wall[...,2]=0
 mi=D[name+'_m'];mask=np.array([p['materials'][i] in ['Gold','GoldEdge','SmoothGold'] for i in mi]);mask[2*nf:]=False
 if name=='outer_gold_setting':mask[:]=False
 if mask.any():
  if 'FineGold' not in p['materials']:p['materials'].append('FineGold')
  mi[mask]=p['materials'].index('FineGold')
 if name.startswith('grass_blade_'):
  N[:nf]=[0,0,1];N[nf:2*nf]=[0,0,-1]
np.savez_compressed(C/'parts.npz',**D);(C/'parts.json').write_text(json.dumps(M,indent=1)+'\n');(C/'palette_overrides.json').write_text(json.dumps(dict(FineGold=dict(albedo=[.5395,.2795,.02925],metallic=1,roughness=.42)),indent=2)+'\n')
(C/'wall_finish.json').write_text(json.dumps(dict(wall_normals='True outward curve normals constant through depth. Removes the artificial front to back barrel normal sweep that produced vertical stripes.',grass='Planar face normals on the seven narrow gold strokes, with real geometry retained and the moderated FineGold finish.',native_review_pending=True),indent=2)+'\n')
