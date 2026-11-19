"""Enamel colors by the approved method: the mockup's own colors in emission, solved through the app's AgX. Python 3.11.

Usage: enamel_fill.py CAND_DIR MOCKUP.png CONFIG.json OUT_DIR
CONFIG.json: {"texture_px": 1024, "materials": {"Field": {"roughness": 0.4, "max_display": 0.92}, "Pearl": {...}, ...}}
OUT_DIR/palette_enamel.json: one entry per material ({color_texture, emission_texture, emission_scale, roughness}) to
merge into palette.json; textures in OUT_DIR/textures.

Approved Codex badges (Tidal Compass, Astral Navigator, Emerald Trophy: forge_tide_compass_20261103/prepare_finish.py
and pack.py) make enamel a metal with a near black color, so the studio adds no pale reflection (the one that washed
teal to grey and made white glare spots on Mountain Sunburst), and carry the mockup's color in emission, solved through
the inverse of the app's AgX. Emerald Trophy: "A fully metallic emerald field removes the pale dielectric reflection
and increases green saturation." Here:
* only mockup pixels where the build shows that material, 3 px inside its edges and never the mockup's gold, are
  sampled; every other texel takes the nearest sampled one, so no gold or neighbor color bleeds into an enamel face;
* colors the app cannot show map to the nearest it can in Oklab with lightness counting 0.35 (pale lemon rule), and
  everything stays at or under 1.4 linear (the glow level is 1.5);
* the mockup is blurred 1.2 px first: its painted gradients stay, its pixel noise goes (grain reads at phone size).
"""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from agx import agx

C = Path(sys.argv[1]); D = np.load(C / 'parts.npz'); META = json.load(open(C / 'parts.json'))
mock = np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(float) / 255
CFG = json.load(open(sys.argv[3])); OUT = Path(sys.argv[4]); (OUT / 'textures').mkdir(parents=True, exist_ok=True)
U = META['units']; S, AX, TOP = U['S'], U['axis'], U.get('top', 15.0); H, W = mock.shape[:2]
# badge3d maps enamel UVs over units.width_px x units.height_px (default 1312 x 1199, one old mockup); any other
# size would shift every enamel color against its area
if (U.get('width_px', 1312.0), U.get('height_px', 1199.0)) != (W, H):
    sys.exit(f"PIECES.json units width_px/height_px {U.get('width_px', 1312.0)} x {U.get('height_px', 1199.0)} do not match "
             f"the mockup {W} x {H}: set them and rerun badge3d.py")
missing = [m for m in CFG['materials'] if m not in META.get('glow_only', [])]
if missing:   # glow only enamel without the fixed shading direction shows dark specks where lights reflect (Golden Storm)
    sys.exit(f'add {missing} to "glow_only" in PIECES.json and rerun badge3d.py before enamel_fill.py')
N = CFG.get('texture_px', 1024)

# top material per mockup pixel
top_z = np.full((H, W), -np.inf); top_m = np.full((H, W), -1, int); names = []
for p in META['parts']:
    V = D[p['name'] + '_v'][:p['front']]; M = D[p['name'] + '_m'][:p['front']]
    ids = [names.index(n) if n in names else (names.append(n) or len(names) - 1) for n in p['materials']]
    px = V[..., 0] / S + AX; py = TOP + (2.995 - V[..., 1]) / S
    for (x0, x1, x2), (y0, y1, y2), (z0, z1, z2), mi in zip(px, py, V[..., 2], M):
        bx0, bx1 = int(max(np.floor(min(x0, x1, x2)), 0)), int(min(np.ceil(max(x0, x1, x2)), W - 1))
        by0, by1 = int(max(np.floor(min(y0, y1, y2)), 0)), int(min(np.ceil(max(y0, y1, y2)), H - 1))
        if bx1 < bx0 or by1 < by0:
            continue
        gy, gx = np.mgrid[by0:by1 + 1, bx0:bx1 + 1] + 0.5
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-12:
            continue
        w0 = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / den; w1 = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / den; w2 = 1 - w0 - w1
        ins = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6); z = w0 * z0 + w1 * z1 + w2 * z2
        iy, ix = (gy - 0.5).astype(int), (gx - 0.5).astype(int); upd = ins & (z > top_z[iy, ix])
        top_z[iy[upd], ix[upd]] = z[upd]; top_m[iy[upd], ix[upd]] = ids[mi]

