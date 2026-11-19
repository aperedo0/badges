"""Package one unfinished badge, preserving its preceding comparison baseline."""
from pathlib import Path
import sys,json,hashlib,subprocess,shutil,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pxr import Usd,UsdGeom,UsdShade
import compact
R=Path(__file__).resolve().parent;slug=sys.argv[1];state=json.loads((R/'schedule.json').read_text())
subprocess.run([sys.executable,str(R/'work_guard.py'),'120','badge packaging'],check=True)
assert state['badges'][slug]['status']!='done','Never restart a completed badge'
rows=json.loads((R/'manifest.json').read_text());row=next(x for x in rows if x['slug']==slug);b=R/slug;c=b/'candidate20';base=b/'baseline'
if base.exists():
 i=1
 while (b/('baseline04_archive_'+str(i))).exists():i+=1
 base.rename(b/('baseline04_archive_'+str(i)))
base.mkdir()
subprocess.run([sys.executable,'-I',str(R/'pack.py'),slug],check=True)
shutil.copy2(c/'mobile'/(slug+'_badge_mobile.usdz'),base/'model.usdz');shutil.copy2(c/'source'/(slug+'.blend'),base/'detailed.blend');shutil.copy2(c/'validation.json',base/'validation.json')
row.update(source=str(base/'model.usdz'),source_sha256=hashlib.sha256((base/'model.usdz').read_bytes()).hexdigest(),status='needs_optimization')
stage=Usd.Stage.Open(row['source']);row['protected_mesh_paths']=[str(p.GetPath()) for p in stage.Traverse() if p.IsA(UsdGeom.Mesh) and UsdShade.MaterialBindingAPI(p).ComputeBoundMaterial()[0].GetPrim().GetName().startswith('CrestGem_')]
(R/'manifest.json').write_text(json.dumps(rows,indent=2)+'\n');result=compact.compact(row)
results=json.loads((R/'optimization.json').read_text());results[slug]=result;(R/'optimization.json').write_text(json.dumps(results,indent=2)+'\n')
dest=Path(row['destination']);shutil.copy2(c/'model.usdz',dest/'coin.usdz');bd=dest.with_name(row['dataset']+'Baseline.dataset');bd.mkdir(exist_ok=True);shutil.copy2(base/'model.usdz',bd/'coin.usdz');shutil.copy2(dest/'Contents.json',bd/'Contents.json')
print(slug,'packaged without touching other badges',result['after'],flush=True)
