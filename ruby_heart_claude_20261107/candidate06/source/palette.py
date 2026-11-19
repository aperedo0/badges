"""Color mix of the gem on an app front screenshot vs the new reference (same tone bins)."""
import sys
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/tools')
import screen_render as SR
from PIL import Image
from matplotlib.path import Path as MPath
O = np.load('/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/trace/outline.npz')
inner = O['inner']; full = np.vstack([inner, inner[::-1] * [-1, 1]])
P2, _ = SR.project(np.c_[full * 0.97, np.full(len(full), 0.5)])
app = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float) / 255
H, W = app.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]
m = MPath(P2).contains_points(np.c_[xx.ravel(), yy.ravel()]).reshape(H, W)
def bins(px):
    lum = px @ np.array([0.2126, 0.7152, 0.0722]); out = []
    for lo, hi in ((0, .25), (.25, .4), (.4, .55), (.55, .75), (.75, 1.01)):
        s = (lum >= lo) & (lum < hi)
        out.append((round(float(s.mean()), 2), (px[s].mean(0) * 255).round().astype(int).tolist() if s.any() else None))
    return out
print('app gem', bins(app[m]))
ref = np.asarray(Image.open('/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/reference2/front.png').convert('RGB')).astype(float) / 255
h, w = ref.shape[:2]; yy, xx = np.mgrid[0:h, 0:w]
r, g, b = ref[..., 0], ref[..., 1], ref[..., 2]
inner2 = ((xx - w * 0.47) / (w * 0.26)) ** 2 + ((yy - h * 0.42) / (h * 0.32)) ** 2 < 1
print('reference', bins(ref[inner2 & (r > g + 0.05) & (r > b)]))
