"""Crown surface from the facet layout plus vertex heights; rasterize and shade."""
import sys, json
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/tools')
import facets, foilsim
from PIL import Image
from matplotlib.path import Path as MPath

NAMES, XY, GIRDLE, FACES = facets.layout()
HALF = [i for i, k in enumerate(NAMES) if not k.endswith("'")]
MIRROR = np.array([NAMES.index(k + "'") if (k + "'") in NAMES else i for i, k in enumerate(NAMES)])

def full_heights(z_half):
    z = np.zeros(len(NAMES))
    z[HALF] = z_half
    z[[MIRROR[i] for i in HALF]] = z_half
    return z

def planes(z):
    P = np.c_[XY, z]
    normals, offsets, resid = [], [], []
    for f in FACES:
        q = P[list(f)]
        c = q.mean(0)
        u, s, vt = np.linalg.svd(q - c)
        n = vt[-1]
        if n[2] < 0: n = -n
        normals.append(n); offsets.append(n @ c); resid.append(s[-1] if len(f) > 3 else 0.0)
    return np.array(normals), np.array(offsets), np.array(resid)

def raster(res=600, extent=(-2.6, 2.6, -2.1, 2.5)):
    x0, x1, y0, y1 = extent
    xs = np.linspace(x0, x1, res); ys = np.linspace(y1, y0, int(res * (y1 - y0) / (x1 - x0)))
    X, Y = np.meshgrid(xs, ys)
    pts = np.c_[X.ravel(), Y.ravel()]
    face = np.full(len(pts), -1)
    for i, f in enumerate(FACES):
        inside = MPath(XY[list(f)]).contains_points(pts, radius=1e-9)
        face[(face < 0) & inside] = i
    return X, Y, face.reshape(X.shape)

def render(z, prm=foilsim.DEFAULT, res=600, deg=0.0, raster_cache=None):
    X, Y, face = raster_cache or raster(res)
    n, w, _ = planes(z)
    m = face >= 0
    fi = face[m]
    px, py = X[m], Y[m]
    pz = (w[fi] - n[fi, 0] * px - n[fi, 1] * py) / n[fi, 2]
    p = np.c_[px, py, pz]
    nn = n[fi]
    pw = foilsim.yaw(p, deg)
    d = foilsim.yaw(foilsim.unit(pw - foilsim.EYE), -deg)
    lin = foilsim.shade(p, nn, d, prm, deg)
    img = np.zeros(X.shape + (3,)) + 0.04
    img[m] = foilsim.display(lin)
    return img
