"""Write the Ruby Heart USDZ from a geometry npz. Run with Blender's Python (pxr).

Usage: write_usdz.py GEOM.npz OUT.usdz [gold_roughness.png|-] [gold r,g,b]
Y up, 1 unit per meter, front +Z, identity transforms, UsdPreviewSurface only.
"""
import sys, os, shutil, tempfile
import numpy as np
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Vt, UsdUtils

src, out = sys.argv[1], sys.argv[2]
rough_tex = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != '-' else None
gold_color = tuple(float(x) for x in sys.argv[4].split(',')) if len(sys.argv) > 4 else (0.98, 0.70, 0.30)
d = np.load(src)
tmp = tempfile.mkdtemp()
usda = os.path.join(tmp, 'ruby_heart.usdc')
stage = Usd.Stage.CreateNew(usda)
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
UsdGeom.SetStageMetersPerUnit(stage, 1.0)
root = UsdGeom.Xform.Define(stage, '/Badge')
stage.SetDefaultPrim(root.GetPrim())
UsdGeom.Scope.Define(stage, '/Badge/Materials')

def preview(name, color, metallic, rough, rough_file=None):
    m = UsdShade.Material.Define(stage, f'/Badge/Materials/{name}')
    sh = UsdShade.Shader.Define(stage, f'/Badge/Materials/{name}/Surface')
    sh.CreateIdAttr('UsdPreviewSurface')
    sh.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
    sh.CreateInput('metallic', Sdf.ValueTypeNames.Float).Set(metallic)
    sh.CreateInput('opacity', Sdf.ValueTypeNames.Float).Set(1.0)
    r = sh.CreateInput('roughness', Sdf.ValueTypeNames.Float)
    r.Set(rough)
    if rough_file:
        st = UsdShade.Shader.Define(stage, f'/Badge/Materials/{name}/BandUV')
        st.CreateIdAttr('UsdPrimvarReader_float2')
        st.CreateInput('varname', Sdf.ValueTypeNames.String).Set('st')
        tx = UsdShade.Shader.Define(stage, f'/Badge/Materials/{name}/Brush')
        tx.CreateIdAttr('UsdUVTexture')
        tx.CreateInput('file', Sdf.ValueTypeNames.Asset).Set('textures/' + os.path.basename(rough_file))
        tx.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(st.ConnectableAPI(), 'result')
        tx.CreateInput('wrapS', Sdf.ValueTypeNames.Token).Set('repeat')
        tx.CreateInput('wrapT', Sdf.ValueTypeNames.Token).Set('clamp')
        tx.CreateInput('sourceColorSpace', Sdf.ValueTypeNames.Token).Set('raw')
        tx.CreateOutput('r', Sdf.ValueTypeNames.Float)
        r.ConnectToSource(tx.ConnectableAPI(), 'r')
    m.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(), 'surface')
    return m

gold = preview('RubyHeart_Gold', gold_color, 1.0, 0.30, rough_tex)
ruby = preview('CrestGem_HeartFoil', (0.55, 0.01, 0.08), 0.0, 0.05)

def mesh(path, V, N, T, mat, uv=None):
    m = UsdGeom.Mesh.Define(stage, path)
    m.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(V.astype(np.float32)))
    m.CreateFaceVertexCountsAttr(Vt.IntArray([3] * len(T)))
    m.CreateFaceVertexIndicesAttr(Vt.IntArray(T.astype(np.int32).ravel().tolist()))
    m.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(N.astype(np.float32)))
    m.SetNormalsInterpolation(UsdGeom.Tokens.vertex)
    m.CreateSubdivisionSchemeAttr('none')
    m.CreateDoubleSidedAttr(False)
    lo, hi = V.min(0), V.max(0)
    m.CreateExtentAttr(Vt.Vec3fArray([Gf.Vec3f(*lo.tolist()), Gf.Vec3f(*hi.tolist())]))
    if uv is not None:
        pv = UsdGeom.PrimvarsAPI(m).CreatePrimvar('st', Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.vertex)
        pv.Set(Vt.Vec2fArray.FromNumpy(uv.astype(np.float32)))
    UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(mat)
    return m

mesh('/Badge/Frame', d['frame_v'], d['frame_n'], d['frame_t'], gold, d['frame_uv'])
mesh('/Badge/Gem', d['gem_v'], d['gem_n'], d['gem_t'], ruby)
stage.GetRootLayer().Save()
if rough_tex:
    os.makedirs(os.path.join(tmp, 'textures'), exist_ok=True)
    shutil.copy(rough_tex, os.path.join(tmp, 'textures', os.path.basename(rough_tex)))
cwd = os.getcwd(); os.chdir(tmp)
ok = UsdUtils.CreateNewARKitUsdzPackage(Sdf.AssetPath('ruby_heart.usdc'), os.path.abspath(os.path.join(cwd, out)) if not os.path.isabs(out) else out)
os.chdir(cwd)
print('usdz written', ok, out, os.path.getsize(out))
