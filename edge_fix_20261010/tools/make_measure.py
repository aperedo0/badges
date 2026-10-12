"""make_measure.py <tier> calib|id : writes measure/<mode>/<tier>.usdz from orig/<tier>: every textured color map set to an even
albedo (calib 0.15, id 0.005) and every glow map black (calib) or pure green (id). Roughness maps and untextured materials unchanged."""
import sys, json, shutil, subprocess, numpy as np
from pathlib import Path
from PIL import Image
E = Path('/Users/antonioperedo/Desktop/badges/edge_fix_20261010'); t, mode = sys.argv[1], sys.argv[2]
info = json.loads(str(np.load(E / 'model' / f'{t}.npz')['info']))
D = E / 'measure' / mode / t
if D.exists(): shutil.rmtree(D)
shutil.copytree(E / 'orig' / t, D)
enc = lambda v: np.uint8(np.clip(np.where(np.array(v) <= .0031308, np.array(v) * 12.92, 1.055 * np.array(v, float) ** (1 / 2.4) - .055), 0, 1) * 255 + .5)
done = set()
for mat, mi in info.items():
    for kind, f in mi['files'].items():
        if f in done or kind not in ('diffuseColor', 'emissiveColor'): continue
        p = D / f; im = Image.open(p); size = im.size
        if kind == 'diffuseColor': val = [0.15] * 3 if mode == 'calib' else [0.005] * 3
        else: val = [0, 0, 0] if mode == 'calib' else [0, 1, 0]
        Image.fromarray(np.tile(enc(val), (size[1], size[0], 1))).convert(im.mode).save(p); done.add(f)
pkg = E / 'orig' / t / f'{t}_badge_mobile.usdz'
files = subprocess.run(['unzip', '-Z1', str(pkg)], capture_output=True, text=True).stdout.split()
out = E / 'measure' / mode / f'{t}.usdz'; out.unlink(missing_ok=True)
subprocess.run(['usdzip', str(out)] + files, cwd=D, check=True, stdout=subprocess.DEVNULL)
r = subprocess.run(['usdchecker', '--arkit', str(out)], capture_output=True, text=True)
print(t, mode, sorted(done), 'Success' if 'Success!' in r.stdout + r.stderr else 'CHECK FAILED')
