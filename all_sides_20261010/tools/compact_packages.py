import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
selection=json.loads((ROOT/'selection.json').read_text());report={}
for tier,num in selection.items():
 w=Path(MANIFEST[tier]['work']);out=w/'candidates'/num;build=json.loads((out/'build.json').read_text());source=next((out/'usd').glob('*.usd*'));original=Sdf.Layer.FindOrOpen(str(source));layer=Sdf.Layer.CreateAnonymous();layer.TransferContent(original)
 assert layer.ExportToString()==original.ExportToString(),tier
 dest=out/'usd/compacted.usdc';layer.Export(str(dest));fresh=Sdf.Layer.FindOrOpen(str(dest));fresh.Reload(True);assert fresh.ExportToString()==original.ExportToString(),(tier,'roundtrip changed scene')
 finish(tier,w,out,Usd.Stage.Open(fresh),build['changes'])
 latest=json.loads((out/'build.json').read_text());report[tier]={'before_bytes':build['bytes'],'after_bytes':latest['bytes'],'scene_text_identical':True,'triangles':latest['triangles']}
(ROOT/'compaction.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
