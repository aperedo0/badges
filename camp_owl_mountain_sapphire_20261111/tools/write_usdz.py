"""Write a badge built by badge3d.py as a USDZ. Run with Blender's bundled Python (it has pxr).

Usage: write_usdz.py CAND_DIR PALETTE.json PREFIX   (textures named in the palette are relative to the palette's folder)
One mesh per part, material subsets, per corner (face varying) normals and UVs, no rescaling, the gem's foil
axis in its first UV set, output CAND_DIR/model.usdz.
"""
import sys, os, json, shutil, tempfile
import numpy as np
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Vt, UsdUtils
CAND = os.path.abspath(sys.argv[1]); PALP = os.path.abspath(sys.argv[2]); PREFIX = sys.argv[3]; ROOT = os.path.dirname(PALP)
D = np.load(os.path.join(CAND, 'parts.npz')); META = json.load(open(os.path.join(CAND, 'parts.json'))); PAL = json.load(open(PALP))
tmp = tempfile.mkdtemp(); path = os.path.join(tmp, 'badge.usdc')
stage = Usd.Stage.CreateNew(path)
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y); UsdGeom.SetStageMetersPerUnit(stage, 1.0)
root = UsdGeom.Xform.Define(stage, '/Badge'); stage.SetDefaultPrim(root.GetPrim())
UsdGeom.Scope.Define(stage, '/Badge/Materials')
mats = {}


def material(name):
    if name in mats:
        return mats[name]
    full = PAL.get(name, {}).get('material_name', 'CrestGem_SapphireClear') if name == 'Gem' else PREFIX + '_' + name
    m = UsdShade.Material.Define(stage, f'/Badge/Materials/{full}')
    sh = UsdShade.Shader.Define(stage, f'/Badge/Materials/{full}/Surface'); sh.CreateIdAttr('UsdPreviewSurface')
    p = PAL.get(name, {})
    dif = sh.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f)
    if name == 'Gem':
        dif.Set(Gf.Vec3f(0.1, 0.55, 0.9)); sh.CreateInput('roughness', Sdf.ValueTypeNames.Float).Set(0.05)
        sh.CreateInput('metallic', Sdf.ValueTypeNames.Float).Set(0.0)
    elif 'emission_texture' in p:
        # enamel by the approved method (Tidal Compass, Emerald Trophy): metallic with a near black color, so the studio
        # adds no pale reflection, and the mockup's color in the emission, solved through the app's AgX (enamel_fill.py)
        st = UsdShade.Shader.Define(stage, f'/Badge/Materials/{full}/UV'); st.CreateIdAttr('UsdPrimvarReader_float2')
        st.CreateInput('varname', Sdf.ValueTypeNames.String).Set('st')
        for key, param, scale in (('color_texture', 'diffuseColor', None), ('emission_texture', 'emissiveColor', p.get('emission_scale', 8.0))):
            t = UsdShade.Shader.Define(stage, f'/Badge/Materials/{full}/{param}Map'); t.CreateIdAttr('UsdUVTexture')
            t.CreateInput('file', Sdf.ValueTypeNames.Asset).Set(p[key])
            t.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(st.ConnectableAPI(), 'result')
            t.CreateInput('sourceColorSpace', Sdf.ValueTypeNames.Token).Set('sRGB')
            t.CreateInput('wrapS', Sdf.ValueTypeNames.Token).Set('clamp'); t.CreateInput('wrapT', Sdf.ValueTypeNames.Token).Set('clamp')
            if scale:
                t.CreateInput('scale', Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(scale, scale, scale, 1.0))
            t.CreateOutput('rgb', Sdf.ValueTypeNames.Float3)
            inp = dif if param == 'diffuseColor' else sh.CreateInput('emissiveColor', Sdf.ValueTypeNames.Color3f)
            inp.ConnectToSource(t.ConnectableAPI(), 'rgb')
        sh.CreateInput('roughness', Sdf.ValueTypeNames.Float).Set(p['roughness']); sh.CreateInput('metallic', Sdf.ValueTypeNames.Float).Set(p.get('enamel_metallic', 1.0))
    elif 'texture' in p:
        st = UsdShade.Shader.Define(stage, f'/Badge/Materials/{full}/UV'); st.CreateIdAttr('UsdPrimvarReader_float2')
        st.CreateInput('varname', Sdf.ValueTypeNames.String).Set('st')
        t = UsdShade.Shader.Define(stage, f'/Badge/Materials/{full}/ColorMap'); t.CreateIdAttr('UsdUVTexture')
        t.CreateInput('file', Sdf.ValueTypeNames.Asset).Set(p['texture'])
        t.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(st.ConnectableAPI(), 'result')
        t.CreateInput('sourceColorSpace', Sdf.ValueTypeNames.Token).Set('sRGB')
        t.CreateInput('wrapS', Sdf.ValueTypeNames.Token).Set('clamp'); t.CreateInput('wrapT', Sdf.ValueTypeNames.Token).Set('clamp')
        t.CreateOutput('rgb', Sdf.ValueTypeNames.Float3)
        dif.ConnectToSource(t.ConnectableAPI(), 'rgb')
        sh.CreateInput('roughness', Sdf.ValueTypeNames.Float).Set(p['roughness']); sh.CreateInput('metallic', Sdf.ValueTypeNames.Float).Set(0.0)
    else:
        if 'albedo' not in p:
            raise SystemExit(f'palette has no color for material {name}')
        dif.Set(Gf.Vec3f(*p['albedo'])); sh.CreateInput('roughness', Sdf.ValueTypeNames.Float).Set(p.get('roughness', 0.2))
        sh.CreateInput('metallic', Sdf.ValueTypeNames.Float).Set(p.get('metallic', 0.0))
    if 'roughness_texture' in p:
        st = UsdShade.Shader.Define(stage, f'/Badge/Materials/{full}/BandUV'); st.CreateIdAttr('UsdPrimvarReader_float2')
        st.CreateInput('varname', Sdf.ValueTypeNames.String).Set('st')
        tx = UsdShade.Shader.Define(stage, f'/Badge/Materials/{full}/Brush'); tx.CreateIdAttr('UsdUVTexture')
        tx.CreateInput('file', Sdf.ValueTypeNames.Asset).Set(p['roughness_texture'])
        tx.CreateInput('sourceColorSpace', Sdf.ValueTypeNames.Token).Set('raw')
        if 'roughness_texture_scale' in p:
            scale=p['roughness_texture_scale']; bias=p.get('roughness_texture_bias',0.0)
            tx.CreateInput('scale',Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(scale,scale,scale,1.0))
            tx.CreateInput('bias',Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(bias,bias,bias,0.0))
        tx.CreateInput('wrapS', Sdf.ValueTypeNames.Token).Set('repeat'); tx.CreateInput('wrapT', Sdf.ValueTypeNames.Token).Set('clamp')
        tx.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(st.ConnectableAPI(), 'result')
        tx.CreateOutput('r', Sdf.ValueTypeNames.Float)
        sh.GetInput('roughness').ConnectToSource(tx.ConnectableAPI(), 'r')
    sh.CreateInput('opacity', Sdf.ValueTypeNames.Float).Set(1.0)
    m.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(), 'surface')
    mats[name] = m; return m


