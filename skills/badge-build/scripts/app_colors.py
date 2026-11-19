"""Measure every material as the app shows it, beside the mockup at the same spots. Python 3.11.

Usage: app_colors.py CAND_DIR MOCKUP.png REVIEW.json OUT.json
CAND_DIR holds parts.npz and parts.json (badge3d.py); REVIEW.json is the badge-fresh-review settings with
"mockup_box" [center x, top row, bottom row] and "build_box" (the same three in the app's front capture) and
"build_front" (the capture). For each material: where it is on top (from the model, mapped into the capture),
away from its borders, the app's display color and the mockup's, as Oklab lightness, chroma and hue at the 20th,
50th and 80th percentiles. Use it to see which colors read alike in the app (gold against lemon), and to correct
paint by measuring instead of guessing (AGENTS.md section 4).
"""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

C = Path(sys.argv[1]); D = np.load(C / 'parts.npz'); META = json.load(open(C / 'parts.json'))
mock = np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(float) / 255
R = json.load(open(sys.argv[3])); app = np.asarray(Image.open(R['build_front']).convert('RGB')).astype(float) / 255
U = META['units']; S, AX, TOP = U['S'], U['axis'], U.get('top', 15.0); H, W = mock.shape[:2]
mcx, mtop, mbot = R['mockup_box']; bcx, btop, bbot = R['build_box']; s = (bbot - btop) / (mbot - mtop)


def oklab(rgb):
    l = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]])
    M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]])
    return np.cbrt(np.maximum(l @ M1.T, 0)) @ M2.T


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
out = {}
erode_mock = max(int(round(3 / s)), 2)                   # 3 app pixels away from every border
for k, n in enumerate(names):
    core = ndi.binary_erosion(top_m == k, iterations=erode_mock)
    if core.sum() < 50:
        continue
    yy, xx = np.nonzero(core)
    ax_ = np.clip(np.round(bcx + (xx + 0.5 - mcx) * s).astype(int), 0, app.shape[1] - 1)
    ay_ = np.clip(np.round(btop + (yy + 0.5 - mtop) * s).astype(int), 0, app.shape[0] - 1)
    row = {}
    for label, rgb in (('app', app[ay_, ax_]), ('mockup', mock[yy, xx])):
        L = oklab(rgb); ch = np.hypot(L[:, 1], L[:, 2]); hue = np.degrees(np.arctan2(L[:, 2], L[:, 1])) % 360
        row[label] = dict(L=np.percentile(L[:, 0], [20, 50, 80]).round(3).tolist(), C=np.percentile(ch, [20, 50, 80]).round(3).tolist(),
                          hue=round(float(np.median(hue)), 0), median_rgb=np.median(rgb, 0).round(3).tolist())
    row['pixels'] = int(core.sum()); out[n] = row
    print(f"{n:14s} app L {row['app']['L']} C {row['app']['C'][1]:.3f} h {row['app']['hue']:.0f} {row['app']['median_rgb']} | "
          f"mockup L {row['mockup']['L']} C {row['mockup']['C'][1]:.3f} h {row['mockup']['hue']:.0f} {row['mockup']['median_rgb']}")
json.dump(out, open(sys.argv[4], 'w'), indent=1)
