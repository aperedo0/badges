"""solve_band.py <tier> <out_dir> [sigma] : Step 0 v2. Re solves only the outline band of each textured front material.
Screen inputs (iPhone 17 shots in shots_v2/): orig_<tier> (the current look O), calib_<tier> (color maps at albedo 0.15, glow off -> light L),
id_<tier> (glow pure green -> which pixels show the textured front). Band: front pixels within 3 px of the silhouette, or within 3 px of
the camera facing surface's edge where that edge is within 11 px of the silhouette. O and L are extended into the band from front pixels
outside it (normalized Gaussian, same connected front region). Band texels get albedo = min(1, O/L) and glow = the rest; all other texels
stay byte identical; uncovered texels next to changed ones copy the nearest changed texel."""
import sys, json, shutil, subprocess, numpy as np
from pathlib import Path
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt, label, map_coordinates, gaussian_filter, binary_erosion, binary_dilation, find_objects
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from common import to_screen, CAM_POS
from agx import agx_inv, refine
E = Path('/Users/antonioperedo/Desktop/badges/edge_fix_20261010'); t = sys.argv[1]; out = Path(sys.argv[2]); sigma = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
EMIS_SCALE = {'copper': 3.0, 'bronze': 3.0, 'steel': 3.0, 'platinum': 3.0, 'diamond': 4.0, 'silver': 1.0}[t]
A0 = 0.15
d = np.load(E / 'model' / f'{t}.npz'); info = json.loads(str(d['info']))
def img(p): return np.asarray(Image.open(p).convert('RGB'), float) / 255
S = E / 'shots_v2'; O_img, C_img, I_img = img(S / f'orig_{t}.png'), img(S / f'calib_{t}.png'), img(S / f'id_{t}.png')
# work window around the badge
allp = d['ALLP']; scr = to_screen(allp.reshape(-1, 3)).reshape(-1, 3, 2)
x0, y0 = np.floor(scr.reshape(-1, 2).min(0)).astype(int) - 16; x1, y1 = np.ceil(scr.reshape(-1, 2).max(0)).astype(int) + 16
win = (slice(y0, y1), slice(x0, x1))
def lin(im):
    disp = im[win]; l = agx_inv(disp); return refine(l, disp, steps=3)
O = lin(O_img); L = lin(C_img) / A0
v = I_img[win][..., 1] - I_img[win][..., [0, 2]].max(-1); F = v > 0.85 * np.percentile(v[v > 0.2], 95)
SS = 4
def raster(tris):
    im = Image.new('L', ((x1 - x0) * SS, (y1 - y0) * SS), 0); dr = ImageDraw.Draw(im)
    for tri in tris: dr.polygon([((p[0] - x0) * SS, (p[1] - y0) * SS) for p in tri], fill=255)
    a = np.asarray(im, float) / 255; return a.reshape(y1 - y0, SS, x1 - x0, SS).mean((1, 3))
n = np.cross(allp[:, 1] - allp[:, 0], allp[:, 2] - allp[:, 0]); n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
view = CAM_POS - allp.mean(1); view /= np.linalg.norm(view, axis=1, keepdims=True); facing = (n * view).sum(1) > 0.5
silc = raster(scr); frontc = raster(scr[facing])
sil = silc > 0.5; front = frontc > 0.5
dsil = distance_transform_edt(sil); dfront = distance_transform_edt(front)
band = sil & ((dsil < 3) | ((dfront < 3) & (dsil < 11)))
src = binary_erosion(F, iterations=1) & ~binary_dilation(band, iterations=1) & (silc > 0.999)
# components of the visible front surface; every pixel belongs to the component of its nearest front pixel
comp, ncomp = label(F, structure=np.ones((3, 3)))
_, (iy, ix) = distance_transform_edt(~F, return_indices=True); compall = comp[iy, ix]
Oext = np.zeros_like(O); Lext = np.zeros_like(L)
for c, sl in enumerate(find_objects(comp), start=1):
    if sl is None: continue
    pad = 24; ys = slice(max(sl[0].start - pad, 0), min(sl[0].stop + pad, O.shape[0])); xs = slice(max(sl[1].start - pad, 0), min(sl[1].stop + pad, O.shape[1]))
    m = (src[ys, xs] & (comp[ys, xs] == c)).astype(float); target = compall[ys, xs] == c
    if m.sum() < 4: continue
    accO = np.zeros(O[ys, xs].shape); accL = np.zeros(O[ys, xs].shape); acc = np.zeros(m.shape)
    for sg in (sigma, sigma * 3, sigma * 8):        # wider passes only fill what the narrow pass could not reach
        w = gaussian_filter(m, sg); need = (acc < 0.5) & (w > 1e-3)
        for ch in range(3):
            accO[..., ch] = np.where(need, gaussian_filter(m * O[ys, xs][..., ch], sg) / np.maximum(w, 1e-9), accO[..., ch])
            accL[..., ch] = np.where(need, gaussian_filter(m * L[ys, xs][..., ch], sg) / np.maximum(w, 1e-9), accL[..., ch])
        acc = np.where(need, 1.0, acc)
    Oext[ys, xs] = np.where(target[..., None], accO, Oext[ys, xs]); Lext[ys, xs] = np.where(target[..., None], accL, Lext[ys, xs])