total = 0
for part in META['parts']:
    name = part['name']; V = D[name + '_v'].reshape(-1, 3).astype(np.float64); N = D[name + '_n'].reshape(-1, 3); UV = D[name + '_uv'].reshape(-1, 2); M = D[name + '_m']
    key = V.astype(np.float32); uniq, inv = np.unique(key, axis=0, return_inverse=True)
    prim = 'Gem' if name == 'gem' else ''.join(w.capitalize() for w in name.split('_'))
    mesh = UsdGeom.Mesh.Define(stage, f'/Badge/{prim}')
    mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(uniq.astype(np.float32)))
    mesh.CreateFaceVertexCountsAttr(Vt.IntArray([3] * (len(inv) // 3)))
    mesh.CreateFaceVertexIndicesAttr(Vt.IntArray(inv.astype(np.int32).tolist()))
    mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(N.astype(np.float32))); mesh.SetNormalsInterpolation(UsdGeom.Tokens.faceVarying)
    mesh.CreateSubdivisionSchemeAttr('none'); mesh.CreateDoubleSidedAttr(False)
    mesh.CreateExtentAttr(Vt.Vec3fArray([Gf.Vec3f(*uniq.min(0).tolist()), Gf.Vec3f(*uniq.max(0).tolist())]))
    pv = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar('st', Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.faceVarying)
    pv.Set(Vt.Vec2fArray.FromNumpy(UV.astype(np.float32)))
    names = part['materials']
    if len(names) == 1:
        UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(material(names[0]))
    else:
        api = UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim())
        for k, mn in enumerate(names):
            faces = np.nonzero(M == k)[0]
            if len(faces) == 0:
                continue
            sub = UsdGeom.Subset.CreateGeomSubset(mesh, mn, UsdGeom.Tokens.face, Vt.IntArray(faces.astype(np.int32).tolist()), 'materialBind', UsdGeom.Tokens.nonOverlapping)
            UsdShade.MaterialBindingAPI.Apply(sub.GetPrim()).Bind(material(mn))
    total += len(inv) // 3
stage.GetRootLayer().Save()
os.makedirs(os.path.join(tmp, 'textures'), exist_ok=True)
for v in PAL.values():
    for key in ('texture', 'color_texture', 'emission_texture', 'roughness_texture'):
        if isinstance(v, dict) and key in v:
            os.makedirs(os.path.dirname(os.path.join(tmp, v[key])), exist_ok=True); shutil.copy(os.path.join(ROOT, v[key]), os.path.join(tmp, v[key]))
out = os.path.join(CAND, 'model.usdz'); cwd = os.getcwd(); os.chdir(tmp)
ok = UsdUtils.CreateNewARKitUsdzPackage(Sdf.AssetPath('badge.usdc'), out); os.chdir(cwd)
print('usdz', ok, round(os.path.getsize(out) / 1e6, 2), 'MB', total, 'triangles')
