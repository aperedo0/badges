"""Package the Blender sculptures with the approved bronze circular casing."""
from pathlib import Path
import importlib.util,sys

ROOT=Path(__file__).resolve().parent
TEMP=Path('/tmp/bronze_coins_20261018')
SOURCE=ROOT.parent/'botanical_match_20261014/sunrise/mobile/sunrise_badge_mobile.usdz'
SOURCES={name:SOURCE for name in ['lightning_compass','zen_balance','torch_sunburst']}
spec=importlib.util.spec_from_file_location('bronze_pack_backend',ROOT.parent/'star_island_20261016/pack.py')
backend=importlib.util.module_from_spec(spec);spec.loader.exec_module(backend)
backend.ROOT=ROOT;backend.TEMP=TEMP;backend.SOURCES=SOURCES
SHELL=backend.SHELL

original_add_material=backend.add_material
def add_material(stage,role,palette,pkg,calibration,name):
    mat=original_add_material(stage,role,palette,pkg,calibration,name)
    if name in ['zen_balance','torch_sunburst'] and role=='bronze' and not calibration:
        from pxr import UsdShade,Sdf
        filename='bronze_roughness.png'
        (pkg/'textures'/filename).write_bytes((ROOT/name/'textures'/filename).read_bytes())
        surface=UsdShade.Shader(stage.GetPrimAtPath(mat.GetPath().AppendChild('Surface')))
        reader=UsdShade.Shader(stage.GetPrimAtPath(mat.GetPath().AppendChild('UV')))
        tex=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('Roughness'))
        tex.CreateIdAttr('UsdUVTexture')
        tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+filename))
        tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('raw')
        tex.CreateInput('wrapS',Sdf.ValueTypeNames.Token).Set('clamp')
        tex.CreateInput('wrapT',Sdf.ValueTypeNames.Token).Set('clamp')
        tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result')
        tex.CreateOutput('r',Sdf.ValueTypeNames.Float)
        surface.GetInput('roughness').ConnectToSource(tex.ConnectableAPI(),'r')
    return mat
backend.add_material=add_material

if __name__=='__main__':
    for name in [s for s in sys.argv[1:] if s!='--calibration']:
        backend.build(name,'--calibration' in sys.argv)