# the mockup's gold (with its highlights: warm, greener than blue) never feeds an enamel texture
r, g, b = mock.transpose(2, 0, 1); mx, mn = mock.max(2), mock.min(2); sat = (mx - mn) / np.maximum(mx, 1e-6); d = np.maximum(mx - mn, 1e-6)
hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
gold = (hue >= 20) & (hue < 62) & (sat > 0.3) & ~((hue >= 44) & (sat > 0.55) & (mx > 0.85))
gold_ext = ndi.binary_dilation(gold | ((mx > 0.8) & ((r - b) > 0.08) & ((g - b) > 0.05)), iterations=1)


def oklab(rgb):
    l = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]])
    M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]])
    return np.cbrt(np.maximum(l @ M1.T, 0)) @ M2.T


lv = np.r_[0.0, np.geomspace(0.0015, 1.4, 90)]
G = np.stack(np.meshgrid(lv, lv, lv, indexing='ij'), -1).reshape(-1, 3)
shown = np.clip(agx(G), 0, 1); Wt = np.array([np.sqrt(0.35), 1, 1]); tree = cKDTree(oklab(shown) * Wt)
blur = np.stack([gaussian_filter(mock[..., c], 1.2) for c in range(3)], -1)
enc = lambda a: np.uint8(np.clip(np.where(a <= 0.0031308, a * 12.92, 1.055 * np.maximum(a, 0) ** (1 / 2.4) - 0.055) * 255 + 0.5, 0, 255))
pal = {}
for mat, spec in CFG['materials'].items():
    if mat not in names:
        print(f'{mat}: not on top anywhere, skipped'); continue
    valid = ndi.binary_erosion(top_m == names.index(mat), iterations=3)
    if spec.get('exclude_gold', True):
        valid &= ~gold_ext
    if valid.sum() < 50:
        print(f'{mat}: too few clean pixels ({valid.sum()})'); continue
    target = np.minimum(blur[valid], spec.get('max_display', 0.92))
    _, idx = tree.query(oklab(target) * Wt); lin = G[idx]                       # linear light that shows the target
    full = np.zeros((H, W, 3)); full[valid] = lin
    _, (iy, ix) = ndi.distance_transform_edt(~valid, return_indices=True); full = full[iy, ix]   # nearest clean texel
    full = np.stack([np.asarray(Image.fromarray(full[..., c].astype(np.float32)).resize((N, N), Image.BILINEAR)) for c in range(3)], -1)
    color = np.minimum(full * 0.007, 0.009); emission = np.maximum(0.0, full - color * 0.4)
    scale = 8.0
    fc, fe = f'textures/{mat.lower()}_color.png', f'textures/{mat.lower()}_emission.png'
    Image.fromarray(enc(color)).save(OUT / fc); Image.fromarray(enc(emission / scale)).save(OUT / fe)
    pal[mat] = dict(color_texture=fc, emission_texture=fe, emission_scale=scale, roughness=spec.get('roughness', 0.4), metallic=1.0)
    med_t = np.median(blur[valid], 0); med_s = np.median(shown[idx], 0)
    print(f'{mat:10s} pixels {int(valid.sum()):7d}  mockup median {med_t.round(3)}  shows {med_s.round(3)}  emission max {float(emission.max()):.2f}')
json.dump(pal, open(OUT / 'palette_enamel.json', 'w'), indent=1)
print('written', OUT / 'palette_enamel.json')
