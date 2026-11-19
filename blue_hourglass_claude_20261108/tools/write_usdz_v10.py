"""Write the Blue Hourglass USDZ from a geometry npz (Blender's Python for pxr). Usage: write_usdz.py GEOM.npz OUT.usdz"""
import sys, os, shutil, tempfile
import numpy as np
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Vt, UsdUtils
HERE = os.path.dirname(os.path.abspath(__file__))
d = np.load(sys.argv[1]); out = os.path.abspath(sys.argv[2])
tmp = tempfile.mkdtemp(); path = os.path.join(tmp, 'blue_hourglass.usdc')
stage = Usd.Stage.CreateNew(path)
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y); UsdGeom.SetStageMetersPerUnit(stage, 1.0)
root = UsdGeom.Xform.Define(stage, '/Badge'); stage.SetDefaultPrim(root.GetPrim())
UsdGeom.Scope.Define(stage, '/Badge/Materials')
MATS = {  # key: material, mesh, color, metallic, roughness, texture, opacity, emissive
    'gold': ('BlueHourglass_Gold', 'Gold', (0.95, 0.52, 0.13), 1.0, 0.30, None, 1.0, None),
    'marble': ('BlueHourglass_BlackMarble', 'Marble', (0.02, 0.02, 0.025), 0.0, 0.20, 'marble_black.png', 1.0, None),
    'glass': ('CrestGem_HourglassGlass', 'Glass', (0.0, 0.0, 0.0), 0.0, 0.03, None, 0.22, None),
    'sand': ('BlueHourglass_Sand', 'Sand', (0.012, 0.045, 0.62), 0.0, 0.62, 'sand_grain.png', 1.0, None),
}
for key, (name, mesh_name, col, met, rough, tex, opa, emi) in MATS.items():
    if key + '_v' not in d.files: continue
    m = UsdShade.Material.Define(stage, f'/Badge/Materials/{name}')
    sh = UsdShade.Shader.Define(stage, f'/Badge/Materials/{name}/Surface'); sh.CreateIdAttr('UsdPreviewSurface')
    diff = sh.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f); diff.Set(Gf.Vec3f(*col))
    sh.CreateInput('metallic', Sdf.ValueTypeNames.Float).Set(met)
    sh.CreateInput('roughness', Sdf.ValueTypeNames.Float).Set(rough)
    sh.CreateInput('opacity', Sdf.ValueTypeNames.Float).Set(opa)
    if key == 'glass': sh.CreateInput('ior', Sdf.ValueTypeNames.Float).Set(1.5)
    if emi: sh.CreateInput('emissiveColor', Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*emi))
    V, N, T = d[key + '_v'], d[key + '_n'], d[key + '_t']
    uv = d[key + '_uv'] if key + '_uv' in d.files else None
    if tex and uv is None:
        uv = np.c_[V[:, 0] * 2.5 + 0.5, V[:, 1] * 2.5 + 0.5]   # planar front projection, finer grain
    if tex:
        st = UsdShade.Shader.Define(stage, f'/Badge/Materials/{name}/UV'); st.CreateIdAttr('UsdPrimvarReader_float2')
        st.CreateInput('varname', Sdf.ValueTypeNames.String).Set('st')
        tx = UsdShade.Shader.Define(stage, f'/Badge/Materials/{name}/Texture'); tx.CreateIdAttr('UsdUVTexture')
        tx.CreateInput('file', Sdf.ValueTypeNames.Asset).Set('textures/' + tex)
        tx.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(st.ConnectableAPI(), 'result')
        tx.CreateInput('wrapS', Sdf.ValueTypeNames.Token).Set('repeat'); tx.CreateInput('wrapT', Sdf.ValueTypeNames.Token).Set('repeat')
        tx.CreateInput('sourceColorSpace', Sdf.ValueTypeNames.Token).Set('sRGB')
        tx.CreateOutput('rgb', Sdf.ValueTypeNames.Float3)
        diff.ConnectToSource(tx.ConnectableAPI(), 'rgb')
    m.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(), 'surface')
    mesh = UsdGeom.Mesh.Define(stage, f'/Badge/{mesh_name}')
    mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(V.astype(np.float32)))
    mesh.CreateFaceVertexCountsAttr(Vt.IntArray([3] * len(T)))
    mesh.CreateFaceVertexIndicesAttr(Vt.IntArray(T.astype(np.int32).ravel().tolist()))
    mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(N.astype(np.float32))); mesh.SetNormalsInterpolation(UsdGeom.Tokens.vertex)
    mesh.CreateSubdivisionSchemeAttr('none'); mesh.CreateDoubleSidedAttr(False)
    mesh.CreateExtentAttr(Vt.Vec3fArray([Gf.Vec3f(*V.min(0).tolist()), Gf.Vec3f(*V.max(0).tolist())]))
    if uv is not None:
        pv = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar('st', Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.vertex)
        pv.Set(Vt.Vec2fArray.FromNumpy(uv.astype(np.float32)))
    UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(m)
stage.GetRootLayer().Save()
os.makedirs(os.path.join(tmp, 'textures'), exist_ok=True)
for f in ('marble_black.png', 'sand_grain.png'):
    shutil.copy(os.path.join(HERE, '..', 'textures', f), os.path.join(tmp, 'textures', f))
cwd = os.getcwd(); os.chdir(tmp)
ok = UsdUtils.CreateNewARKitUsdzPackage(Sdf.AssetPath('blue_hourglass.usdc'), out); os.chdir(cwd)
print('usdz written', ok, out, os.path.getsize(out))
