"""idvariant.py <in.usdz> <out_dir> : material ID render variant. Every UsdPreviewSurface gets black diffuse, metallic 0,
roughness 1 and a flat distinct emissive color (textures disconnected). Writes <out_dir>/id.usdz and prints the color table."""
import sys, os, shutil, subprocess, zipfile
from pxr import Usd, UsdShade, Sdf, Gf
src, out = sys.argv[1], sys.argv[2]
work = os.path.join(out, 'id_work'); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
names = zipfile.ZipFile(src).namelist(); zipfile.ZipFile(src).extractall(work)
root = os.path.join(work, names[0]); st = Usd.Stage.Open(root)
COLORS = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, .5, 0), (.5, 0, 1), (1, 1, 1), (0, .5, 0)]
k = 0
for p in st.Traverse():
    if p.IsA(UsdShade.Shader) and UsdShade.Shader(p).GetIdAttr().Get() == 'UsdPreviewSurface':
        s = UsdShade.Shader(p)
        for name in ('diffuseColor', 'emissiveColor', 'metallic', 'roughness', 'normal', 'occlusion', 'opacity'):
            i = s.GetInput(name)
            if i and i.HasConnectedSource(): i.DisconnectSource()
        s.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0, 0, 0))
        s.CreateInput('metallic', Sdf.ValueTypeNames.Float).Set(0.0)
        s.CreateInput('roughness', Sdf.ValueTypeNames.Float).Set(1.0)
        c = COLORS[k % len(COLORS)]; s.CreateInput('emissiveColor', Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*c))
        print(p.GetParent().GetName(), c); k += 1
st.GetRootLayer().Save()
dst = os.path.join(out, 'id.usdz'); os.path.exists(dst) and os.remove(dst)
subprocess.run(['usdzip', dst] + names, cwd=work, check=True, stdout=subprocess.DEVNULL)
r = subprocess.run(['usdchecker', '--arkit', dst], capture_output=True, text=True); print('arkit', 'OK' if 'Success' in r.stdout + r.stderr else r.stdout + r.stderr)
