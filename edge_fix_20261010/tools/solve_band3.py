"""solve_band3.py (v4: screen space target, smooth brightness ratio that keeps the hue, floor against notches)
solve_band2.py <tier> <out_dir> : Step 0 v2 (amended). Re solves only the outline band of every textured map, from the badge's own
maps and the measured light, never from a screenshot of the colors.
Geometry: 4x supersampled z buffer of every triangle (app camera) -> per screenshot pixel coverage, facing class (front: n.view > 0.5,
else wall), silhouette distance dsil, front edge distance dfront. Band = covered and (dsil < 3 or (dfront < 3 and dsil < 11)).
Light L = calib shot (albedo 0.15, glow off) through the grey axis inverse / 0.15, measured where a pixel is fully covered by one class,
extended into partial pixels from the same class (nested sigmas 1.5, 4, 12 px where weight < 0.1).
Texels: total = albedo * L + glow * s at visible, non band, measured source texels; band texels (visible ones only) get the total
extended inside their own UV island and facing class (nested sigmas, in texels), then albedo = clip(total / L, .005, 1),
glow = clip(total - albedo * L, 0, s) stored as sRGB(glow / s). Everything else stays byte identical."""
import sys, json, shutil, subprocess, numpy as np
from pathlib import Path
from PIL import Image
from scipy.ndimage import distance_transform_edt, label, map_coordinates, gaussian_filter, find_objects
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from common import CAM_POS, CAM_TARGET, FOCAL
from agx import agx_inv
E = Path('/Users/antonioperedo/Desktop/badges/edge_fix_20261010'); t = sys.argv[1]; out = Path(sys.argv[2]).resolve()
EDGE_REACH = float(sys.argv[3]) if len(sys.argv) > 3 else 11.0   # how far from the silhouette a front edge still counts as outline
WALLS = (sys.argv[4] != '0') if len(sys.argv) > 4 else True      # whether wall class texels change
S_EMIS = {'copper': 3.0, 'bronze': 3.0, 'steel': 3.0, 'platinum': 3.0, 'diamond': 4.0, 'silver': 1.0}[t]; A0 = 0.15; SS = 4
d = np.load(E / 'model' / f'{t}.npz'); info = json.loads(str(d['info']))
fw = CAM_TARGET - CAM_POS; fw /= np.linalg.norm(fw); rt = np.cross(fw, [0, 1, 0]); rt /= np.linalg.norm(rt); up = np.cross(rt, fw)
def proj(pts):
    q = np.asarray(pts, float) - CAM_POS; dep = q @ fw
    m = np.stack([540 + FOCAL * (q @ rt) / dep, 720 - FOCAL * (q @ up) / dep], -1)
    return m * 47 / 60 + np.array([180, 70]), dep
allp = d['ALLP']; scr, dep = proj(allp.reshape(-1, 3)); scr = scr.reshape(-1, 3, 2); dep = dep.reshape(-1, 3)
x0, y0 = np.floor(scr.reshape(-1, 2).min(0)).astype(int) - 16; x1, y1 = np.ceil(scr.reshape(-1, 2).max(0)).astype(int) + 16
Wp, Hp = x1 - x0, y1 - y0
nrm = np.cross(allp[:, 1] - allp[:, 0], allp[:, 2] - allp[:, 0]); nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-12)
vw = CAM_POS - allp.mean(1); vw /= np.linalg.norm(vw, axis=1, keepdims=True); facing = (nrm * vw).sum(1) > 0.5
zb = np.full((Hp * SS, Wp * SS), np.inf); fb = np.zeros((Hp * SS, Wp * SS), np.int8)   # 0 none, 1 front, 2 wall
def bary_grid(p, gx, gy):
    e1 = p[1] - p[0]; e2 = p[2] - p[0]; den = e1[0] * e2[1] - e1[1] * e2[0]
    if abs(den) < 1e-12: return None
    u = ((gx - p[0, 0]) * e2[1] - (gy - p[0, 1]) * e2[0]) / den; v = (e1[0] * (gy - p[0, 1]) - e1[1] * (gx - p[0, 0])) / den
    return 1 - u - v, u, v
