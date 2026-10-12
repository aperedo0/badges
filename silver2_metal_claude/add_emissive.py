"""Run with Blender's python: add_emissive.py <usdc> [materials...] : connects 0/<mat>_emissive.png to emissiveColor (default: both star materials)."""
import sys
from pxr import Usd, UsdShade, Sdf
st = Usd.Stage.Open(sys.argv[1])
for mat in (sys.argv[2:] or ['Silver2_StarLit_Satin', 'Silver2_StarShaded_Satin']):
    base = f'/Silver2/Materials/{mat}'
    surf = UsdShade.Shader.Get(st, base + '/Surface')
    uv = UsdShade.Shader.Get(st, base + '/UV')
    tex = UsdShade.Shader.Define(st, base + '/emissiveColor')
    tex.CreateIdAttr('UsdUVTexture')
    tex.CreateInput('file', Sdf.ValueTypeNames.Asset).Set(f'0/{mat}_emissive.png')
    tex.CreateInput('sourceColorSpace', Sdf.ValueTypeNames.Token).Set('sRGB')
    tex.CreateInput('wrapS', Sdf.ValueTypeNames.Token).Set('clamp')
    tex.CreateInput('wrapT', Sdf.ValueTypeNames.Token).Set('clamp')
    tex.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(uv.ConnectableAPI(), 'result')
    out = tex.CreateOutput('rgb', Sdf.ValueTypeNames.Float3)
    surf.CreateInput('emissiveColor', Sdf.ValueTypeNames.Color3f).ConnectToSource(out)
st.GetRootLayer().Save()
print('emissive connected')
