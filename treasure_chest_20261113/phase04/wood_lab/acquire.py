import urllib.request,json,concurrent.futures,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent/'resources';P.mkdir(exist_ok=True)
def get(url,dest):
 if dest.exists():return
 req=urllib.request.Request(url,headers={'User-Agent':'BestSpentWoodLookdev/1.0 (local artist study; assets from Poly Haven)'})
 with urllib.request.urlopen(req,timeout=120) as r:dest.write_bytes(r.read())
def asset(name):
 d=P/name;d.mkdir(exist_ok=True)
 get('https://api.polyhaven.com/files/'+name,d/'files.json')
 get('https://api.polyhaven.com/info/'+name,d/'info.json')
 data=json.loads((d/'files.json').read_text())
 for role,ext in [('Diffuse','jpg'),('Rough','jpg'),('nor_gl','png'),('Displacement','png')]:
  entry=data[role]['2k'].get(ext) or next(iter(data[role]['2k'].values()))
  url=entry['url'];get(url,d/url.rsplit('/',1)[1]);print(name,role,url,flush=True)
 get('https://cdn.polyhaven.com/asset_img/primary/'+name+'.png?width=700',d/'preview.png')
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(asset,['rough_wood','wood_cabinet_worn_long']))
d=P/'texturecan_wood0034';d.mkdir(exist_ok=True)
get('https://www.texturecan.com/img/textures/wood_0034/wood_0034_plane_600.png',d/'preview.png')
get('https://www.texturecan.com/downloads/wood_0034/wood_0034_2k_skKy8z.zip',d/'maps.zip')
with zipfile.ZipFile(d/'maps.zip') as z:z.extractall(d/'maps')
(P/'SOURCES.json').write_text(json.dumps(dict(license='CC0 1.0',polyhaven_license='https://polyhaven.com/license',polyhaven_api='https://polyhaven.com/our-api',texturecan_license='https://www.texturecan.com/terms/',assets=['https://polyhaven.com/a/rough_wood','https://polyhaven.com/a/wood_cabinet_worn_long','https://www.texturecan.com/details/288/']),indent=2))
