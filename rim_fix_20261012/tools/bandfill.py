"""bandfill.py <work> <config.json> : repaint the outermost strip of a texture's covered area as the smooth (harmonic) continuation
of the texels just inside it, and refill every uncovered texel (padding) by pull-push, so neither the strip nor mipmaps carry a
rim. config: {"textures": ["1/color.png", "1/emissive.png"], "faces": [["<mesh>", "<subset>"], ...], "band_px": 3,
"out": "<dir for new pngs>"}. Band width in texels = band_px x texels per screen pixel (measured from the rest pose)."""
import sys, os, json, numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, zoom
import scipy.sparse as sp, scipy.sparse.linalg as spl
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/diamond/codex_rest_20261011/approved5/tools')
from common import to_screen
w = sys.argv[1]; cfg = json.load(open(sys.argv[2])); d = dict(np.load(w + '/mesh.npz')); meta = json.load(open(w + '/meta.json'))
edit = dict(np.load(w + '/edit.npz')) if os.path.exists(w + '/edit.npz') else {}
tex0 = Image.open(os.path.join(w, 'pkg', cfg['textures'][0])); W, H = tex0.size
tris_uv = []; tris_p = []
for mesh, subname in cfg['faces']:
    m = [x for x in meta if x['name'] == mesh][0]; i = m['i']
    P = edit.get(f'{i}:points', d[f'{i}:points']); C = d[f'{i}:counts']; I = d[f'{i}:indices']; UV = edit.get(f'{i}:uv', d[f'{i}:uv'])
    faces = edit.get(f'{i}:subset:{subname}', d[f'{i}:subset:{subname}']); off = np.r_[0, np.cumsum(C)[:-1]]
    for f in faces:
        slots = np.arange(off[f], off[f] + C[f]); vi = I[slots]
        uvs = UV[slots] if m['uv_interp'] == 'faceVarying' else UV[vi]
        for k in range(1, C[f] - 1):
            tris_uv.append(uvs[[0, k, k + 1]]); tris_p.append(P[vi[[0, k, k + 1]]])
tris_uv = np.array(tris_uv); tris_p = np.array(tris_p)
# texels per screen pixel from front facing triangles
scr = to_screen(tris_p.reshape(-1, 3)).reshape(-1, 3, 2)
a_uv = 0.5 * np.abs(np.cross(tris_uv[:, 1] - tris_uv[:, 0], tris_uv[:, 2] - tris_uv[:, 0])) * W * H
a_s = 0.5 * np.abs(np.cross(scr[:, 1] - scr[:, 0], scr[:, 2] - scr[:, 0])); ok = (a_s > 1e-3) & (a_uv > 1e-6)
tpp = float(np.sqrt(np.median(a_uv[ok] / a_s[ok]))); band = cfg.get('band_px', 3) * tpp
cov = np.zeros((H, W), bool)
for uv in tris_uv:
    px = np.stack([uv[:, 0] * W - .5, (1 - uv[:, 1]) * H - .5], -1)
    x0, y0 = np.floor(px.min(0)).astype(int); x1, y1 = np.ceil(px.max(0)).astype(int)
    gx, gy = np.meshgrid(np.arange(max(x0, 0), min(x1, W - 1) + 1), np.arange(max(y0, 0), min(y1, H - 1) + 1))
    if gx.size == 0: continue
    e1 = px[1] - px[0]; e2 = px[2] - px[0]; den = e1[0] * e2[1] - e1[1] * e2[0]
    if abs(den) < 1e-14: continue
    u = ((gx - px[0, 0]) * e2[1] - (gy - px[0, 1]) * e2[0]) / den; v = (e1[0] * (gy - px[0, 1]) - e1[1] * (gx - px[0, 0])) / den
    ins = (u >= -0.02) & (v >= -0.02) & (1 - u - v >= -0.02); cov[gy[ins], gx[ins]] = True
