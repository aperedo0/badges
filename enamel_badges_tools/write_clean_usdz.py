"""Write a clean enamel badge (separate gold, enamel, side wall and gem parts) as a USDZ. Run with Blender's Python.

Usage: write_clean_usdz.py PARTS.npz TEXTURE_DIR OUT.usdz PREFIX
"""
import sys, os, shutil, tempfile
import numpy as np
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Vt, UsdUtils

parts_path, texdir, out, prefix = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3]), sys.argv[4]
d = dict(np.load(parts_path))
keys = [k[:-2] for k in d if k.endswith('_v')]
lo = min(d[k + '_v'][:, 1].min() for k in keys); hi = max(d[k + '_v'][:, 1].max() for k in keys)
sc = (2.995 + 2.455) / (hi - lo)
for k in keys:
    v = d[k + '_v'].copy(); v[:, 1] -= lo; v *= sc; v[:, 1] -= 2.455; d[k + '_v'] = v
tmp = tempfile.mkdtemp(); path = os.path.join(tmp, 'badge.usdc')
stage = Usd.Stage.CreateNew(path)
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y); UsdGeom.SetStageMetersPerUnit(stage, 1.0)
root = UsdGeom.Xform.Define(stage, '/Badge'); stage.SetDefaultPrim(root.GetPrim())
UsdGeom.Scope.Define(stage, '/Badge/Materials')


def surface(name, color, metal, rough):
    mat = UsdShade.Material.Define(stage, f'/Badge/Materials/{name}')
    sh = UsdShade.Shader.Define(stage, f'/Badge/Materials/{name}/Surface'); sh.CreateIdAttr('UsdPreviewSurface')
    ins = {'diffuseColor': sh.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f),
           'metallic': sh.CreateInput('metallic', Sdf.ValueTypeNames.Float),
           'roughness': sh.CreateInput('roughness', Sdf.ValueTypeNames.Float)}
    ins['diffuseColor'].Set(Gf.Vec3f(*color)); ins['metallic'].Set(metal); ins['roughness'].Set(rough)
    sh.CreateInput('opacity', Sdf.ValueTypeNames.Float).Set(1.0)
    mat.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(), 'surface')
    return mat, sh, ins


def texture(matname, label, fname, st, out_name, cs):
    t = UsdShade.Shader.Define(stage, f'/Badge/Materials/{matname}/{label}'); t.CreateIdAttr('UsdUVTexture')
    t.CreateInput('file', Sdf.ValueTypeNames.Asset).Set('textures/' + fname)
    t.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(st.ConnectableAPI(), 'result')
    t.CreateInput('wrapS', Sdf.ValueTypeNames.Token).Set('clamp'); t.CreateInput('wrapT', Sdf.ValueTypeNames.Token).Set('clamp')
    t.CreateInput('sourceColorSpace', Sdf.ValueTypeNames.Token).Set(cs)
    t.CreateOutput(out_name, Sdf.ValueTypeNames.Float3 if out_name == 'rgb' else Sdf.ValueTypeNames.Float)
    return t


def mesh(key, prim, mat):
    V, N, T, UV = d[key + '_v'], d[key + '_n'], d[key + '_t'], d[key + '_uv']
    m = UsdGeom.Mesh.Define(stage, f'/Badge/{prim}')
    m.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(V.astype(np.float32)))
    m.CreateFaceVertexCountsAttr(Vt.IntArray([3] * len(T)))
    m.CreateFaceVertexIndicesAttr(Vt.IntArray(T.astype(np.int32).ravel().tolist()))
    m.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(N.astype(np.float32))); m.SetNormalsInterpolation(UsdGeom.Tokens.vertex)
    m.CreateSubdivisionSchemeAttr('none'); m.CreateDoubleSidedAttr(False)
    m.CreateExtentAttr(Vt.Vec3fArray([Gf.Vec3f(*V.min(0).tolist()), Gf.Vec3f(*V.max(0).tolist())]))
    pv = UsdGeom.PrimvarsAPI(m).CreatePrimvar('st', Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.vertex)
    pv.Set(Vt.Vec2fArray.FromNumpy(UV.astype(np.float32)))
    UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(mat)


GOLD = (0.70, 0.31, 0.0)
mesh('gold', 'Gold', surface(prefix + '_Gold', GOLD, 1.0, 0.26)[0])
mesh('side', 'SideWall', surface(prefix + '_Side', GOLD, 1.0, 0.5)[0])
name = prefix + '_Enamel'
mat, sh, ins = surface(name, (0.8, 0.6, 0.3), 0.0, 0.2)
st = UsdShade.Shader.Define(stage, f'/Badge/Materials/{name}/UV'); st.CreateIdAttr('UsdPrimvarReader_float2')
st.CreateInput('varname', Sdf.ValueTypeNames.String).Set('st')
ins['diffuseColor'].ConnectToSource(texture(name, 'ColorMap', 'enamel_color.png', st, 'rgb', 'sRGB').ConnectableAPI(), 'rgb')
ins['roughness'].ConnectToSource(texture(name, 'RoughMap', 'enamel_rough.png', st, 'r', 'raw').ConnectableAPI(), 'r')
emi = sh.CreateInput('emissiveColor', Sdf.ValueTypeNames.Color3f)
emi.ConnectToSource(texture(name, 'GlowMap', 'enamel_glow.png', st, 'rgb', 'raw').ConnectableAPI(), 'rgb')
mesh('enamel', 'Enamel', mat)
if 'gem' in keys:
    gm = surface('CrestGem_FoilSapphire', (0.1, 0.55, 0.9), 0.0, 0.05)[0]
    d['gem_uv'] = np.where((d['gem_v'][:, 2] >= 0)[:, None], [[0.0, 0.5]], [[0.5, 0.5]])   # foil axis: front, back
    mesh('gem', 'Gem', gm)
stage.GetRootLayer().Save()
os.makedirs(os.path.join(tmp, 'textures'), exist_ok=True)
for f in ('enamel_color.png', 'enamel_rough.png', 'enamel_glow.png'):
    shutil.copy(os.path.join(texdir, f), os.path.join(tmp, 'textures', f))
cwd = os.getcwd(); os.chdir(tmp)
ok = UsdUtils.CreateNewARKitUsdzPackage(Sdf.AssetPath('badge.usdc'), out); os.chdir(cwd)
allv = np.vstack([d[k + '_v'] for k in keys])
print('usdz', ok, os.path.getsize(out), 'triangles', sum(len(d[k + '_t']) for k in keys),
      'bounds', allv.min(0).round(3).tolist(), allv.max(0).round(3).tolist())
