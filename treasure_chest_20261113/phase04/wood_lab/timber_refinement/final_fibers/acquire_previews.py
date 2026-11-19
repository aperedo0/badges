from pathlib import Path
import urllib.request,json,concurrent.futures
D=Path(__file__).resolve().parent/'resources';D.mkdir(exist_ok=True)
def get(url,path):
 if not path.exists():
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'BestSpentWoodStudy/1.0; Poly Haven artist resources'}),timeout=90) as r:path.write_bytes(r.read())
def asset(name):
 p=D/name;p.mkdir(exist_ok=True);get('https://api.polyhaven.com/files/'+name,p/'files.json');j=json.loads((p/'files.json').read_text());url=j['Diffuse']['1k']['jpg']['url'];get(url,p/'diffuse.jpg');get('https://cdn.polyhaven.com/asset_img/primary/'+name+'.png?width=650',p/'preview.png');print(name,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(asset,['raw_plank_wall','medieval_wood','plank_flooring_03']))
(D/'SOURCES.json').write_text(json.dumps(dict(license='CC0',license_url='https://polyhaven.com/license',assets=['https://polyhaven.com/a/'+n for n in ['raw_plank_wall','medieval_wood','plank_flooring_03']]),indent=2))
