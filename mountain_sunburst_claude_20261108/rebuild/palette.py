"""Solve each enamel color's paint through the app's measured light (plan section 5) and make the sun gradient.

Rules: perceptual (Oklab) match with lightness counting 0.35 (the pale lemon method of carve_badge_v7b.py),
gain times albedo plus offset at most 1.4 linear per channel, no glow. Writes palette.json (linear albedo per
material, predicted display color) and textures/sun_gradient.png in mockup pixel space.
"""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from agx import agx
from scipy.spatial import cKDTree
HERE = Path(__file__).resolve().parent
cal = json.load(open('/Users/antonioperedo/Desktop/badges/enamel_badges_tools/calibration.json'))
gain, off = np.array(cal['gain']), np.array(cal['offset'])


def oklab(rgb):
    l = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]])
    M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]])
    return np.cbrt(np.maximum(l @ M1.T, 0)) @ M2.T


lv = np.r_[0.0, np.geomspace(0.003, 1.4, 70)]
G = np.stack(np.meshgrid(lv, lv, lv, indexing='ij'), -1).reshape(-1, 3)
G = G[((G + off) <= 1.4).all(1) & (G <= gain).all(1)]
shown = np.clip(agx(G + off), 0, 1); Wt = np.array([np.sqrt(0.35), 1, 1]); tree = cKDTree(oklab(shown) * Wt)


def solve(rgb):
    _, i = tree.query(oklab(np.atleast_2d(rgb)) * Wt); return G[i] / gain, shown[i]


targets = {'Red': (0.85, 0.31, 0.17), 'Lemon': (1.0, 0.77, 0.06), 'Snow': (0.95, 0.94, 0.96), 'Cloud': (0.95, 0.93, 0.91),
           'Teal': (0.18, 0.49, 0.67), 'Steel': (0.13, 0.36, 0.55), 'Navy': (0.10, 0.20, 0.47), 'Royal': (0.12, 0.23, 0.53)}
pal = {}
for k, t in targets.items():
    a, s = solve(np.array(t)); pal[k] = dict(target=list(t), albedo=a[0].round(4).tolist(), shows=s[0].round(3).tolist())
# lavender snow keeps the mockup's white to lavender ratio (round 3 blocker 6)
lav_t = np.array(pal['Snow']['shows']) * (np.array([0.81, 0.80, 0.85]) / np.array([0.95, 0.94, 0.96]))
a, s = solve(lav_t); pal['SnowLavender'] = dict(target=lav_t.round(3).tolist(), albedo=a[0].round(4).tolist(), shows=s[0].round(3).tolist())
pal['Gold'] = dict(albedo=[0.55, 0.22, 0.0], metallic=1.0, roughness=0.24)
pal['GoldRing'] = dict(albedo=[0.55, 0.22, 0.0], metallic=1.0, roughness=0.30)
pal['Side'] = dict(albedo=[0.33, 0.132, 0.0], metallic=1.0, roughness=0.55)
for k in targets:
    pal[k]['roughness'] = 0.28 if k in ('Snow', 'Cloud') else 0.12
pal['SnowLavender']['roughness'] = 0.28
# the sun: pale lemon at the top to orange at the lower left, as a texture over the mockup's pixel space
W, H = 1312, 1199; Y, X = np.mgrid[0:H, 0:W].astype(float)
cx, cy, r = 653.5, 566.2, 218.0
t = np.clip(((Y - (cy - r)) / (2 * r)) * 0.75 + ((cx - X) / (2 * r) + 0.5) * 0.25, 0, 1)
top, bottom = np.array([1.0, 0.77, 0.10]), np.array([0.94, 0.49, 0.06])
grad_targets = top[None] + (bottom - top)[None] * np.linspace(0, 1, 64)[:, None]
grad_alb = np.vstack([solve(g)[0] for g in grad_targets])
idx = np.clip((t * 63).round().astype(int), 0, 63)
tex = grad_alb[idx] ** (1 / 2.2)
(HERE / 'textures').mkdir(exist_ok=True)
Image.fromarray(np.uint8(np.clip(tex, 0, 1) * 255)).resize((512, 468), Image.BILINEAR).save(HERE / 'textures/sun_gradient.png')
pal['SunDisc'] = dict(texture='textures/sun_gradient.png', roughness=0.12, shows_top=solve(top)[1][0].round(3).tolist(), shows_bottom=solve(bottom)[1][0].round(3).tolist())
json.dump(pal, open(HERE / 'palette.json', 'w'), indent=1)
for k, v in pal.items():
    print(k, v.get('shows', v.get('albedo')))
