import sys,zipfile,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
selection=json.loads((ROOT/'selection.json').read_text());files=[Path(MANIFEST[t]['work'])/'candidates'/n/(t+'_badge_mobile.usdz') for t,n in selection.items()]
files += [p for version in ['current','updated'] for tier in selection
          for p in (ROOT/'inspection_models'/version/tier).rglob('*.usdz')]
reports=[]
for package in files:
 with tempfile.TemporaryDirectory(prefix='badge_package_verify_') as tmp:
  with zipfile.ZipFile(package) as z:
   names=z.namelist();z.extractall(tmp)
  root=Path(tmp)/names[0];stage=Usd.Stage.Open(str(root));tri=0;textures=[]
  for prim in stage.Traverse():
   if prim.IsA(UsdGeom.Mesh):tri+=len(UsdGeom.Mesh(prim).GetFaceVertexCountsAttr().Get())
   for a in prim.GetAttributes():
    if a.GetTypeName()==Sdf.ValueTypeNames.Asset:
     value=a.Get()
     if value and value.path:
      assert value.path in names,(package,'missing asset',value.path)
      textures.append(value.path)
  build=json.loads((package.parent/'build.json').read_text());assert tri==build['triangles'],(package,'stale geometry',tri,build['triangles'])
  assert sha(package)==build['sha256'],(package,'hash mismatch')
  reports.append({'package':str(package),'triangles':tri,'textures_resolve':True,'sha256':sha(package)})
(ROOT/'package_verification.json').write_text(json.dumps(reports,indent=2)+'\n');print('Verified',len(reports),'independently unpacked USDZ files, including geometry counts and every texture dependency.')
