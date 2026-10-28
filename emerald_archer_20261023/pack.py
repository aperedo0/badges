"""Preserve the approved complete gold shell and package Blender relief data."""
from pathlib import Path
import importlib.util,sys,json
ROOT=Path(__file__).resolve().parent
TEMP=Path('/tmp/emerald_archer_20261023')
spec=importlib.util.spec_from_file_location('archer_pack_backend',ROOT.parent/'star_island_20261016/pack.py')
backend=importlib.util.module_from_spec(spec);spec.loader.exec_module(backend)
backend.ROOT=ROOT;backend.TEMP=TEMP
backend.SOURCES={name:ROOT.parent/'botanical_match_20261014/sprout/mobile/sprout_badge_mobile.usdz' for name in ['candidate01','candidate02']}
original_add_material=backend.add_material
def add_material(stage,role,palette,pkg,calibration,name):
    from pxr import UsdShade,Sdf,Gf
    mat=original_add_material(stage,role,palette,pkg,calibration,name)
    surface=UsdShade.Shader(stage.GetPrimAtPath(mat.GetPath().AppendChild('Surface')))
    if role=='field' and not calibration:
        reader=UsdShade.Shader(stage.GetPrimAtPath(mat.GetPath().AppendChild('UV')))
        for suffix,channel,space in [('color','diffuseColor','sRGB'),('roughness','roughness','raw')]:
            filename='field_'+suffix+'.png';(pkg/'textures'/filename).write_bytes((ROOT/name/'textures'/filename).read_bytes())
            if not reader:
                reader=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('UV'));reader.CreateIdAttr('UsdPrimvarReader_float2')
                reader.CreateInput('varname',Sdf.ValueTypeNames.String).Set('CoinReliefUV');reader.CreateOutput('result',Sdf.ValueTypeNames.Float2)
            tex=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild(suffix.title()))
            tex.CreateIdAttr('UsdUVTexture');tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+filename))
            tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set(space)
            tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result')
            output='r' if suffix=='roughness' else 'rgb';tex.CreateOutput(output,Sdf.ValueTypeNames.Float if output=='r' else Sdf.ValueTypeNames.Float3)
            surface.GetInput(channel).ConnectToSource(tex.ConnectableAPI(),output)
    if role.startswith('emerald'):
        surface.CreateInput('clearcoat',Sdf.ValueTypeNames.Float).Set(.35)
        surface.CreateInput('clearcoatRoughness',Sdf.ValueTypeNames.Float).Set(.12)
        emission=ROOT/name/'textures'/(role+'_emission.png')
        if emission.exists() and not calibration:
            filename=emission.name;(pkg/'textures'/filename).write_bytes(emission.read_bytes())
            reader=UsdShade.Shader(stage.GetPrimAtPath(mat.GetPath().AppendChild('UV')))
            tex=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('Emission'));tex.CreateIdAttr('UsdUVTexture')
            tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+filename))
            tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('sRGB')
            tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result')
            tex.CreateOutput('rgb',Sdf.ValueTypeNames.Float3)
            surface.GetInput('emissiveColor').ConnectToSource(tex.ConnectableAPI(),'rgb')
    return mat
backend.add_material=add_material
if __name__=='__main__':
    # The common packer uses the model's public name for its geometry file.
    import numpy as np
    name='candidate02' if 'candidate02' in sys.argv else 'candidate01'
    geometry=np.load(TEMP/'emerald_archer_geometry.npz')
    np.savez_compressed(TEMP/(name+'_geometry.npz'),**{k:geometry[k].astype(float) if not k.endswith('_triangles') else geometry[k] for k in geometry.files})
    backend.build(name,'--calibration' in sys.argv)
    source=ROOT/name/'mobile'/(name+'_badge_mobile.usdz')
    if '--calibration' not in sys.argv:source.rename(source.with_name('emerald_archer_badge_mobile.usdz'))
