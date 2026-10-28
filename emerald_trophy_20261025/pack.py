"""Package the complete trophy around the exactly preserved approved gold shell."""
from pathlib import Path
import importlib.util,json,sys
ROOT=Path(__file__).resolve().parent;TEMP=Path('/tmp/emerald_trophy_20261025')
spec=importlib.util.spec_from_file_location('trophy_backend',ROOT.parent/'star_island_20261016/pack.py')
backend=importlib.util.module_from_spec(spec);spec.loader.exec_module(backend)
backend.ROOT=ROOT;backend.TEMP=TEMP
backend.SOURCES={name:ROOT.parent/'botanical_match_20261014/sprout/mobile/sprout_badge_mobile.usdz' for name in ['candidate01','candidate02','candidate03','candidate04','candidate05']}
original=backend.add_material
def material(stage,role,palette,pkg,calibration,name):
    from pxr import UsdShade,Sdf,Gf
    m=original(stage,role,palette,pkg,calibration,name)
    surface=UsdShade.Shader(stage.GetPrimAtPath(m.GetPath().AppendChild('Surface')))
    emission=json.loads((ROOT/name/'design.json').read_text()).get('emission',{})
    if role in emission:surface.GetInput('emissiveColor').Set(Gf.Vec3f(*map(float,emission[role])))
    if role=='field':
        source=ROOT/name/'textures/field_roughness.png';(pkg/'textures'/source.name).write_bytes(source.read_bytes())
        reader=UsdShade.Shader(stage.GetPrimAtPath(m.GetPath().AppendChild('UV')))
        t=UsdShade.Shader.Define(stage,m.GetPath().AppendChild('Roughness'));t.CreateIdAttr('UsdUVTexture')
        t.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+source.name))
        t.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('raw')
        t.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result');t.CreateOutput('r',Sdf.ValueTypeNames.Float)
        surface.GetInput('roughness').ConnectToSource(t.ConnectableAPI(),'r')
    if role=='relief':
        source=ROOT/name/'textures/relief_emission.png';(pkg/'textures'/source.name).write_bytes(source.read_bytes())
        reader=UsdShade.Shader(stage.GetPrimAtPath(m.GetPath().AppendChild('UV')))
        t=UsdShade.Shader.Define(stage,m.GetPath().AppendChild('Emission'));t.CreateIdAttr('UsdUVTexture')
        t.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+source.name))
        t.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('sRGB')
        t.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result')
        t.CreateInput('scale',Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(8,8,8,1))
        t.CreateOutput('rgb',Sdf.ValueTypeNames.Float3)
        surface.GetInput('emissiveColor').ConnectToSource(t.ConnectableAPI(),'rgb')
    if role.startswith('emerald'):

        surface.CreateInput('clearcoat',Sdf.ValueTypeNames.Float).Set(.35)
        surface.CreateInput('clearcoatRoughness',Sdf.ValueTypeNames.Float).Set(.12)
    return m
backend.add_material=material
if __name__=='__main__':
    name=next((a for a in sys.argv[1:] if a.startswith('candidate')),'candidate01')
    backend.build(name)
    p=ROOT/name/'mobile'/(name+'_badge_mobile.usdz')
    p.rename(p.with_name('emerald_trophy_badge_mobile.usdz'))