for k in range(len(allp)):
    p = (scr[k] - [x0, y0]) * SS - 0.5
    bx0, by0 = np.floor(p.min(0)).astype(int); bx1, by1 = np.ceil(p.max(0)).astype(int)
    bx0, by0 = max(bx0, 0), max(by0, 0); bx1, by1 = min(bx1, Wp * SS - 1), min(by1, Hp * SS - 1)
    if bx1 < bx0 or by1 < by0: continue
    gx, gy = np.meshgrid(np.arange(bx0, bx1 + 1), np.arange(by0, by1 + 1)); b = bary_grid(p, gx, gy)
    if b is None: continue
    w0, w1, w2 = b; ins = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
    if not ins.any(): continue
    z = w0 * dep[k, 0] + w1 * dep[k, 1] + w2 * dep[k, 2]
    Y, X = gy[ins], gx[ins]; zz = z[ins]; closer = zz < zb[Y, X]
    zb[Y[closer], X[closer]] = zz[closer]; fb[Y[closer], X[closer]] = 1 if facing[k] else 2
blk = lambda a: a.reshape(Hp, SS, Wp, SS)
cov = blk(fb > 0).mean((1, 3)); frontfrac = blk(fb == 1).mean((1, 3)); wallfrac = blk(fb == 2).mean((1, 3))
full_front = frontfrac >= 0.999; full_wall = wallfrac >= 0.999
sil = cov > 0.5; dsil = distance_transform_edt(sil); dfront = distance_transform_edt(frontfrac > 0.5)
band = sil & ((dsil < 3) | ((frontfrac > 0.5) & (dfront < 3) & (dsil < EDGE_REACH)))   # the front edge rule applies to front pixels only
src_px = sil & (dsil >= 4) & ~((dfront < 4) & (dsil < 12))      # front sources
src_wall = sil & (dsil >= 3.5)                                  # wall sources: the wall itself, away from the silhouette
calib = np.asarray(Image.open(E / 'shots_v2' / f'calib_{t}.png').convert('RGB'), float)[y0:y1, x0:x1] / 255
Lm = agx_inv(calib) / A0
def nested(field, mask, sigmas):
    acc = np.zeros(field.shape); wacc = np.zeros(mask.shape); used = []
    m = mask.astype(float)
    for sg in sigmas:
        w = gaussian_filter(m, sg); need = (wacc < 0.1) & (w > 1e-4)
        for ch in range(3): acc[..., ch] = np.where(need, gaussian_filter(m * field[..., ch], sg) / np.maximum(w, 1e-12), acc[..., ch])
        wacc = np.where(need, np.maximum(w, 0.1), wacc); used.append(int(need.sum()))
    return acc, wacc > 0, used
Lf, okf, uf = nested(Lm, full_front, (1.5, 4, 12)); Lw, okw, uw = nested(Lm, full_wall, (1.5, 4, 12))
Lf = np.where(full_front[..., None], Lm, Lf); Lw = np.where(full_wall[..., None], Lm, Lw)
print(f'{t}: window {Wp}x{Hp}, band px {int(band.sum())}, source px {int(src_px.sum())}, L front fills {uf}, wall fills {uw}')
def at(f, s, order=1):
    yy = s[:, 1] - y0 - .5; xx = s[:, 0] - x0 - .5
    if f.ndim == 3: return np.stack([map_coordinates(f[..., c], [yy, xx], order=order, mode='nearest') for c in range(3)], -1)
    return map_coordinates(f.astype(float), [yy, xx], order=order, mode='constant', cval=0)
def zat(s):
    yy = np.clip(np.round((s[:, 1] - y0) * SS - .5).astype(int), 0, Hp * SS - 1); xx = np.clip(np.round((s[:, 0] - x0) * SS - .5).astype(int), 0, Wp * SS - 1)
    return zb[yy, xx]
