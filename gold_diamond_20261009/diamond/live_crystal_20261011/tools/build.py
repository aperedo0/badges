from pathlib import Path
import sys, json, shutil
import numpy as np
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf

COMMON = Path('/Users/antonioperedo/Desktop/badges/all_sides_20261010/tools')
sys.path.insert(0, str(COMMON))
from model_common import read_mesh, write_mesh, finish

ROOT = Path(__file__).resolve().parents[1]
number = sys.argv[sys.argv.index('--') + 1]
out = ROOT / 'candidates' / number
out.mkdir(parents=True, exist_ok=True)
edit = out / 'usd'
assert not edit.exists()
edit.mkdir()
source = Path('/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/diamond/all_sides_20261010/candidates/04/usd/compacted.usdc')
layer = Sdf.Layer.CreateNew(str(edit / 'diamond.usdc'))
layer.TransferContent(Sdf.Layer.FindOrOpen(str(source)))
stage = Usd.Stage.Open(layer)
mesh = next(p for p in stage.Traverse() if p.IsA(UsdGeom.Mesh))
p, f, n, oldmat, uv = read_mesh(mesh)
stage.RemovePrim('/DiamondCrystal/Materials')

def material(name, color, roughness, metal=0., opacity=1., coat=0., ior=2.42, emission=(0.,0.,0.)):
    mat = UsdShade.Material.Define(stage, '/DiamondCrystal/Materials/' + name)
    sh = UsdShade.Shader.Define(stage, mat.GetPath().AppendChild('Surface'))
    sh.CreateIdAttr('UsdPreviewSurface')
    for key, val in {'diffuseColor':color, 'emissiveColor':emission}.items():
        sh.CreateInput(key, Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*val))
    for key, val in {'roughness':roughness,'metallic':metal,'opacity':opacity,'clearcoat':coat,'clearcoatRoughness':.075,'ior':ior}.items():
        sh.CreateInput(key, Sdf.ValueTypeNames.Float).Set(float(val))
    sh.CreateOutput('surface', Sdf.ValueTypeNames.Token)
    mat.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(), 'surface')
    return str(mat.GetPath())

if number == '01':
    shell = material('CrystalExterior', (.008,.025,.055), .075, opacity=.22, coat=.35)
    write_mesh(stage, mesh.GetPath(), p, f, n, [shell]*len(f))
    angle=np.deg2rad(7.5)
    rot=np.array([[np.cos(angle),0,np.sin(angle)],[0,1,0],[-np.sin(angle),0,np.cos(angle)]])
    center=np.array([0.,-.05,0.])
    core=(p-center)*.88@rot.T+center
    cn=n@rot.T
    coremat=material('BlueInternalFacets', (.035,.15,.42), .12, metal=1., coat=.2, emission=(.002,.006,.015))
    write_mesh(stage, '/DiamondCrystal/InteriorFacets', core, f, cn, [coremat]*len(f))
elif number=='02':
    shell = material('LiveBlueCrystal', (.045,.19,.48), .18, metal=0., coat=.6, opacity=1.)
    write_mesh(stage, mesh.GetPath(), p, f, n, [shell]*len(f))
else:
    shell=material('LiveBlueCrystal',(.045,.19,.48),.14 if number=='05' else .18,metal=.25 if number=='05' else 0.,coat=.7 if number=='05' else .6,emission=(.008,.02,.035))
    sh=UsdShade.Shader.Get(stage,Sdf.Path(shell).AppendChild('Surface'))
    reader=UsdShade.Shader.Define(stage,Sdf.Path(shell).AppendChild('UV'))
    reader.CreateIdAttr('UsdPrimvarReader_float2')
    reader.CreateInput('varname',Sdf.ValueTypeNames.String).Set('BadgeUV')
    reader.CreateOutput('result',Sdf.ValueTypeNames.Float2)
    texture=UsdShade.Shader.Define(stage,Sdf.Path(shell).AppendChild('BodyColor'))
    texture.CreateIdAttr('UsdUVTexture')
    shutil.copyfile(out/'textures/body_color.png',edit/'body_color.png')
    texture.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('body_color.png'))
    texture.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('sRGB')
    texture.CreateInput('wrapS',Sdf.ValueTypeNames.Token).Set('repeat')
    texture.CreateInput('wrapT',Sdf.ValueTypeNames.Token).Set('clamp')
    texture.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result')
    texture.CreateOutput('rgb',Sdf.ValueTypeNames.Float3)
    sh.GetInput('diffuseColor').ConnectToSource(texture.ConnectableAPI(),'rgb')
    write_mesh(stage,mesh.GetPath(),p,f,n,[shell]*len(f),uv)
finish('diamond', ROOT, out, stage, [{
    'design':'Unchanged round gem exterior. Candidate 01 includes an inset optical interior; candidate 02 measures the directly lit dielectric facets; subsequent candidates retain the original round geometry.',
    'material':('Transparent reflective exterior plus opaque interior' if number=='01' else 'Uniform directly lit dielectric calibration' if number=='02' else 'Measured light-responsive optical body color with live dielectric specular and clearcoat; low uniform blue emission, no emissive picture texture'),
    'source_round_sha256':'2ba20a7cf8a5efb7bcbe764879bc8205a9845f38f7c080aa1999a0d2c1ca3b16'
}])
(out/'NOTES.md').write_text('Kept the previous full round gem geometry; replaced fixed optical emission with calibrated body color and live specular lighting.\nThe optical pattern now changes brightness under the app lighting as its facets turn; a small uniform blue emission maintains shadow readability.\n' if number not in ['01','02'] else 'Material calibration experiment on a copy of the previous round gem.\nCompared transparency and direct facet lighting under the actual Home stage.\n')
