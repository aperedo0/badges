"""solve.py <calib_dir> <out_npz> [a0] [blur] [gain]: per texel albedo so the app shows the reference star.
Observed calib render (uniform albedo a0) -> linear light per texel (inverse AgX), fitted smooth per plane.
Target = reference display color at the same face position (inverse AgX). Albedo = target / light."""
import sys, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from common import *
calib, out = Path(sys.argv[1]), sys.argv[2]
a0 = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
blur = float(sys.argv[4]) if len(sys.argv) > 4 else 1.5
gain = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
cube = np.frombuffer(open('/Users/antonioperedo/Desktop/screen_time/ScreenTime/SupportingFiles/Assets.xcassets/Badge3DAgXCube.dataset/agx_medium_high_contrast_65_rgba16f.bin','rb').read(), dtype=np.float16).astype(float).reshape(65, 65, 65, 4)  # [b][g][r]
LO, HI = -12.47393, 12.5260688117
def agx(lin):
    """Forward AgX for an (...,3) linear color, trilinear in the cube like the shader."""
    s = np.clip((np.log2(np.maximum(lin, 2.0 ** LO)) - LO) / (HI - LO), 0, 1) * 64
    i0 = np.clip(np.floor(s).astype(int), 0, 63); f = s - i0
    r0, g0, b0 = i0[..., 0], i0[..., 1], i0[..., 2]; fr, fg, fb = f[..., 0:1], f[..., 1:2], f[..., 2:3]
    out = 0
    for db in (0, 1):
        for dg in (0, 1):
            for dr in (0, 1):
                w = (fr if dr else 1 - fr) * (fg if dg else 1 - fg) * (fb if db else 1 - fb)
                out = out + w * cube[b0 + db, g0 + dg, r0 + dr, :3]
    return out
grid = 2.0 ** np.linspace(-12, 8, 4000)
grey_disp = agx(np.repeat(grid[:, None], 3, axis=1))
def agx_inv(disp):
    """Inverse per channel along the grey axis (silver is near neutral)."""
    res = np.empty_like(disp)
    for c in range(3):
        res[..., c] = np.interp(disp[..., c], grey_disp[:, c], grid)
    return res
def refine(lin_guess, disp_target, steps=6):
    """Newton style per channel correction with the full 3D transform."""
    lin = lin_guess.copy()
    for _ in range(steps):
        d = agx(lin); err = disp_target - d
        h = lin * 0.01 + 1e-6
        for c in range(3):
            l2 = lin.copy(); l2[..., c] += h[..., c]
            slope = (agx(l2)[..., c] - d[..., c]) / h[..., c]
            lin[..., c] = np.maximum(lin[..., c] + err[..., c] / np.maximum(slope, 1e-6), 1e-6)
    return lin
app = np.asarray(Image.open(calib / 'app.png').convert('RGB'), float) / 255
ref = np.asarray(Image.open(W / 'src/silver_reference.png').convert('RGB'), float) / 255
if blur > 0: ref = np.stack([gaussian_filter(ref[..., c], blur) for c in range(3)], -1)
planes = np.zeros((10, CELL, CELL, 3)); report = []
for p in range(10):
    tri = TRIS[p]; wx, wy = cell_world(p); wz = plane_z(p, wx, wy)
    w0, w1, w2 = bary(tri[:, :2], wx, wy)
    # screen positions and inset mask (2.5 px from every edge) for the light fit
    scr = to_screen(np.stack([wx, wy, wz], -1).reshape(-1, 3)).reshape(CELL, CELL, 2)
    st = to_screen(tri)
    def edge_dist(a, b, q):
        e = b - a; n = np.array([-e[1], e[0]]) / np.linalg.norm(e); return (q - a) @ n
    c = st.mean(0); ds = []
    for a, b in [(st[0], st[1]), (st[1], st[2]), (st[2], st[0])]:
        sgn = np.sign(edge_dist(a, b, c)); ds.append(edge_dist(a, b, scr) * sgn)
    inner = np.min(ds, axis=0) >= 2.5
    obs = np.stack([map_coordinates(app[..., ch], [scr[..., 1] - .5, scr[..., 0] - .5], order=1) for ch in range(3)], -1)
    light = agx_inv(obs) / a0
    # smooth fit of log light, cubic in barycentric (u=w1, v=w2), evaluated with clamped coordinates
    def basis(u, v): return np.stack([u ** i * v ** j for i in range(4) for j in range(4 - i)], -1)
    B = basis(w1[inner], w2[inner]); fit = np.zeros((CELL, CELL, 3))
    cu = np.clip(w1, 0.02, 0.98); cv = np.clip(w2, 0.02, 0.98); s = cu + cv; over = s > 0.98
    cu = np.where(over, cu / s * 0.98, cu); cv = np.where(over, cv / s * 0.98, cv)
    Bf = basis(cu, cv); resid = []
    for ch in range(3):
        coef, *_ = np.linalg.lstsq(B, np.log(light[inner][:, ch]), rcond=None)
        fit[..., ch] = np.exp(Bf @ coef); resid.append(float(np.std(np.log(light[inner][:, ch]) - B @ coef)))
    # target: reference color at the same face position, kept 4 ref px off the ridges and 3 px off the outer edge
    rtri = np.stack(world_to_ref(tri[:, 0], tri[:, 1]), -1)
    def height(k):
        a, b = [rtri[i] for i in range(3) if i != k]; e = b - a; n = np.array([-e[1], e[0]]) / np.linalg.norm(e); return abs((rtri[k] - a) @ n)
    t0 = np.maximum(1 - w1 - w2, 3 / height(0)); t1 = np.maximum(w1, 4 / height(1)); t2 = np.maximum(w2, 4 / height(2))
    ssum = t0 + t1 + t2; t0, t1, t2 = t0 / ssum, t1 / ssum, t2 / ssum
    rq = t0[..., None] * rtri[0] + t1[..., None] * rtri[1] + t2[..., None] * rtri[2]
    tgt = np.stack([map_coordinates(ref[..., ch], [rq[..., 1], rq[..., 0]], order=1) for ch in range(3)], -1)
    lin_t = refine(agx_inv(tgt), tgt) * gain
    alb = lin_t / fit
    planes[p] = np.clip(alb, 0.005, 1.0)
    m = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
    report.append((p, round(float((alb[m] > 1).mean()), 3), [round(r, 3) for r in resid], np.round(alb[m].mean(0), 3).tolist()))
np.savez(out, planes=planes)
for r in report: print('plane', r[0], 'clipped>1:', r[1], 'fit resid(log):', r[2], 'mean albedo:', r[3])
