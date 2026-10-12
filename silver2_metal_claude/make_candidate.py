"""make_candidate.py <name> <albedo.npz | const:VALUE> [emissive.npz | const:VALUE] : writes star color atlases into a copy of candidate 33 and packs <name>/silver2_badge_mobile.usdz.
albedo.npz holds 'planes' -> array (10,128,128,3) of linear albedo per plane cell."""
import sys, shutil, subprocess, numpy as np
from PIL import Image
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from common import *
name, source = sys.argv[1], sys.argv[2]
out = W / name; pkg = out / 'pkg'
if pkg.exists(): shutil.rmtree(pkg)
shutil.copytree(W / 'src/c33x', pkg)
if source.startswith('const:'):
    planes = np.ones((10, CELL, CELL, 3)) * float(source.split(':')[1])
else:
    planes = np.load(source)['planes']
for mat in ['Silver2_StarLit_Satin', 'Silver2_StarShaded_Satin']:
    path = pkg / '0' / f'{mat}_color.png'
    atlas = np.asarray(Image.open(path).convert('RGB')).copy()
    for p in range(10):
        rs, cs = cell_slice(p)
        atlas[rs, cs] = np.uint8(np.clip(srgb_encode(planes[p]), 0, 1) * 255 + .5)
    Image.fromarray(atlas).save(path)
if len(sys.argv) > 3:
    esrc = sys.argv[3]
    emis = np.ones((10, CELL, CELL, 3)) * float(esrc.split(':')[1]) if esrc.startswith('const:') else np.load(esrc)['planes']
    for mat in ['Silver2_StarLit_Satin', 'Silver2_StarShaded_Satin']:
        atlas = np.zeros((SIZE, SIZE, 3), np.uint8)
        for p in range(10):
            rs, cs = cell_slice(p)
            atlas[rs, cs] = np.uint8(np.clip(srgb_encode(emis[p]), 0, 1) * 255 + .5)
        Image.fromarray(atlas).save(pkg / '0' / f'{mat}_emissive.png')
    subprocess.run(['/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13', str(W / 'add_emissive.py'), str(pkg / 'silver2_badge_mobile.usdc')], check=True)
usdz = out / 'silver2_badge_mobile.usdz'
usdz.unlink(missing_ok=True)
files = ['silver2_badge_mobile.usdc'] + sorted(f'0/{f.name}' for f in (pkg / '0').iterdir())
subprocess.run(['usdzip', str(usdz)] + files, cwd=pkg, check=True, stdout=subprocess.DEVNULL)
r = subprocess.run(['usdchecker', '--arkit', str(usdz)], capture_output=True, text=True)
print(name, 'usdchecker:', (r.stdout + r.stderr).strip().splitlines()[-1])