def samp(f, s, order=1):
    return np.stack([map_coordinates(f[..., ch], [s[:, 1] - y0 - .5, s[:, 0] - x0 - .5], order=order, mode='nearest') for ch in range(3)], -1)
def samp1(f, s): return map_coordinates(f.astype(float), [s[:, 1] - y0 - .5, s[:, 0] - x0 - .5], order=0, mode='constant', cval=0)
srgb_e = lambda v: np.where(v <= .0031308, v * 12.92, 1.055 * np.clip(v, 0, None) ** (1 / 2.4) - .055)
srgb_d = lambda v: np.where(v <= .04045, v / 12.92, ((v + .055) / 1.055) ** 2.4)
# package copy
if out.exists(): shutil.rmtree(out)
shutil.copytree(E / 'orig' / t, out)
for mat, mi in info.items():
    cf = mi['files'].get('diffuseColor'); ef = mi['files'].get('emissiveColor')
    if not cf: continue
    col = np.asarray(Image.open(out / cf).convert('RGB')).copy(); H, W = col.shape[:2]
    emi = np.asarray(Image.open(out / ef).convert('RGB')).copy() if ef else None
    # every material reading this color map (a map may be shared)
    mats = [m for m, x in info.items() if x['files'].get('diffuseColor') == cf]
    sel = np.isin(d['MAT'], mats); P = d['P'][sel]; UV = d['UV'][sel]
    cover = np.zeros((H, W), bool); changed = np.zeros((H, W), bool)
    for tri, uv in zip(P, UV):
        px = np.stack([uv[:, 0] * W - .5, (1 - uv[:, 1]) * H - .5], -1)
        bx0, by0 = np.floor(px.min(0)).astype(int); bx1, by1 = np.ceil(px.max(0)).astype(int)
        gx, gy = np.meshgrid(np.arange(max(bx0, 0), min(bx1, W - 1) + 1), np.arange(max(by0, 0), min(by1, H - 1) + 1))
        e1 = px[1] - px[0]; e2 = px[2] - px[0]; den = e1[0] * e2[1] - e1[1] * e2[0]
        if abs(den) < 1e-12 or gx.size == 0: continue
        u = ((gx - px[0, 0]) * e2[1] - (gy - px[0, 1]) * e2[0]) / den; vv = (e1[0] * (gy - px[0, 1]) - e1[1] * (gx - px[0, 0])) / den
        ins = (u >= -0.01) & (vv >= -0.01) & (u + vv <= 1.01)
        if not ins.any(): continue
        Y, X = gy[ins], gx[ins]; cover[Y, X] = True
        pos = (1 - u[ins] - vv[ins])[:, None] * tri[0] + u[ins][:, None] * tri[1] + vv[ins][:, None] * tri[2]
        s = to_screen(pos); inb = samp1(band, s) > 0.5
        if not inb.any(): continue
        s = s[inb]; Y, X = Y[inb], X[inb]
        tgt = samp(Oext, s); lt = np.maximum(samp(Lext, s), 1e-4)
        alb = np.clip(tgt / lt, 0.005, 1.0); em = np.clip(tgt - alb * lt, 0, EMIS_SCALE)
        col[Y, X] = np.uint8(np.clip(srgb_e(alb), 0, 1) * 255 + .5)
        if emi is not None: emi[Y, X] = np.uint8(np.clip(srgb_e(em / EMIS_SCALE), 0, 1) * 255 + .5)
        changed[Y, X] = True
    _, (iy2, ix2) = distance_transform_edt(~cover, return_indices=True); take = ~cover & changed[iy2, ix2]
    col = np.where(take[..., None], col[iy2, ix2], col)
    Image.fromarray(col).save(out / cf)
    if emi is not None:
        emi = np.where(take[..., None], emi[iy2, ix2], emi); Image.fromarray(emi).save(out / ef)
    print(f'{t} {cf}: band texels {int(changed.sum())} of {int(cover.sum())} covered')
files = subprocess.run(['unzip', '-Z1', str(E / 'orig' / t / f'{t}_badge_mobile.usdz')], capture_output=True, text=True).stdout.split()
pkg = out.parent / f'{t}.usdz'; pkg.unlink(missing_ok=True)
subprocess.run(['usdzip', str(pkg)] + files, cwd=out, check=True, stdout=subprocess.DEVNULL)
r = subprocess.run(['usdchecker', '--arkit', str(pkg)], capture_output=True, text=True)
print(t, 'packed', pkg.stat().st_size, 'Success' if 'Success!' in r.stdout + r.stderr else 'CHECK FAILED', 'components', ncomp, 'band px', int(band.sum()))
