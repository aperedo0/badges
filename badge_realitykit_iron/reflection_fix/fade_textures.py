"""Fades the casing's forged texture to an even finish over the part of the rim the floor reflection shows.
Usage: /usr/local/bin/python3 fade_textures.py <work dir> <h_smooth> <h_full> <out dir>
Heights are model units above the floor (Y = -2.895). Below h_smooth every casing texel equals the even value
Codex already used at the contact (mean of texels below 0.08 units); between h_smooth and h_full it blends back
(smoothstep) to the untouched texture; above h_full nothing changes. Texture size, mode and every other file stay
the same. Writes weight previews for checking."""
import json, sys, shutil
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
W, h0, h1, out = Path(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), Path(sys.argv[4])
FLOOR = -2.895
geo = np.load(W / 'geometry.npz')
mats = json.load(open(W / 'materials.json'))
tex_tris = {}
for key, info in mats.items():
    if not key.startswith('Casing'):
        continue
    for f in info['files'].values():
        tex_tris.setdefault(f, []).append((geo[key + '|pos'], geo[key + '|uv']))
if out.exists():
    shutil.rmtree(out)
shutil.copytree(W / 'src', out)
def smooth(x):
    x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
report = {}
for f, groups in tex_tris.items():
    path = W / 'src' / f
    img = Image.open(path); mode = img.mode
    arr = np.asarray(img).astype(np.float64)
    if arr.ndim == 2:
        arr = arr[..., None]
    H, Wd = arr.shape[:2]
    hmap = np.full((H, Wd), np.nan)
    for pos, uv in groups:
        hf = pos[..., 1] - FLOOR                     # (n,3) heights above the floor
        px = uv[..., 0] * Wd - 0.5; py = (1 - uv[..., 1]) * H - 0.5
        for t in range(len(pos)):
            x, y, h = px[t], py[t], hf[t]
            x0, x1 = int(np.floor(x.min())), int(np.ceil(x.max())); y0, y1 = int(np.floor(y.min())), int(np.ceil(y.max()))
            x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, Wd - 1), min(y1, H - 1)
            if x1 < x0 or y1 < y0:
                continue
            gy, gx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
            d = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
            if abs(d) < 1e-12:
                continue
            a = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / d
            b = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / d
            c = 1 - a - b
            inside = (a >= -1e-6) & (b >= -1e-6) & (c >= -1e-6)
            hv = a * h[0] + b * h[1] + c * h[2]
            sub = hmap[y0:y1 + 1, x0:x1 + 1]
            take = inside & (np.isnan(sub) | (hv < sub))
            sub[take] = hv[take]
    covered = ~np.isnan(hmap)
    if not covered.any():
        continue
    # texels outside every triangle (padding) take the nearest covered texel's height, so no seam appears
    _, (iy, ix) = distance_transform_edt(~covered, return_indices=True)
    hfull = hmap[iy, ix]
    band = hfull < 0.08
    if band.sum() < 20:
        band = hfull < 0.3
    target = arr[band].mean(axis=0)
    w = smooth((hfull - h0) / (h1 - h0))[..., None]
    new = target * (1 - w) + arr * w
    res = np.clip(np.rint(new), 0, 255).astype(np.uint8)
    res = res[..., 0] if mode == 'L' else res
    Image.fromarray(res, mode).save(out / f)
    Image.fromarray(np.uint8(np.clip(w[..., 0] * 255, 0, 255))).save(out / (f + '.weight.png'))
    changed = (np.abs(new - arr).max(axis=-1) >= 0.5)
    report[f] = {'size': [Wd, H], 'mode': mode, 'target': [round(float(v), 1) for v in target],
                 'covered_fraction': round(float(covered.mean()), 3), 'changed_texels': int(changed.sum())}
json.dump(report, open(out / 'fade_report.json', 'w'), indent=1)
for k, v in report.items():
    print(k, v)
