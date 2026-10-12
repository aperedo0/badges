"""make2.py <name> <base_dir> : copies base, drops in <name>/tex/*.png, connects emissive for every *_emissive.png, packs <name>/silver2_badge_mobile.usdz."""
import sys, shutil, subprocess
from pathlib import Path
W = Path('/Users/antonioperedo/Desktop/badges/silver2_metal_claude'); name, base = sys.argv[1], W / sys.argv[2]
out = W / name; pkg = out / 'pkg'
if pkg.exists(): shutil.rmtree(pkg)
shutil.copytree(base, pkg)
mats = []
for f in sorted((out / 'tex').glob('*.png')):
    shutil.copy(f, pkg / '0' / f.name)
    if f.name.endswith('_emissive.png'): mats.append(f.name[:-len('_emissive.png')])
if mats:
    subprocess.run(['/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13', str(W / 'add_emissive.py'), str(pkg / 'silver2_badge_mobile.usdc')] + mats, check=True)
usdz = out / 'silver2_badge_mobile.usdz'; usdz.unlink(missing_ok=True)
files = ['silver2_badge_mobile.usdc'] + sorted(f'0/{f.name}' for f in (pkg / '0').iterdir())
subprocess.run(['usdzip', str(usdz)] + files, cwd=pkg, check=True, stdout=subprocess.DEVNULL)
r = subprocess.run(['usdchecker', '--arkit', str(usdz)], capture_output=True, text=True)
print(name, 'emissive on', mats, '| usdchecker:', 'Success' if 'Success!' in r.stdout + r.stderr else (r.stdout + r.stderr)[-300:])
