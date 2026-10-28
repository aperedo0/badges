"""Copy the complete installed arrow background, without changing the trophy."""
from pathlib import Path
import zipfile,subprocess,json,hashlib
from pxr import Usd,UsdShade,Sdf
R=Path(__file__).resolve().parent;C=R/'candidate07';(C/'mobile').mkdir(parents=True,exist_ok=True);(C/'textures').mkdir(exist_ok=True)
source=R/'candidate06/mobile/emerald_trophy_badge_mobile.usdz';arrow=R.parent/'emerald_archer_20261023/mobile/emerald_archer_badge_mobile.usdz'
P=Path('/tmp/emerald_trophy_20261025/arrow_background_package');P.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(source) as z:
 members=z.namelist();z.extractall(P);usd=next(n for n in members if n.endswith('.usdc'))
a=Usd.Stage.Open(str(arrow));s=Usd.Stage.Open(str(P/usd));paths=['/Badge/_materials/New_field','/Badge/Front_field','/Badge/Back_field']
for path in paths:
 s.RemovePrim(path);assert Sdf.CopySpec(a.GetRootLayer(),path,s.GetRootLayer(),path)
with zipfile.ZipFile(arrow) as z:
 for suffix in ['color','roughness']:
  name='field_'+suffix+'.png';data=z.read('textures/'+name);(P/'textures'/name).write_bytes(data);(C/'textures'/name).write_bytes(data)
def attrs(stage):
 return {str(p.GetPath()):{x.GetName():((x.Get().path if isinstance(x.Get(),Sdf.AssetPath) else repr(x.Get())),[str(c) for c in x.GetConnections()]) for x in p.GetAttributes()} for p in stage.Traverse()}
original=Usd.Stage.Open(str(source));old=attrs(original);new=attrs(s)
for p in old:
 if any(p==root or p.startswith(root+'/') for root in paths):continue
 assert old[p]==new[p],p
for path in paths:
 left={k:v for k,v in attrs(a).items() if k==path or k.startswith(path+'/')};right={k:v for k,v in new.items() if k==path or k.startswith(path+'/')}
 assert left==right,path
assert s.GetRootLayer().Export(str(P/usd))
model=C/'mobile/emerald_trophy_badge_mobile.usdz';model.unlink(missing_ok=True)
subprocess.run(['/usr/bin/usdzip',str(model)]+members,cwd=P,check=True,capture_output=True)
check=subprocess.run(['/usr/bin/usdchecker','--arkit',str(model)],capture_output=True,text=True);assert check.returncode==0,check.stdout+check.stderr
with zipfile.ZipFile(source) as za,zipfile.ZipFile(model) as zb:
 assert za.namelist()==zb.namelist()
 for name in members:
  if name!=usd:assert za.read(name)==zb.read(name),name
facts={'complete_background_shader_graph':'exact copy of final arrow model','front_and_back_geometry_normals_UVs':'exact copy of final arrow model','background_texture_bytes':'exact copy of final arrow model','rim_and_crest':'unchanged from candidate06','USD_ARKit_validation':'passed','bytes':model.stat().st_size,'sha256':hashlib.sha256(model.read_bytes()).hexdigest()}
(C/'background_validation.json').write_text(json.dumps(facts,indent=2)+'\n');print(json.dumps(facts,indent=2))
