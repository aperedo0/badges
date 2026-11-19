"""Render the gem crown through the app's measured front camera and compare to an app screenshot.

Usage: screen_render.py GEOM.npz OPTICS.json APP_FRONT.png OUT.png
Camera (measured by Codex on this simulator): eye (0, 1.8, 23), forward toward
(0, -2.35, -23), focal 1762.5 px, principal point (603, 633.3) on 1206 x 2622.
"""
import sys, json
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/tools')
import foilsim
from PIL import Image

EYE = np.array([0, 1.8, 23.0])
F = foilsim.unit(np.array([0, -2.35, -23.0]))
UP = np.cross([1, 0, 0], F); UP /= np.linalg.norm(UP)
RIGHT = np.array([1.0, 0, 0])
FOC, CX, CY = 1762.5, 603.0, 633.3

def project(P):
    v = P - EYE
    z = v @ F
    return np.c_[CX + (v @ RIGHT) / z * FOC, CY - (v @ UP) / z * FOC], z

def render(V, N, T, prm, box):
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    zbuf = np.full((H, W), np.inf); pid = np.full((H, W), -1)
    P2, Z = project(V)
    for t, tri in enumerate(T):
        if N[tri[0], 2] <= 0: continue  # front crown only
        q = P2[tri]; zz = Z[tri]
        bx0, by0 = np.floor(q.min(0)).astype(int); bx1, by1 = np.ceil(q.max(0)).astype(int)
        bx0, by0 = max(bx0, x0), max(by0, y0); bx1, by1 = min(bx1, x1 - 1), min(by1, y1 - 1)
        if bx1 < bx0 or by1 < by0: continue
        ys, xs = np.mgrid[by0:by1 + 1, bx0:bx1 + 1]
        px = xs + 0.5; py = ys + 0.5
        a, b, c = q
        den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(den) < 1e-9: continue
        w0 = ((b[1] - c[1]) * (px - c[0]) + (c[0] - b[0]) * (py - c[1])) / den
        w1 = ((c[1] - a[1]) * (px - c[0]) + (a[0] - c[0]) * (py - c[1])) / den
        w2 = 1 - w0 - w1
        inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        z = w0 * zz[0] + w1 * zz[1] + w2 * zz[2]
        sub = zbuf[ys - y0, xs - x0]
        upd = inside & (z < sub)
        zbuf[ys[upd] - y0, xs[upd] - x0] = z[upd]; pid[ys[upd] - y0, xs[upd] - x0] = t
    m = pid >= 0
    ys, xs = np.nonzero(m)
    dirs = foilsim.unit(F[None] * FOC + RIGHT[None] * ((xs + x0 + 0.5) - CX)[:, None] + UP[None] * (CY - (ys + y0 + 0.5))[:, None])
    tri = T[pid[m]]
    n = N[tri[:, 0]]
    # intersect ray with the triangle plane
    p0 = V[tri[:, 0]]
    s = np.sum(n * (p0 - EYE), 1) / np.sum(n * dirs, 1)
    p = EYE + dirs * s[:, None]
    img = np.zeros((H, W, 3))
    img[m] = foilsim.display(foilsim.shade(p, n, dirs, prm))
    return img, m

if __name__ == '__main__':
    g = np.load(sys.argv[1]); prm = dict(foilsim.DEFAULT, **json.load(open(sys.argv[2]))['prm'])
    prm['absorption'] = tuple(prm['absorption'])
    box = (300, 300, 906, 950)
    img, m = render(g['gem_v'], g['gem_n'], g['gem_t'], prm, box)
    app = np.asarray(Image.open(sys.argv[3]).convert('RGB')).astype(float)[box[1]:box[3], box[0]:box[2]] / 255
    from scipy import ndimage as ndi
    core = ndi.binary_erosion(m, iterations=4)
    err = np.abs(img - app)[core]
    print('gem pixels', core.sum(), 'mean abs err per channel', err.mean(0).round(3), 'sim mean', img[core].mean(0).round(3), 'app mean', app[core].mean(0).round(3))
    sim = app.copy(); sim[m] = img[m]
    out = np.concatenate([app, sim], 1)
    Image.fromarray(np.uint8(np.clip(out, 0, 1) * 255)).save(sys.argv[4])
