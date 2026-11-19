"""Compare what the app shows with the planned enamel colors, per area. Usage: measure.py candidateNN"""
import sys, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from agx import agx, agx_inv
C = sys.argv[1]
a = np.asarray(Image.open(C + '/app/front.png').convert('RGB')).astype(float) / 255
meta = json.load(open(C + '/parts.json')); S = meta['units_per_pixel']; CX = meta['center_x']; TOP = meta['top']
bmin, bmax = meta['bounds_min'], meta['bounds_max']
reg = a[300:850, 300:900]; mm = ((reg.max(2) - reg.min(2)) > .16) & (reg.max(2) > .35)
cols = np.nonzero(mm.any(0))[0]; rows = np.nonzero(mm.any(1))[0]
x0, x1, y0 = cols.min() + 300, cols.max() + 300, rows.min() + 300
ppu = (x1 - x0) / (bmax[0] - bmin[0])
m = np.load(C + '/masks.npz'); H = W = 1254
em = np.asarray(Image.open(C + '/textures/art_emission.png').convert('RGB')).astype(float) / 255
art = json.load(open(C + '/textures/art.json'))
lin_plan = np.where(em <= .04045, em / 12.92, ((em + .055) / 1.055) ** 2.4) * art['emission_scale']
ys, xs = np.mgrid[:H, :W]
sx = x0 + ((xs - CX) * S - bmin[0]) * ppu; sy = y0 + (ys - TOP) * S * ppu


def disk(n):
    y, x = np.mgrid[-n:n + 1, -n:n + 1]; return x * x + y * y <= n * n + .5


im = np.asarray(Image.open('reference/mockup.png').convert('RGB')).astype(float) / 255
lum = im @ np.array([.2126, .7152, .0722])
classes = dict(bolt_face=ndi.binary_erosion(m['face'] & m['bolt_visible'], disk(14)), pearl=ndi.binary_erosion(m['pearl'] & ~m['bolt'], disk(14)),
               blue_dark=ndi.binary_erosion(m['blue'] & (lum < .2) & ~m['bolt'], disk(8)), blue_light=ndi.binary_erosion(m['blue'] & (lum > .5) & ~m['bolt'], disk(8)),
               gold=ndi.binary_erosion(m['gold'], disk(5)))
print('screen: left', x0, 'right', x1, 'top', y0, 'pixels per unit', round(ppu, 2))
out = {}
for k, mk in classes.items():
    yy, xx = np.nonzero(mk); sel = np.random.default_rng(0).choice(len(yy), min(5000, len(yy)), replace=False); yy = yy[sel]; xx = xx[sel]
    got = a[np.round(sy[yy, xx]).astype(int), np.round(sx[yy, xx]).astype(int)]
    plan = lin_plan[(yy * 1024 / H).astype(int), (xx * 1024 / W).astype(int)]
    g = np.median(got, 0); pl = np.median(plan, 0); gl = np.clip(agx_inv(g[None]), 0, None)[0]
    out[k] = dict(app=g.tolist(), app_linear=gl.tolist(), planned_linear=pl.tolist())
    extra = '' if k == 'gold' else f'  planned {np.round(agx(pl[None])[0], 3)}  planned light {np.round(pl, 3)}'
    print(f'{k:11s} app shows {np.round(g, 3)}  app light {np.round(gl, 3)}' + extra)
json.dump(out, open(C + '/measure.json', 'w'), indent=1)