dist = distance_transform_edt(cov)
from scipy.ndimage import maximum_filter
hw = maximum_filter(dist, size=int(2 * band) * 2 + 1)            # local half width of the part around each texel
bw = np.minimum(band, cfg.get('thin_frac', 0.35) * hw)           # thin parts (tips) keep most of their own texels
bandm = cov & (dist <= bw); known = cov & ~bandm
print(f'  thin texels (band narrowed): {int((cov & (dist <= band) & ~bandm).sum())}')
print(f'texture {W}x{H}, texels/px {tpp:.2f}, band {band:.1f} texels, covered {cov.sum()}, band texels {bandm.sum()}, known {known.sum()}')
# harmonic fill of band texels: Laplace with Dirichlet at known covered texels, Neumann at uncovered
idx = -np.ones((H, W), int); bys, bxs = np.nonzero(bandm); idx[bys, bxs] = np.arange(len(bys))
rows, cols, vals = [], [], []; diag = np.zeros(len(bys)); rhs_nb = [[] for _ in range(len(bys))]
nbrs = ((0, 1), (0, -1), (1, 0), (-1, 0))
kn_lists = []
for dy, dx in nbrs:
    ny, nx = bys + dy, bxs + dx; inb = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
    ny_c, nx_c = np.clip(ny, 0, H - 1), np.clip(nx, 0, W - 1); c = inb & cov[ny_c, nx_c]
    diag += c; isb = c & bandm[ny_c, nx_c]
    r = np.nonzero(isb)[0]; rows += list(r); cols += list(idx[ny_c[r], nx_c[r]]); vals += [-1.0] * len(r)
    kn_lists.append((np.nonzero(c & ~bandm[ny_c, nx_c])[0], ny_c, nx_c))
iso = diag == 0; diag[iso] = 1
A = sp.csr_matrix((np.r_[vals, diag], (np.r_[rows, np.arange(len(bys))], np.r_[cols, np.arange(len(bys))])), shape=(len(bys),) * 2)
solve = spl.factorized(A.tocsc())
os.makedirs(cfg['out'], exist_ok=True); outfiles = {}
for f in cfg['textures']:
    im = Image.open(os.path.join(w, 'pkg', f)); mode = im.mode; a = np.asarray(im.convert('RGB'), float)
    new = a.copy()
    for ch in range(3):
        b = np.zeros(len(bys))
        for r, ny_c, nx_c in kn_lists: b[r] += a[ny_c[r], nx_c[r], ch]
        x = solve(b); x[iso] = a[bys[iso], bxs[iso], ch]; new[bys, bxs, ch] = x
    # pull-push padding for uncovered texels
    def pullpush(img, mask):
        if min(img.shape[:2]) <= 1 or mask.all(): return np.where(mask[..., None], img, img[mask].mean(0) if mask.any() else 0)
        h2, w2 = (img.shape[0] + 1) // 2, (img.shape[1] + 1) // 2
        pad = np.zeros((h2 * 2, w2 * 2, 3)); pm = np.zeros((h2 * 2, w2 * 2)); pad[:img.shape[0], :img.shape[1]] = img * mask[..., None]; pm[:img.shape[0], :img.shape[1]] = mask
        s = pad.reshape(h2, 2, w2, 2, 3).sum((1, 3)); n = pm.reshape(h2, 2, w2, 2).sum((1, 3))
        low = pullpush(s / np.maximum(n, 1)[..., None], n > 0)
        up = np.repeat(np.repeat(low, 2, 0), 2, 1)[:img.shape[0], :img.shape[1]]
        return np.where(mask[..., None], img, up)
    new = pullpush(new, cov)
    o = os.path.join(cfg['out'], f); os.makedirs(os.path.dirname(o), exist_ok=True)
    Image.fromarray(np.uint8(np.clip(new, 0, 255) + .5)).convert(mode).save(o); outfiles[f] = o
    chg = np.abs(new - a).max(-1) > 0.5
    print(f'  {f}: band texels changed {int((chg & bandm).sum())}, padding changed {int((chg & ~cov).sum())}, interior changed {int((chg & known).sum())}')
fj = os.path.join(cfg['out'], 'files.json'); allf = json.load(open(fj)) if os.path.exists(fj) else {}; allf.update(outfiles)
json.dump(allf, open(fj, 'w'), indent=1)
