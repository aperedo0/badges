from pathlib import Path
import subprocess,json,shutil,sys,hashlib
from pxr import Usd,UsdGeom,UsdShade
sys.path.insert(0,str(Path(__file__).resolve().parent))
import compact
R=Path(__file__).resolve().parent;rows=json.loads((R/'gallery.json').read_text())
for row in rows:
 slug=row['slug'];b=R/slug;c=b/'candidate15';base=b/'baseline'
 subprocess.run([sys.executable,'-I',str(R/'pack.py'),slug],check=True)
 shutil.copy2(c/'mobile'/(slug+'_badge_mobile.usdz'),base/'model.usdz')
 shutil.copy2(c/'source'/(slug+'.blend') if (c/'source'/(slug+'.blend')).exists() else b/'candidate01/source'/(slug+'.blend'),base/'detailed.blend')
 shutil.copy2(c/'validation.json',base/'validation.json')
 row.update(title=row['name'],status='needs_optimization',source=str(base/'model.usdz'),source_sha256=hashlib.sha256((base/'model.usdz').read_bytes()).hexdigest())
 stage=Usd.Stage.Open(row['source']);row['protected_mesh_paths']=[str(p.GetPath()) for p in stage.Traverse() if p.IsA(UsdGeom.Mesh) and UsdShade.MaterialBindingAPI(p).ComputeBoundMaterial()[0].GetPrim().GetName().startswith('CrestGem_')]
(R/'manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
results={}
for row in rows:
 results[row['slug']]=compact.compact(row)
 dest=Path(row['destination']);shutil.copy2(R/row['slug']/'candidate15/model.usdz',dest/'coin.usdz')
 bd=dest.with_name(row['dataset']+'Baseline.dataset');bd.mkdir(exist_ok=True);shutil.copy2(R/row['slug']/'baseline/model.usdz',bd/'coin.usdz');shutil.copy2(dest/'Contents.json',bd/'Contents.json')
 print(row['slug'],'compact',results[row['slug']]['after'],flush=True)
(R/'optimization.json').write_text(json.dumps(results,indent=2)+'\n')
