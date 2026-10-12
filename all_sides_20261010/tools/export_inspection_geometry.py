import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
selection=json.loads((ROOT/(sys.argv[sys.argv.index('--selection')+1] if '--selection' in sys.argv else 'selection.json')).read_text())
packages=[p for version in ['current','updated'] for tier in selection for p in (ROOT/'inspection_models'/version/tier).rglob('*.usdz')]
for package in packages:
 stage=Usd.Stage.Open(str(package));pts=[];faces=[];offset=0
 for prim in stage.Traverse():
  if prim.IsA(UsdGeom.Mesh):
   p,f,*_=read_mesh(prim);pts.append(p);faces.append(f+offset);offset+=len(p)
 np.savez_compressed(package.parent/'geometry.npz',points=np.concatenate(pts),faces=np.concatenate(faces))
print('Inspection geometry exported.')
