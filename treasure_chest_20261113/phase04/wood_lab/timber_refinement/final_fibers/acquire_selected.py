from pathlib import Path
import urllib.request,json,concurrent.futures
D=Path(__file__).resolve().parent/'resources'
def get(url,path):
 if not path.exists():
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'BestSpentWoodStudy/1.0; assets from Poly Haven'}),timeout=150) as r:path.write_bytes(r.read())
def asset(name):
 p=D/name;j=json.loads((p/'files.json').read_text())
 for role,res,ext in [('Diffuse','4k','jpg'),('nor_gl','4k','png'),('Displacement','4k','png'),('Rough','2k','jpg')]:
  data=j[role][res][ext];dest=p/data['url'].rsplit('/',1)[1];get(data['url'],dest);print(name,role,dest.stat().st_size,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(asset,['raw_plank_wall','medieval_wood']))
