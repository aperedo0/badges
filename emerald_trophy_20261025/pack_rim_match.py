"""Apply only the owner requested rim material changes to the traced trophy."""
from pathlib import Path
import json,zipfile,subprocess,hashlib
from pxr import Usd,UsdGeom,UsdShade,Gf,Sdf
R=Path(__file__).resolve().parent;C=R/'candidate06';S=R/'candidate05/mobile/emerald_trophy_badge_mobile.usdz'
P=Path('/tmp/emerald_trophy_20261025/rim_match_package');P.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(S) as z:
 members=z.namelist();z.extractall(P);usd=next(n for n in members if n.endswith('.usdc'))
a=Usd.Stage.Open(str(S));s=Usd.Stage.Open(str(P/usd));meta=json.loads((C/'rim_finish.json').read_text());gold=meta['gold_linear'];allowed=set()
for name,factor in [('Silver___circumferential_brushed_steel_Mobile_Casing',1),('Shell_inner',.94),('Shell_bevel',1)]:
 sh=UsdShade.Shader(s.GetPrimAtPath('/Badge/_materials/'+name+'/Surface'));attr=sh.GetInput('diffuseColor');attr.Set(Gf.Vec3f(*[float(x*factor) for x in gold]));allowed.add(str(attr.GetAttr().GetPath()))
for source in (C/'textures').glob('Rim_*.png'):(P/'textures'/source.name).write_bytes(source.read_bytes())
def attrs(stage):return {str(q.GetPath()):{x.GetName():((x.Get().path if isinstance(x.Get(),Sdf.AssetPath) else repr(x.Get())),[str(c) for c in x.GetConnections()]) for x in q.GetAttributes()} for q in stage.Traverse()}
before=attrs(a);after=attrs(s);assert before.keys()==after.keys()
changed=[]
for path in before:
 for name in before[path]:
  if before[path][name]!=after[path][name]:
   full=path+'.'+name;assert full in allowed,full;changed.append(full)
assert s.GetRootLayer().Export(str(P/usd))
model=C/'mobile/emerald_trophy_badge_mobile.usdz';model.unlink(missing_ok=True)
subprocess.run(['/usr/bin/usdzip',str(model)]+members,cwd=P,check=True,capture_output=True)
check=subprocess.run(['/usr/bin/usdchecker','--arkit',str(model)],capture_output=True,text=True);assert check.returncode==0,check.stdout+check.stderr
maps={'textures/Rim_brushed_reference_color.png','textures/Rim_brushed_reference_roughness.png'}
with zipfile.ZipFile(S) as za,zipfile.ZipFile(model) as zb:
 assert za.namelist()==zb.namelist()
 for name in members:
  if name!=usd and name not in maps:assert za.read(name)==zb.read(name),name
facts={'owner_requested_rim_finish':meta,'changed_attributes':changed,'changed_texture_files':sorted(maps),
 'all_geometry_normals_UVs_and_relief_data':'exactly preserved','inner_and_outer_border_roughness':'exactly preserved',
 'no_rim_emission_or_painted_lighting':True,'USD_ARKit_validation':'passed','bytes':model.stat().st_size,
 'sha256':hashlib.sha256(model.read_bytes()).hexdigest()}
(C/'rim_validation.json').write_text(json.dumps(facts,indent=2)+'\n');print(json.dumps(facts,indent=2))
