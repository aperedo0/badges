"""Clean symmetric heart outline from the reference silhouette (model units).

Model: x = (x_ref - CX) * S, y = -2.455 + (BOTTOM - y_ref) * S.
Writes trace/outline.npz with the left half (x <= 0) as polylines from the
notch at the top center, around the lobe, to the bottom tip.
"""
import sys
import numpy as np
from PIL import Image, ImageDraw
from matplotlib import contour as mcontour
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

M = np.load('trace/masks.npz')
fg = M['fg'].astype(float)
CX, TOP, BOTTOM = 622.0, 123.0, 1111.0
HEIGHT = 5.45
S = HEIGHT / (BOTTOM - TOP)
BAND = 0.39

def to_model(p):
    return np.c_[(p[:, 0] - CX) * S, -2.455 + (BOTTOM - p[:, 1]) * S]

def to_ref(q):
    return np.c_[q[:, 0] / S + CX, BOTTOM - (q[:, 1] + 2.455) / S]

cs = plt.contour(fg, levels=[0.5])
paths = cs.allsegs[0]
path = max(paths, key=len)  # (x, y) in pixel coords
plt.close('all')

def half(path, side):
    p = path.copy()
    if p[0].tolist() == p[-1].tolist():
        p = p[:-1]
    if side > 0:
        p[:, 0] = 2 * CX - p[:, 0]
    notch = np.argmin(np.hypot(p[:, 0] - CX, p[:, 1] - 201))
    tip = np.argmin(np.hypot(p[:, 0] - CX, p[:, 1] - 1115))
    n = len(p)
    a = [(notch + k) % n for k in range((tip - notch) % n + 1)]
    b = [(notch - k) % n for k in range((notch - tip) % n + 1)]
    arc = a if p[a, 0].mean() < p[b, 0].mean() else b
    return p[arc]

def resample(q, n):
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(q, axis=0), axis=1))]
    t = np.linspace(0, d[-1], n)
    return np.c_[np.interp(t, d, q[:, 0]), np.interp(t, d, q[:, 1])]

L = resample(half(path, -1), 400)
R = resample(half(path, +1), 400)
for name, q in (('left', L), ('right_mirrored', R)):
    print(name, 'start', q[0].round(1), 'end', q[-1].round(1))
avg = (L + R) / 2
# Smooth curve: least squares cubic spline over arc length with few knots.
from scipy.interpolate import LSQUnivariateSpline
d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(avg, axis=0), axis=1))]; u = d / d[-1]
knots = np.linspace(0, 1, 8)[1:-1]
sm = np.c_[LSQUnivariateSpline(u, avg[:, 0], knots, k=3)(u), LSQUnivariateSpline(u, avg[:, 1], knots, k=3)(u)]
print('spline max deviation px', np.abs(sm - avg).max().round(2))

def corner(curve, raw, sel, keep_from, blend, apex_y=None, at_start=True):
    """Replace the end of the curve near the center line with a straight line fitted to raw points."""
    pts = raw[sel(raw)]
    a, b = np.polyfit(pts[:, 0], pts[:, 1], 1)
    c = curve.copy()
    idx = np.arange(len(c))
    near = (c[:, 0] > CX - keep_from) & ((c[:, 1] < 600) if at_start else (c[:, 1] > 600))
    for i in idx[near]:
        w = np.clip((c[i, 0] - (CX - keep_from)) / blend, 0, 1)
        c[i, 1] = (1 - w) * c[i, 1] + w * (a * c[i, 0] + b)
    # the curve must end exactly on the center line on the fitted line
    end = 0 if at_start else -1
    c[end] = [CX, a * CX + b]
    return c, (a, b)

