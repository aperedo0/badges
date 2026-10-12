"""calib2.py <name> <base_dir> calib|id : writes <name>/tex atlases.
calib: star face cells and whole leaf atlases at albedo 0.5, no emissive.
id: star cells and leaf atlases at albedo 0.005 with emissive red (star) and green (leaves), for a coverage mask."""
import sys, numpy as np
from PIL import Image
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from common import *
name, base, mode = sys.argv[1], W / sys.argv[2], sys.argv[3]
tex = W / name / 'tex'; tex.mkdir(parents=True, exist_ok=True)
alb = 0.5 if mode == 'calib' else 0.005
leaf_alb = float(sys.argv[4]) if len(sys.argv) > 4 and mode == 'calib' else alb
enc = lambda v: np.uint8(np.clip(srgb_encode(np.array(v, float)), 0, 1) * 255 + .5)
for mat, emis in [('Silver2_StarLit_Satin', (1, 0, 0)), ('Silver2_StarShaded_Satin', (1, 0, 0))]:
    a = np.asarray(Image.open(base / '0' / f'{mat}_color.png').convert('RGB')).copy(); e = np.zeros_like(a)
    for p in range(10):
        rs, cs = cell_slice(p); a[rs, cs] = enc([alb] * 3); e[rs, cs] = enc(emis)
    Image.fromarray(a).save(tex / f'{mat}_color.png')
    if mode == 'id': Image.fromarray(e).save(tex / f'{mat}_emissive.png')
for mat in ['Silver2_LeafLit_Satin', 'Silver2_LeafShaded_Satin']:
    Image.fromarray(np.tile(enc([leaf_alb] * 3), (SIZE, SIZE, 1))).save(tex / f'{mat}_color.png')
    if mode == 'id': Image.fromarray(np.tile(enc([0, 1, 0]), (SIZE, SIZE, 1))).save(tex / f'{mat}_emissive.png')
print(name, mode, 'atlases written')
