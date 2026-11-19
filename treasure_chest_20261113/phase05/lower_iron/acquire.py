from pathlib import Path
import urllib.request,zipfile,json,hashlib
D=Path(__file__).resolve().parent/'resources';D.mkdir(exist_ok=True);sources=[]
for asset in ['Metal055A','Metal003']:
 url='https://ambientcg.com/get?file='+asset+'_1K-PNG.zip';archive=D/(asset+'_1K-PNG.zip')
 if not archive.exists():
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'TreasureChestLookdev/1.0 (local art study)'}),timeout=90) as r:archive.write_bytes(r.read())
 folder=D/asset;folder.mkdir(exist_ok=True)
 with zipfile.ZipFile(archive) as z:
  for info in z.infolist():
   name=Path(info.filename).name
   if name.lower().endswith(('.png','.txt')) and any(k in name for k in ['Color','Roughness','NormalGL','Displacement','Metalness','LICENSE']):(folder/name).write_bytes(z.read(info))
 sources.append(dict(asset=asset,page='https://ambientcg.com/view?id='+asset,download=url,license='CC0 1.0',license_url='https://docs.ambientcg.com/license/',archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),files=sorted(p.name for p in folder.iterdir())))
 print(asset,sorted(p.name for p in folder.iterdir()),flush=True)
(D/'SOURCES.json').write_text(json.dumps(sources,indent=2))
