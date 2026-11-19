"""Solve each material's paint through the app's measured light. Python 3.11.

Usage: palette.py TARGETS.json OUT_DIR
TARGETS.json: {"Red": {"target": [r, g, b], "roughness": 0.12},             # display colors the mockup shows (0 to 1)
               "Gold": {"albedo": [0.8, 0.37, 0.015], "metallic": 1, "roughness": 0.26},   # metals pass through
               "Sun": {"gradient": {"from": [r, g, b], "to": [r, g, b], "center": [x, y], "radius": px, "angle_deg": 250,
                                    "size_px": [W, H]}, "roughness": 0.12}}
Rules (badge-plan catalog): perceptual Oklab match with lightness counting 0.35 (colors the app cannot show keep
their hue and give up brightness: bright lemon becomes pale lemon), paint only, gain times albedo plus offset at
most 1.4 linear per channel (brighter glows), no emission. Writes OUT_DIR/palette.json and gradient textures.
"""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from agx import agx
from scipy.spatial import cKDTree
T = json.load(open(sys.argv[1])); OUT = Path(sys.argv[2]); (OUT / 'textures').mkdir(parents=True, exist_ok=True)
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
    _, i = tree.query(oklab(np.atleast_2d(np.asarray(rgb, float))) * Wt); return G[i] / gain, shown[i]


pal = {}
for name, v in T.items():
    if 'target' in v:
        a, s = solve(v['target']); pal[name] = dict(target=v['target'], albedo=a[0].round(4).tolist(), shows=s[0].round(3).tolist(), roughness=v.get('roughness', 0.12))
    elif 'gradient' in v:
        g = v['gradient']; Wp, Hp = g['size_px']; cx, cy = g['center']; r = g['radius']; ang = np.radians(g.get('angle_deg', 270))
        # solve the two ends only and blend the paint smoothly between them: solving every step snaps each to its own
        # grid point, and neighbors that jump back and forth draw stripes (cand02's sun)
        a0, a1 = solve(g['from'])[0][0], solve(g['to'])[0][0]
        Wt_, Ht_ = 1024, int(round(1024 * Hp / Wp)); Y, X = np.mgrid[0:Ht_, 0:Wt_].astype(float) * (Wp / Wt_)
        t = np.clip(0.5 + ((X - cx) * np.cos(ang) - (Y - cy) * np.sin(ang)) / (2 * r), 0, 1)[..., None]
        tex = (a0[None, None] * (1 - t) + a1[None, None] * t) ** (1 / 2.2)
        f = f'textures/{name.lower()}_gradient.png'
        Image.fromarray(np.uint8(np.clip(tex, 0, 1) * 255 + 0.5)).save(OUT / f)
        pal[name] = dict(texture=f, roughness=v.get('roughness', 0.12), shows_from=solve(g['from'])[1][0].round(3).tolist(), shows_to=solve(g['to'])[1][0].round(3).tolist())
    else:
        pal[name] = v
json.dump(pal, open(OUT / 'palette.json', 'w'), indent=1)
for k, v in pal.items():
    print(f"{k:14s}", v.get('shows', v.get('albedo', v.get('texture'))))