# Notch: the straight gold edge between x = CX-80 and CX-25 (above the glow), apex measured at y ~ 232.
def corner_apex(curve, raw, apex, x_far, keep_from, blend, at_start):
    j = np.argmin(np.abs(raw[:, 0] - x_far) + (1e6 if at_start else 0) * (raw[:, 1] > 600))
    p0 = raw[j]; a = (apex[1] - p0[1]) / (apex[0] - p0[0]); b = apex[1] - a * apex[0]
    c = curve.copy()
    for i in range(len(c)):
        if c[i, 0] > CX - keep_from and ((c[i, 1] < 600) if at_start else (c[i, 1] > 600)):
            w = np.clip((c[i, 0] - (CX - keep_from)) / blend, 0, 1)
            c[i, 1] = (1 - w) * c[i, 1] + w * (a * c[i, 0] + b)
    c[0 if at_start else -1] = apex
    return c, (a, b)
sm, notch_line = corner_apex(sm, avg, (CX, 232.0), CX - 90, 95, 30, True)
sm, tip_line = corner(sm, avg, lambda q: (q[:, 0] > CX - 160) & (q[:, 0] < CX - 40) & (q[:, 1] > 940), 120, 40, at_start=False)
print('notch line', np.round(notch_line, 3), 'apex y', round(notch_line[0] * CX + notch_line[1], 1))
print('tip line', np.round(tip_line, 3), 'apex y', round(tip_line[0] * CX + tip_line[1], 1))
# keep a monotone run near each end (drop points that went past the center)
sm[:, 0] = np.minimum(sm[:, 0], CX)
def px_offset(q, d):
    t = np.gradient(q, axis=0); t /= np.linalg.norm(t, axis=1, keepdims=True)
    n = np.c_[-t[:, 1], t[:, 0]]
    i = np.argmin(q[:, 0])
    if n[i, 0] < 0: n = -n
    return q + n * d
ends = sm[[0, -1]].copy()
TOP = float(sm[:, 1].min()); BOTTOM = float(sm[:, 1].max())
sm = px_offset(sm, 4.0)
sm[0] = ends[0] + [0, 4.0 * 1.35]
sm[-1] = ends[1] - [0, 4.0 * 1.35]
TOP = float(sm[:, 1].min()); BOTTOM = float(sm[:, 1].max()); S = HEIGHT / (BOTTOM - TOP)
outer = to_model(sm)
outer[:, 0] = np.minimum(outer[:, 0], 0)
outer[0, 0] = outer[-1, 0] = 0

def offset_inward(poly, d):
    t = np.gradient(poly, axis=0, edge_order=1); t /= np.linalg.norm(t, axis=1, keepdims=True)
    n = np.c_[t[:, 1], -t[:, 0]]
    if n[np.argmin(poly[:, 0]), 0] < 0: n = -n
    q = poly + n * d
    inside = q[:, 0] < 0
    i0 = np.argmax(inside); i1 = len(q) - 1 - np.argmax(inside[::-1])
    def cross(a, b): return a + (b - a) * (a[0] / (a[0] - b[0]))
    top = cross(q[i0 - 1], q[i0]) if i0 > 0 else cross(q[i0 + 1], q[i0])
    bot = cross(q[i1], q[i1 + 1]) if i1 < len(q) - 1 else cross(q[i1 - 1], q[i1])
    return np.vstack([[0, top[1]], q[i0:i1 + 1], [0, bot[1]]])

inner = offset_inward(outer, BAND)
print('outer model x', outer[:, 0].min().round(3), 'y', outer[:, 1].min().round(3), outer[:, 1].max().round(3))
print('inner notch y', inner[0].round(3), 'tip', inner[-1].round(3), 'min x', inner[:, 0].min().round(3))
np.savez('trace/outline.npz', outer=outer, inner=inner, S=S, CX=CX, BOTTOM=BOTTOM, TOP=TOP)

ref = Image.open('reference.png').convert('RGB')
d = ImageDraw.Draw(ref)
for poly, col in ((outer, (0, 255, 255)), (inner, (0, 255, 0))):
    for sgn in (1, -1):
        q = poly.copy(); q[:, 0] *= sgn
        r = to_ref(q)
        d.line([tuple(p) for p in r], fill=col, width=2)
ref.save('trace/outline_overlay.png')
