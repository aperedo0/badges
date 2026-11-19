"""Write the app's USDZ from the built pieces. Run with Blender's Python (it has the USD library).
Usage: pack.py candidateNN
"""
from pathlib import Path
import json, subprocess, shutil, tempfile, hashlib, sys
import numpy as np
from pxr import Usd, UsdGeom, UsdShade, Sdf, Vt, Gf
R = Path(__file__).resolve().parent; C = R / sys.argv[1]
D = np.load(C / 'geometry.npz'); meta = json.loads((C / 'parts.json').read_text()); art = json.loads((C / 'textures/art.json').read_text())
MATS = json.loads((C / 'materials.json').read_text()) if (C / 'materials.json').exists() else {
    'gold': dict(color=[.78, .33, .01], metallic=1.0, roughness=.32),
    'gold_side': dict(color=[.45, .21, .03], metallic=1.0, roughness=.5),
    'art': dict(color=[0, 0, 0], metallic=1.0, roughness=1.0),
    'art_bolt': dict(color=[0, 0, 0], metallic=1.0, roughness=1.0)}
(C / 'materials.json').write_text(json.dumps(MATS, indent=1) + '\n')
with tempfile.TemporaryDirectory(prefix='golden_storm_', dir='/tmp') as temp:
    pkg = Path(temp); (pkg / 'textures').mkdir()
    for name in ['art_emission.png', 'bolt_emission.png']:
        shutil.copyfile(C / 'textures' / name, pkg / 'textures' / name)
    stage = Usd.Stage.CreateNew(str(pkg / 'badge.usdc')); root = UsdGeom.Xform.Define(stage, '/GoldenStorm'); stage.SetDefaultPrim(root.GetPrim())
    UsdGeom.SetStageUpAxis(stage, 'Y'); UsdGeom.SetStageMetersPerUnit(stage, 1.)
    mats = {}
    for role, spec in MATS.items():
        base = '/GoldenStorm/Materials/GoldenStorm_' + role
        mat = UsdShade.Material.Define(stage, base); sh = UsdShade.Shader.Define(stage, base + '/Surface'); sh.CreateIdAttr('UsdPreviewSurface')
        for key, value in [('metallic', spec['metallic']), ('roughness', spec['roughness']), ('ior', 1.46), ('opacity', 1.)]:
            sh.CreateInput(key, Sdf.ValueTypeNames.Float).Set(float(value))
        sh.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).Set(tuple(spec['color']))
        sh.CreateOutput('surface', Sdf.ValueTypeNames.Token); mat.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(), 'surface')
        if role in ('art', 'art_bolt'):
            rd = UsdShade.Shader.Define(stage, base + '/UV'); rd.CreateIdAttr('UsdPrimvarReader_float2')
            rd.CreateInput('varname', Sdf.ValueTypeNames.String).Set('StormUV'); rd.CreateOutput('result', Sdf.ValueTypeNames.Float2)
            for suffix, param in [('emission', 'emissiveColor')]:        # the enamel reflects nothing: its color is all glow
                tex = UsdShade.Shader.Define(stage, base + '/' + suffix); tex.CreateIdAttr('UsdUVTexture')
                tex.CreateInput('file', Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/' + ('bolt_' if role == 'art_bolt' else 'art_') + suffix + '.png'))
                tex.CreateInput('sourceColorSpace', Sdf.ValueTypeNames.Token).Set('raw' if role == 'art_bolt' else 'sRGB')
                tex.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(rd.ConnectableAPI(), 'result')
                tex.CreateInput('wrapS', Sdf.ValueTypeNames.Token).Set('clamp'); tex.CreateInput('wrapT', Sdf.ValueTypeNames.Token).Set('clamp')
                if suffix == 'emission':
                    e = float(art['bolt_scale'] if role == 'art_bolt' else art['emission_scale']); tex.CreateInput('scale', Sdf.ValueTypeNames.Float4).Set((e, e, e, 1))
                tex.CreateOutput('rgb', Sdf.ValueTypeNames.Float3)
                sh.CreateInput(param, Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.ConnectableAPI(), 'rgb')
        mats[role] = mat
    allp = []; count = 0
    for i, part in enumerate(meta['parts']):
        v = D[f'{i}_v']; n = D[f'{i}_n']; uv = D[f'{i}_uv']; t = D[f'{i}_t']
        mesh = UsdGeom.Mesh.Define(stage, f'/GoldenStorm/Part_{i}'); mesh.GetPrim().SetDisplayName(part['name'])
        mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(v)); mesh.CreateFaceVertexCountsAttr([3] * len(t)); mesh.CreateFaceVertexIndicesAttr(t.ravel().tolist())
        mesh.CreateSubdivisionSchemeAttr('none'); mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(n)); mesh.SetNormalsInterpolation('vertex')
        if part['role'] in ('art', 'art_bolt'):
            UsdGeom.PrimvarsAPI(mesh).CreatePrimvar('StormUV', Sdf.ValueTypeNames.TexCoord2fArray, 'vertex').Set(Vt.Vec2fArray.FromNumpy(uv))
        mesh.CreateExtentAttr([Gf.Vec3f(*map(float, v.min(0))), Gf.Vec3f(*map(float, v.max(0)))])
        UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mats[part['role']]); allp.append(v); count += len(t)
    stage.GetRootLayer().Save(); out = C / 'model.usdz'
    if out.exists():
        out.unlink()
    subprocess.run(['/usr/bin/usdzip', str(out), 'badge.usdc', 'textures/art_emission.png', 'textures/bolt_emission.png'], cwd=pkg, check=True, capture_output=True)
    chk = subprocess.run(['/usr/bin/usdchecker', '--arkit', str(out)], capture_output=True, text=True); (C / 'usdchecker.txt').write_text(chk.stdout + chk.stderr)
    p = np.vstack(allp)
    ok = p[:, 1].min() >= -2.4551 and p[:, 1].max() <= 3.0151 and abs(p[:, 0]).max() < 3.35 and abs(p[:, 2].max() + p[:, 2].min()) < 1e-3
    res = dict(triangles=count, megabytes=round(out.stat().st_size / 1e6, 2), sha256=hashlib.sha256(out.read_bytes()).hexdigest(), bounds_min=np.round(p.min(0), 4).tolist(),
               bounds_max=np.round(p.max(0), 4).tolist(), fits_frame=bool(ok), arkit_valid=chk.returncode == 0)
    (C / 'validation.json').write_text(json.dumps(res, indent=1) + '\n'); print(json.dumps(res, indent=1))
    if chk.returncode:
        print(chk.stdout[-1500:], chk.stderr[-1500:])
