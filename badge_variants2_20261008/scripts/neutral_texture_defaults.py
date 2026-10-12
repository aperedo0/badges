"""Diagnostic: neutral disconnected fallback inputs, identical mapped values.

USD tools ignore fallback values when an input is connected. This test checks
whether RealityKit instead combines them with textures. No geometry changes.
"""
from pathlib import Path
import sys,json,zipfile,hashlib
from pxr import Usd,UsdShade,UsdUtils,Sdf,Gf
ROOT=Path(__file__).resolve().parents[1]
kind=sys.argv[sys.argv.index('--')+1]
base=ROOT/kind
dest=base/'iterations/11';dest.mkdir(exist_ok=False)
model=base/'iterations/10'/f'{kind}_badge_mobile.usdz'
work=dest/'package';work.mkdir()
with zipfile.ZipFile(model) as z:z.extractall(work)
path=next(work.glob('*.usdc'))
stage=Usd.Stage.Open(str(path));changes=[]
for p in stage.Traverse():
    if not p.IsA(UsdShade.Shader):continue
    sh=UsdShade.Shader(p)
    if sh.GetIdAttr().Get()!='UsdPreviewSurface':continue
    for name,val in [('diffuseColor',Gf.Vec3f(1,1,1)),('roughness',1.)]:
        inp=sh.GetInput(name)
        if inp and inp.HasConnectedSource():
            changes.append({'shader':str(p.GetPath()),'input':name,'old':str(inp.Get()),'new':str(val)})
            inp.Set(val)
stage.GetRootLayer().Save();out=dest/model.name
assert UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(str(path)),str(out))
c=UsdUtils.ComplianceChecker(arkit=True);c.CheckCompliance(str(out))
assert not c.GetErrors() and not c.GetFailedChecks()
info={'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'changed_fallbacks':changes,'geometry_changed':False,'connected_texture_values_changed':False,'compliance':{'errors':c.GetErrors(),'failed_checks':c.GetFailedChecks(),'warnings':c.GetWarnings()}}
(dest/'build.json').write_text(json.dumps(info,indent=2)+'\n')
(dest/'NOTES.md').write_text('Diagnostic only: neutralize fallback diffuse/roughness values on connected texture inputs. Actual maps, geometry and normals unchanged. If the app follows USD connection semantics, appearance will be identical to10.\n')
print(kind,info['sha256'])