sd = lambda v: np.where(v <= .04045, v / 12.92, ((v + .055) / 1.055) ** 2.4)
se = lambda v: np.where(v <= .0031308, v * 12.92, 1.055 * np.clip(v, 0, None) ** (1 / 2.4) - .055)
if out.exists(): shutil.rmtree(out)
shutil.copytree(E / 'orig' / t, out)
done = set()
for mat, mi in info.items():
    cf = mi['files'].get('diffuseColor'); ef = mi['files'].get('emissiveColor')
    if not cf or cf in done: continue
    done.add(cf)
    mats = [m for m, x in info.items() if x['files'].get('diffuseColor') == cf]
    col8 = np.asarray(Image.open(out / cf).convert('RGB')); H, W = col8.shape[:2]
    emi8 = np.asarray(Image.open(out / ef).convert('RGB')) if ef else np.zeros_like(col8)
    alb0 = sd(col8 / 255); emi0 = sd(emi8 / 255) * S_EMIS
    sel = np.isin(d['MAT'], mats); P = d['P'][sel]; UV = d['UV'][sel]
    uvA0 = 0.5 * np.abs(np.cross(UV[:, 1] - UV[:, 0], UV[:, 2] - UV[:, 0])) * W * H
    sA0 = np.array([0.5 * abs(np.cross(*(proj(tr)[0][1:] - proj(tr)[0][0]))) for tr in P])
    pnorm = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); pnorm /= np.maximum(np.linalg.norm(pnorm, axis=1, keepdims=True), 1e-12)
    pv = CAM_POS - P.mean(1); pv /= np.linalg.norm(pv, axis=1, keepdims=True); pface = (pnorm * pv).sum(1) > 0.5
    okA0 = (sA0 > 1e-3) & pface; tpp = float(np.sqrt(uvA0[okA0].sum() / sA0[okA0].sum())) if okA0.any() else 2.0
    cover = np.zeros((H, W), bool); cls = np.zeros((H, W), np.int8); vis = np.zeros((H, W), bool); inband = np.zeros((H, W), bool)
    Lt = np.zeros((H, W, 3)); spos = np.zeros((H, W, 2)); srcok_t = np.zeros((H, W), bool)
    for k, (tri, uv) in enumerate(zip(P, UV)):
        px = np.stack([uv[:, 0] * W - .5, (1 - uv[:, 1]) * H - .5], -1)
        bx0, by0 = np.floor(px.min(0)).astype(int); bx1, by1 = np.ceil(px.max(0)).astype(int)
        gx, gy = np.meshgrid(np.arange(max(bx0, 0), min(bx1, W - 1) + 1), np.arange(max(by0, 0), min(by1, H - 1) + 1))
        if gx.size == 0: continue
        b = bary_grid(px, gx, gy)
        if b is None: continue
        w0, w1, w2 = b; ins = (w0 >= -0.01) & (w1 >= -0.01) & (w2 >= -0.01)
        if not ins.any(): continue
        Y, X = gy[ins], gx[ins]
        pos = w0[ins][:, None] * tri[0] + w1[ins][:, None] * tri[1] + w2[ins][:, None] * tri[2]
        s_, z = proj(pos); visible = z <= zat(s_) + 0.01
        c = 1 if pface[k] else 2
        keep_front = (cls[Y, X] == 1) & (c == 2)
        cover[Y, X] = True; cls[Y, X] = np.where(cls[Y, X] == 1, 1, c); vis[Y, X] |= visible
        b_ = at(band, s_, order=0) > 0.5; inband[Y, X] |= b_ & visible
        Lc = at(Lf if c == 1 else Lw, s_)
        Lt[Y, X] = np.where(keep_front[:, None], Lt[Y, X], Lc)
        spos[Y, X] = np.where(keep_front[:, None], spos[Y, X], s_)
        full = at(full_front if c == 1 else full_wall, s_, order=0) > 0.5
        srcok_t[Y, X] |= visible & ~b_ & full & (at(src_px if c == 1 else src_wall, s_, order=0) > 0.5) & ~keep_front
    # totals at every covered texel from the badge's own maps and the measured light
    lumw = np.array([0.2126, 0.7152, 0.0722])
    Ttex = alb0 * Lt + emi0; Tlum = Ttex @ lumw
    # screen space source luminance per class: splat the source texels' totals into their pixels, then extend (nested sigmas)
    TGT = {}
    for c in (1, 2):
        m = srcok_t & (cls == c)
        acc = np.zeros((y1 - y0, x1 - x0)); cnt = np.zeros_like(acc)
        if m.any():
            sp = spos[m]; xi = np.clip(np.round(sp[:, 0] - x0 - .5).astype(int), 0, x1 - x0 - 1); yi = np.clip(np.round(sp[:, 1] - y0 - .5).astype(int), 0, y1 - y0 - 1)
            np.add.at(acc, (yi, xi), Tlum[m]); np.add.at(cnt, (yi, xi), 1)
        srcmask = cnt > 0; lumpx = np.where(srcmask, acc / np.maximum(cnt, 1), 0)
        near_, okn, used_n = nested(np.repeat(lumpx[..., None], 3, -1), srcmask, (1.5, 4, 12))
        broad, okb, used_b = nested(np.repeat(lumpx[..., None], 3, -1), srcmask, (4, 12))
        TGT[c] = (near_[..., 0], broad[..., 0], okn & okb)
        print(f'    class {c}: source texels {int(m.sum())}, source px {int(srcmask.sum())}, fills {used_n}')
    # per band texel: target luminance = max(near extension, 0.6 x broad average), ratio = target / own, smoothed inside the band
    ratio = np.ones((H, W)); bt = inband & vis
    for c in (1, 2):
        sel_ = bt & (cls == c)
        if not sel_.any(): continue
        near_, broad, ok = TGT[c]; sp = spos[sel_]
        tn = map_coordinates(near_, [sp[:, 1] - y0 - .5, sp[:, 0] - x0 - .5], order=1, mode='nearest')
        tb = map_coordinates(broad, [sp[:, 1] - y0 - .5, sp[:, 0] - x0 - .5], order=1, mode='nearest')
        okk = map_coordinates(ok.astype(float), [sp[:, 1] - y0 - .5, sp[:, 0] - x0 - .5], order=0, mode='nearest') > 0.5
        target = np.maximum(tn, 0.6 * tb)
        r = np.where(okk, np.clip(target / np.maximum(Tlum[sel_], 1e-6), 0, 1), 1.0)
        ratio[sel_] = r
    # smooth the darkening (1 - ratio) inside the band, so neighbouring texels never alternate (no speckles)
    sig = max(0.8 * tpp, 0.8)
    dk = np.where(bt, 1 - ratio, 0.0); wgt = gaussian_filter(bt.astype(float), sig)
    dks = gaussian_filter(dk, sig) / np.maximum(wgt, 1e-6)
    ratio_s = np.where(bt, 1 - np.clip(dks, 0, 1), 1.0)
    have = bt & (ratio_s < 0.995)
    rr = ratio_s[..., None]
    alb = np.clip(alb0 * rr, 0.0, 1.0); emi = np.clip(emi0 * rr, 0, S_EMIS)
    col_new = col8.copy(); emi_new = emi8.copy()
    col_new[have] = np.uint8(np.clip(se(alb[have]), 0, 1) * 255 + .5)
    emi_new[have] = np.uint8(np.clip(se(emi[have] / S_EMIS), 0, 1) * 255 + .5)
    _, (iy, ix) = distance_transform_edt(~cover, return_indices=True); take = ~cover & have[iy, ix]
    col_new = np.where(take[..., None], col_new[iy, ix], col_new); emi_new = np.where(take[..., None], emi_new[iy, ix], emi_new)
    changed = np.any(col_new != col8, -1) | np.any(emi_new != emi8, -1)
    assert not (changed & ~(have | take)).any(), 'changed texels outside the band and its padding'
    stats = [int(have.sum()), float(np.round(ratio_s[have].min(), 3)) if have.any() else 1.0]
    uvA = 0.5 * np.abs(np.cross(UV[:, 1] - UV[:, 0], UV[:, 2] - UV[:, 0])) * W * H
    Image.fromarray(col_new).save(out / cf)
    if ef: Image.fromarray(emi_new).save(out / ef)
    print(f'  {cf}: texels/px {tpp:.2f}, covered {int(cover.sum())}, band texels {int(inband.sum())}, darkened {stats[0]}, lowest ratio {stats[1]}, padding {int(take.sum())}')
files = subprocess.run(['unzip', '-Z1', str(E / 'orig' / t / f'{t}_badge_mobile.usdz')], capture_output=True, text=True).stdout.split()
pkg = out.parent / f'{t}.usdz'; pkg.unlink(missing_ok=True)
subprocess.run(['usdzip', str(pkg)] + files, cwd=out, check=True, stdout=subprocess.DEVNULL)
r = subprocess.run(['usdchecker', '--arkit', str(pkg)], capture_output=True, text=True)
print(t, 'packed', pkg.stat().st_size, 'Success' if 'Success!' in r.stdout + r.stderr else 'CHECK FAILED')
