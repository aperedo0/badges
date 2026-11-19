"""Render the gem (both crowns) through the app camera at a turn angle, offline.

Usage: view_gem.py GEOM.npz OPTICS_JSON_STRING OUT.png yaw1,yaw2,...
"""
import sys, json
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/tools')
import foilsim, screen_render as SR
from PIL import Image, ImageDraw

def render(V, N, T, prm, deg, box=(300, 250, 906, 856)):
    Vw = foilsim.yaw(V, deg); Nw = foilsim.yaw(N, deg)
    x0, y0, x1, y1 = box; W, H = x1 - x0, y1 - y0
    zbuf = np.full((H, W), np.inf); pid = np.full((H, W), -1)
    P2, Z = SR.project(Vw)
    for t, tri in enumerate(T):
        c = Vw[tri].mean(0)
        if Nw[tri[0]] @ (SR.EYE - c) <= 0: continue
        q = P2[tri]; zz = Z[tri]
        bx0, by0 = np.floor(q.min(0)).astype(int); bx1, by1 = np.ceil(q.max(0)).astype(int)
        bx0, by0 = max(bx0, x0), max(by0, y0); bx1, by1 = min(bx1, x1 - 1), min(by1, y1 - 1)
        if bx1 < bx0 or by1 < by0: continue
        ys, xs = np.mgrid[by0:by1 + 1, bx0:bx1 + 1]; px = xs + .5; py = ys + .5
        a, b, cc = q
        den = (b[1] - cc[1]) * (a[0] - cc[0]) + (cc[0] - b[0]) * (a[1] - cc[1])
        if abs(den) < 1e-9: continue
        w0 = ((b[1] - cc[1]) * (px - cc[0]) + (cc[0] - b[0]) * (py - cc[1])) / den
        w1 = ((cc[1] - a[1]) * (px - cc[0]) + (a[0] - cc[0]) * (py - cc[1])) / den
        w2 = 1 - w0 - w1
        inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        z = w0 * zz[0] + w1 * zz[1] + w2 * zz[2]
        upd = inside & (z < zbuf[ys - y0, xs - x0])
        zbuf[ys[upd] - y0, xs[upd] - x0] = z[upd]; pid[ys[upd] - y0, xs[upd] - x0] = t
    m = pid >= 0; ys, xs = np.nonzero(m)
    dirs = foilsim.unit(SR.F[None] * SR.FOC + SR.RIGHT[None] * ((xs + x0 + .5) - SR.CX)[:, None] + SR.UP[None] * (SR.CY - (ys + y0 + .5))[:, None])
    tri = T[pid[m]]; nw = Nw[tri[:, 0]]; p0 = Vw[tri[:, 0]]
    s = np.sum(nw * (p0 - SR.EYE), 1) / np.sum(nw * dirs, 1)
    pw = SR.EYE + dirs * s[:, None]
    img = np.zeros((H, W, 3)) + 0.045
    img[m] = foilsim.display(foilsim.shade(foilsim.yaw(pw, -deg), N[tri[:, 0]], foilsim.yaw(dirs, -deg), prm, deg))
    return img

if __name__ == '__main__':
    g = np.load(sys.argv[1]); prm = dict(foilsim.DEFAULT, **json.loads(sys.argv[2]))
    prm['absorption'] = tuple(prm['absorption'])
    yaws = [float(a) for a in sys.argv[4].split(',')]
    ims = [render(g['gem_v'], g['gem_n'], g['gem_t'], prm, a) for a in yaws]
    out = Image.fromarray(np.uint8(np.concatenate(ims, 1) * 255))
    out.save(sys.argv[3])
