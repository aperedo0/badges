"""Shared geometry and mappings for the Silver 2 star metal work (working copy of Codex candidate 33)."""
import json, numpy as np
from pathlib import Path
W = Path('/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
SIZE, CELL, PAD = 512, 128, 12
CORE = CELL - 2 * PAD
LIT_PLANES = [4, 6, 7, 8, 9]
geom = json.loads((W / 'src/Star_geometry.json').read_text())
build = json.loads((W / 'src/build.json').read_text())
P = np.array(geom['points'], float)
IDX = np.array(geom['indices'])
TRIS = [P[IDX[f]] for f in geom['subsets']['front']]
OUTLINE = np.array([(627,237),(718,435),(898,478),(771,613),(801,801),(627,701),(453,800),(482,614),(351,478),(535,436)], float)
CENTER = np.array([627, 553], float)
CAM_POS = np.array([0, 1.8, 23.0]); CAM_TARGET = np.array([0, -0.55, 0]); FOCAL = 75 / 36 * 1080

def cell_world(plane):
    """World x, y of every texel of a plane's 128x128 cell (including padding)."""
    tri = TRIS[plane]; low, high = tri[:, :2].min(0), tri[:, :2].max(0)
    ty, tx = np.meshgrid(np.arange(CELL), np.arange(CELL), indexing='ij')
    wx = low[0] + (tx - PAD) / CORE * (high[0] - low[0])
    wy = low[1] + (CELL - PAD - ty) / CORE * (high[1] - low[1])
    return wx, wy

def cell_slice(plane):
    r, c = plane // 4, plane % 4
    return slice(r * CELL, (r + 1) * CELL), slice(c * CELL, (c + 1) * CELL)

def bary(tri2, x, y):
    a = tri2[1] - tri2[0]; b = tri2[2] - tri2[0]; den = a[0] * b[1] - a[1] * b[0]
    u = ((x - tri2[0, 0]) * b[1] - (y - tri2[0, 1]) * b[0]) / den
    v = (a[0] * (y - tri2[0, 1]) - a[1] * (x - tri2[0, 0])) / den
    return 1 - u - v, u, v

def plane_z(plane, x, y):
    tri = TRIS[plane]; w0, w1, w2 = bary(tri[:, :2], x, y)
    return w0 * tri[0, 2] + w1 * tri[1, 2] + w2 * tri[2, 2]

def to_screen(pts):
    """Model points (N,3) to iPhone 17 screenshot pixels (Codex's measured mapping: master * 47/60 + [180, 70])."""
    f = CAM_TARGET - CAM_POS; f /= np.linalg.norm(f); r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    d = pts - CAM_POS; depth = d @ f
    m = np.stack([540 + FOCAL * (d @ r) / depth, 720 - FOCAL * (d @ u) / depth], axis=-1)
    return m * 47 / 60 + np.array([180, 70])

def world_to_ref(x, y):
    t = build['metadata']['reference_to_world']; s = np.array(t['scale']); o = np.array(t['offset']); rs = build['metadata']['reference_scale']
    sx = x / s[0] - o[0]; sy = (y + 2.455) / s[1] - o[1]
    return sx / rs + 628, 1052 - (sy + 3.015) / rs

def srgb_encode(lin):
    lin = np.clip(lin, 0, 1)
    return np.where(lin <= .0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - .055)

def srgb_decode(v):
    return np.where(v <= .04045, v / 12.92, ((v + .055) / 1.055) ** 2.4)

PIVOT = np.array([0, -2.455, 0])
def model_to_screen(pts, s):
    """Original (unscaled) model points to screenshot pixels for a model scaled by s about the float point."""
    return to_screen(PIVOT + s * (np.asarray(pts) - PIVOT))
