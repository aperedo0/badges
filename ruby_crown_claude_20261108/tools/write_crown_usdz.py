"""Write the Ruby Crown USDZ from a geometry npz. Run with Blender's Python (pxr).

Usage: write_crown_usdz.py GEOM.npz OUT.usdz [velvet.png]
"""
import sys, os, tempfile
import numpy as np
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Vt, UsdUtils

d = np.load(sys.argv[1]); out = os.path.abspath(sys.argv[2])
tmp = tempfile.mkdtemp(); path = os.path.join(tmp, 'ruby_crown.usdc')
stage = Usd.Stage.CreateNew(path)
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y); UsdGeom.SetStageMetersPerUnit(stage, 1.0)
root = UsdGeom.Xform.Define(stage, '/Badge'); stage.SetDefaultPrim(root.GetPrim())
UsdGeom.Scope.Define(stage, '/Badge/Materials')
MATS = {
    'gold': ('RubyCrown_Gold', (1.0, 0.42, 0.06), 1.0, 0.24),
    'gold_leaf': ('RubyCrown_GoldLeaf', (1.0, 0.40, 0.055), 1.0, 0.40),
    'gold_recess': ('RubyCrown_GoldRecess', (0.16, 0.075, 0.022), 1.0, 0.55),
    'frieze': ('RubyCrown_Frieze', (0.045, 0.030, 0.018), 0.0, 1.0),
    'velvet': ('red_velvet', (0.105, 0.0025, 0.010), 0.0, 0.86),
    'ruby': ('CrestGem_CrownFoilRuby', (0.55, 0.01, 0.08), 0.0, 0.05),
    'ruby_small': ('CrestGem_CrownFoilRubySmall', (0.55, 0.01, 0.08), 0.0, 0.05),
    'clear': ('CrestGem_CrownFoilClear', (0.85, 0.85, 0.9), 0.0, 0.03),
}
NAMES = {'ruby_small': 'SmallRubies', 'gold': 'Gold', 'gold_leaf': 'GoldLeaves', 'gold_recess': 'GoldRecess', 'frieze': 'Frieze', 'velvet': 'Velvet', 'ruby': 'Rubies', 'clear': 'ClearStones'}
VELVET_TEX = sys.argv[3] if len(sys.argv) > 3 else None
for key, (name, col, met, rough) in MATS.items():
    if key + '_v' not in d.files: continue
    m = UsdShade.Material.Define(stage, f'/Badge/Materials/{name}')
    sh = UsdShade.Shader.Define(stage, f'/Badge/Materials/{name}/Surface'); sh.CreateIdAttr('UsdPreviewSurface')
    dc = sh.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f); dc.Set(Gf.Vec3f(*col))
    if key == 'velvet' and VELVET_TEX:
        rd = UsdShade.Shader.Define(stage, f'/Badge/Materials/{name}/VelvetUV'); rd.CreateIdAttr('UsdPrimvarReader_float2')
        rd.CreateInput('varname', Sdf.ValueTypeNames.String).Set('st')
        tx = UsdShade.Shader.Define(stage, f'/Badge/Materials/{name}/VelvetColor'); tx.CreateIdAttr('UsdUVTexture')
        tx.CreateInput('file', Sdf.ValueTypeNames.Asset).Set('textures/velvet.png')
        tx.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(rd.ConnectableAPI(), 'result')
        tx.CreateInput('wrapS', Sdf.ValueTypeNames.Token).Set('repeat'); tx.CreateInput('wrapT', Sdf.ValueTypeNames.Token).Set('clamp')
        tx.CreateInput('sourceColorSpace', Sdf.ValueTypeNames.Token).Set('sRGB')
        tx.CreateOutput('rgb', Sdf.ValueTypeNames.Float3)
        dc.ConnectToSource(tx.ConnectableAPI(), 'rgb')
    sh.CreateInput('metallic', Sdf.ValueTypeNames.Float).Set(met)
    sh.CreateInput('roughness', Sdf.ValueTypeNames.Float).Set(rough)
    sh.CreateInput('opacity', Sdf.ValueTypeNames.Float).Set(1.0)
    if key == 'frieze':
        sh.CreateInput('useSpecularWorkflow', Sdf.ValueTypeNames.Int).Set(1)
        sh.CreateInput('specularColor', Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0.0, 0.0, 0.0))
    m.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(), 'surface')
    V, N, T = d[key + '_v'], d[key + '_n'], d[key + '_t']
    mesh = UsdGeom.Mesh.Define(stage, f'/Badge/{NAMES[key]}')
    mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(V.astype(np.float32)))
    mesh.CreateFaceVertexCountsAttr(Vt.IntArray([3] * len(T)))
    mesh.CreateFaceVertexIndicesAttr(Vt.IntArray(T.astype(np.int32).ravel().tolist()))
    mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(N.astype(np.float32))); mesh.SetNormalsInterpolation(UsdGeom.Tokens.vertex)
    mesh.CreateSubdivisionSchemeAttr('none'); mesh.CreateDoubleSidedAttr(False)
    mesh.CreateExtentAttr(Vt.Vec3fArray([Gf.Vec3f(*V.min(0).tolist()), Gf.Vec3f(*V.max(0).tolist())]))
    if key + '_uv' in d.files:
        pv = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar('st', Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.vertex)
        pv.Set(Vt.Vec2fArray.FromNumpy(d[key + '_uv'].astype(np.float32)))
    UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(m)
stage.GetRootLayer().Save()
if VELVET_TEX:
    import shutil
    os.makedirs(os.path.join(tmp, 'textures'), exist_ok=True); shutil.copy(VELVET_TEX, os.path.join(tmp, 'textures', 'velvet.png'))
cwd = os.getcwd(); os.chdir(tmp)
ok = UsdUtils.CreateNewARKitUsdzPackage(Sdf.AssetPath('ruby_crown.usdc'), out)
os.chdir(cwd)
print('usdz written', ok, out, os.path.getsize(out))
