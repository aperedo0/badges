"""Write an enamel badge USDZ (Blender's Python for pxr). Usage: write_badge_usdz.py BADGE_DIR GEOM.npz OUT.usdz PREFIX"""
import sys, os, shutil, tempfile
import numpy as np
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Vt, UsdUtils
D, geom, out, prefix = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3]), sys.argv[4]
d = dict(np.load(geom))
vs = [k for k in d if k.endswith('_v')]
lo = min(d[k][:, 1].min() for k in vs); hi = max(d[k][:, 1].max() for k in vs)
sc = (2.995 + 2.455) / (hi - lo)
for k in vs:
    v = d[k].copy(); v[:, 1] -= lo; v *= sc; v[:, 1] -= 2.455; d[k] = v
tmp = tempfile.mkdtemp(); path = os.path.join(tmp, 'badge.usdc')
stage = Usd.Stage.CreateNew(path)
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y); UsdGeom.SetStageMetersPerUnit(stage, 1.0)
root = UsdGeom.Xform.Define(stage, '/Badge'); stage.SetDefaultPrim(root.GetPrim())
UsdGeom.Scope.Define(stage, '/Badge/Materials')
def tex(name, inp, f, st, out_name, cs):
    t = UsdShade.Shader.Define(stage, f'/Badge/Materials/{name}/{inp}Map'); t.CreateIdAttr('UsdUVTexture')
    t.CreateInput('file', Sdf.ValueTypeNames.Asset).Set('textures/' + f)
    t.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(st.ConnectableAPI(), 'result')
    t.CreateInput('wrapS', Sdf.ValueTypeNames.Token).Set('clamp'); t.CreateInput('wrapT', Sdf.ValueTypeNames.Token).Set('clamp')
    t.CreateInput('sourceColorSpace', Sdf.ValueTypeNames.Token).Set(cs)
    t.CreateOutput(out_name, Sdf.ValueTypeNames.Float3 if out_name == 'rgb' else Sdf.ValueTypeNames.Float)
    return t
def mesh(key, mat):
    V, N, T = d[key + '_v'], d[key + '_n'], d[key + '_t']
    m = UsdGeom.Mesh.Define(stage, f'/Badge/{key.capitalize()}')
    m.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(V.astype(np.float32)))
    m.CreateFaceVertexCountsAttr(Vt.IntArray([3] * len(T)))
    m.CreateFaceVertexIndicesAttr(Vt.IntArray(T.astype(np.int32).ravel().tolist()))
    m.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(N.astype(np.float32))); m.SetNormalsInterpolation(UsdGeom.Tokens.vertex)
    m.CreateSubdivisionSchemeAttr('none'); m.CreateDoubleSidedAttr(False)
    m.CreateExtentAttr(Vt.Vec3fArray([Gf.Vec3f(*V.min(0).tolist()), Gf.Vec3f(*V.max(0).tolist())]))
    uv = d[key + '_uv']
    pv = UsdGeom.PrimvarsAPI(m).CreatePrimvar('st', Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.vertex)
    pv.Set(Vt.Vec2fArray.FromNumpy(uv.astype(np.float32)))
    UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(mat)
name = prefix + '_Enamel'
mat = UsdShade.Material.Define(stage, f'/Badge/Materials/{name}')
sh = UsdShade.Shader.Define(stage, f'/Badge/Materials/{name}/Surface'); sh.CreateIdAttr('UsdPreviewSurface')
diff = sh.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f); diff.Set(Gf.Vec3f(0.8, 0.6, 0.3))
met = sh.CreateInput('metallic', Sdf.ValueTypeNames.Float); met.Set(0.0)
rou = sh.CreateInput('roughness', Sdf.ValueTypeNames.Float); rou.Set(0.2)
sh.CreateInput('opacity', Sdf.ValueTypeNames.Float).Set(1.0)
st = UsdShade.Shader.Define(stage, f'/Badge/Materials/{name}/UV'); st.CreateIdAttr('UsdPrimvarReader_float2')
st.CreateInput('varname', Sdf.ValueTypeNames.String).Set('st')
diff.ConnectToSource(tex(name, 'Color', 'badge_color.png', st, 'rgb', 'sRGB').ConnectableAPI(), 'rgb')
met.ConnectToSource(tex(name, 'Metal', 'badge_metal.png', st, 'r', 'raw').ConnectableAPI(), 'r')
rou.ConnectToSource(tex(name, 'Rough', 'badge_rough.png', st, 'r', 'raw').ConnectableAPI(), 'r')
emi_in = sh.CreateInput('emissiveColor', Sdf.ValueTypeNames.Color3f)
emi_in.ConnectToSource(tex(name, 'Glow', 'badge_emissive.png', st, 'rgb', 'raw').ConnectableAPI(), 'rgb')
mat.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(), 'surface')
mesh('badge', mat)
if 'gem_v' in d:
    gm = UsdShade.Material.Define(stage, '/Badge/Materials/CrestGem_FoilSapphire')
    gs = UsdShade.Shader.Define(stage, '/Badge/Materials/CrestGem_FoilSapphire/Surface'); gs.CreateIdAttr('UsdPreviewSurface')
    gs.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0.1, 0.55, 0.9))
    gs.CreateInput('roughness', Sdf.ValueTypeNames.Float).Set(0.05); gs.CreateInput('metallic', Sdf.ValueTypeNames.Float).Set(0.0)
    gm.CreateSurfaceOutput().ConnectToSource(gs.ConnectableAPI(), 'surface')
    # foil axis per vertex in the first UV set: front faces +Z (0, 0.5), back faces -Z (0.5, 0.5)
    d['gem_uv'] = np.where((d['gem_v'][:, 2] >= 0)[:, None], [[0.0, 0.5]], [[0.5, 0.5]])
    mesh('gem', gm)
stage.GetRootLayer().Save()
os.makedirs(os.path.join(tmp, 'textures'), exist_ok=True)
for f in ('badge_color.png', 'badge_metal.png', 'badge_rough.png', 'badge_emissive.png'):
    shutil.copy(os.path.join(D, 'textures', f), os.path.join(tmp, 'textures', f))
cwd = os.getcwd(); os.chdir(tmp)
ok = UsdUtils.CreateNewARKitUsdzPackage(Sdf.AssetPath('badge.usdc'), out); os.chdir(cwd)
allv = np.vstack([d[k] for k in vs])
print('usdz', ok, os.path.getsize(out), 'bounds', allv.min(0).round(3).tolist(), allv.max(0).round(3).tolist())
