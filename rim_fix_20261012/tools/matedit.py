"""matedit.py <in.usdz> <out.usdz> <spec.json> : material edits. spec = {"MaterialName": {"like": "SourceMaterialName",
"diffuse_scale": 0.8, "emissive_scale": 1.5, "roughness": 0.45}, "Other": {"diffuse": [r,g,b], "roughness": 0.5}, ...}
"like" makes the material read the source material's color/emissive textures (same UV primvar) with the given scales.
Optional "files": {"old": "new"} in the spec root remaps texture files (new files must be in the package folder given by "dir")."""
import sys, os, json, shutil, subprocess, zipfile, tempfile
from pxr import Usd, UsdShade, Sdf, Gf
def compact_usdc(path):
    """Re-save with Apple's usdcat: its crate writer packs float arrays (Blender's does not; 2.8 MB vs 5.4 MB)."""
    if not path.endswith('.usdc'): return
    tmp = path[:-5] + '_compact.usdc'; subprocess.run(['/usr/bin/usdcat', path, '-o', tmp], check=True); os.replace(tmp, path)
src, dst, spec = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
work = tempfile.mkdtemp(prefix='matedit_'); names = zipfile.ZipFile(src).namelist(); zipfile.ZipFile(src).extractall(work)
root = os.path.join(work, names[0]); st = Usd.Stage.Open(root)
mats = {p.GetName(): UsdShade.Material(p) for p in st.Traverse() if p.IsA(UsdShade.Material)}
def surface(m): return UsdShade.Shader(m.GetPrim().GetChild('Surface'))
def tex_node(m, inp):
    i = surface(m).GetInput(inp)
    if i and i.HasConnectedSource(): return UsdShade.Shader(i.GetConnectedSources()[0][0].source.GetPrim())
for name, s in spec.items():
    if name in ('files', 'dir', 'extra_files'): continue
    m = mats[name]; surf = surface(m); mp = m.GetPrim().GetPath()
    if 'like' in s:
        srcm = mats[s['like']]
        uvsrc = tex_node(srcm, 'diffuseColor').GetInput('st').GetConnectedSources()[0][0].source.GetPrim()
        uvr = UsdShade.Shader.Define(st, mp.AppendChild('UV')); uvr.CreateIdAttr('UsdPrimvarReader_float2')
        uvr.CreateInput('varname', Sdf.ValueTypeNames.String).Set(UsdShade.Shader(uvsrc).GetInput('varname').Get())
        uvout = uvr.CreateOutput('result', Sdf.ValueTypeNames.Float2)
        for inp, key in (('diffuseColor', 'diffuse_scale'), ('emissiveColor', 'emissive_scale')):
            sn = tex_node(srcm, inp)
            i = surf.GetInput(inp) or surf.CreateInput(inp, Sdf.ValueTypeNames.Color3f)
            if i.HasConnectedSource(): i.DisconnectSource()
            if sn is None or s.get(key, 1) == 0:
                surf.CreateInput(inp, Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0, 0, 0)); continue
            t = UsdShade.Shader.Define(st, mp.AppendChild(inp)); t.CreateIdAttr('UsdUVTexture')
            t.CreateInput('file', Sdf.ValueTypeNames.Asset).Set(sn.GetInput('file').Get().path)
            t.CreateInput('sourceColorSpace', Sdf.ValueTypeNames.Token).Set('sRGB')
            for w in ('wrapS', 'wrapT'): t.CreateInput(w, Sdf.ValueTypeNames.Token).Set('clamp')
            t.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(uvout)
            base = sn.GetInput('scale').Get() if sn.GetInput('scale') else Gf.Vec4f(1, 1, 1, 1)
            k = s.get(key, 1.0); t.CreateInput('scale', Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(base[0] * k, base[1] * k, base[2] * k, 1))
            out = t.CreateOutput('rgb', Sdf.ValueTypeNames.Float3)
            surf.CreateInput(inp, Sdf.ValueTypeNames.Color3f).ConnectToSource(out)
    if 'diffuse' in s:
        i = surf.GetInput('diffuseColor')
        if i and i.HasConnectedSource(): i.DisconnectSource()
        surf.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*s['diffuse']))
    if 'roughness' in s: surf.CreateInput('roughness', Sdf.ValueTypeNames.Float).Set(float(s['roughness']))
    if 'roughness_map' in s:   # grayscale PNG (raw), read through the same UV primvar as the material's color texture
        srcm = mats[s.get('like', name)]; si_ = tex_node(srcm, 'diffuseColor').GetInput('st').GetConnectedSources()[0][0]; uvsrc = si_.source.GetOutput(si_.sourceName)
        t = UsdShade.Shader.Define(st, mp.AppendChild('roughnessMap')); t.CreateIdAttr('UsdUVTexture')
        t.CreateInput('file', Sdf.ValueTypeNames.Asset).Set(s['roughness_map'])
        t.CreateInput('sourceColorSpace', Sdf.ValueTypeNames.Token).Set('raw')
        for w_ in ('wrapS', 'wrapT'): t.CreateInput(w_, Sdf.ValueTypeNames.Token).Set('clamp')
        t.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(uvsrc)
        out = t.CreateOutput('r', Sdf.ValueTypeNames.Float)
        ri = surf.GetInput('roughness') or surf.CreateInput('roughness', Sdf.ValueTypeNames.Float)
        surf.CreateInput('roughness', Sdf.ValueTypeNames.Float).ConnectToSource(out)
    if 'metallic' in s: surf.CreateInput('metallic', Sdf.ValueTypeNames.Float).Set(float(s['metallic']))
st.GetRootLayer().Save()
compact_usdc(st.GetRootLayer().realPath)
for f in spec.get('extra_files', []):
    shutil.copy(os.path.join(spec['dir'], f), os.path.join(work, f))
    if f not in names: names.append(f)
os.path.exists(dst) and os.remove(dst)
subprocess.run(['usdzip', dst] + names, cwd=work, check=True, stdout=subprocess.DEVNULL)
r = subprocess.run(['usdchecker', '--arkit', dst], capture_output=True, text=True)
print(os.path.basename(dst), os.path.getsize(dst), 'arkit', 'OK' if 'Success' in r.stdout + r.stderr else (r.stdout + r.stderr)[-500:])
