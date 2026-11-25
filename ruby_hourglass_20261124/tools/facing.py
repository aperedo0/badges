"""Create the two nested optical cores with a polished, continuous outer surface."""
import json, shutil, sys
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[1]
folder=root/(sys.argv[1] if len(sys.argv)>1 else json.loads((root/'design.json').read_text())['candidate'])
folder.mkdir(exist_ok=True)
base=folder if folder.name in ('candidate04','candidate05') else root/'candidate01'
g=json.loads((base/'geometry.json').read_text())
for name in ['Upper_Ruby','Lower_Ruby']:
    outer=g.get(name+'_Facing',g[name]).copy();g[name+'_Facing']=outer
    pts=np.array(outer['points']);norm=np.array(outer['normals']);faces=np.array(outer['triangles'])
    center=(pts.max(axis=0)+pts.min(axis=0))*.5
    inner=center+(pts-center)*np.array([.972,.994,.94] if folder.name in ('candidate04','candidate05') else [.988,.994,.965])
    gap=(norm*pts[faces[:,0]]).sum(axis=1)[:,None]-norm@inner.T
    assert gap.min()>.0005,(name,gap.min())
    a,b,c=inner[faces].transpose(1,0,2)
    core_norm=np.cross(b-a,c-a);core_norm/=np.linalg.norm(core_norm,axis=1)[:,None]
    g[name]=dict(points=inner.round(9).tolist(),triangles=faces.tolist(),normals=core_norm.round(9).tolist())
    print(name,'minimum inset',gap.min())
(folder/'geometry.json').write_text(json.dumps(g,separators=(',',':')))
if base!=folder:shutil.copy2(base/'BronzeBrush.png',folder/'BronzeBrush.png')
if not (folder/'facing.json').exists():
    settings=json.loads((root/'design.json').read_text()) if folder.name in ('candidate04','candidate05') else dict(color=[.27,.004,.012],metallic=.47,roughness=.19,opacity=.78)
    (folder/'facing.json').write_text(json.dumps(settings,indent=2)+'\n')
