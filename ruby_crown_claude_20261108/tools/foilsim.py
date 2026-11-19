"""CPU model of the foil backed ruby shader (mirrors the planned Metal code).

Each pixel: surface reflection of the sharp studio light, plus light that
refracts into the stone, reflects off the mirror foil at z = 0, and leaves
through the same facet plane (thin stone). Repeated internal reflections are
followed for a few bounces. Model space equals world space at rest.
"""
import sys
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from agx import agx

HERE = '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/tools'

def unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-15)

def reflect(d, n):
    return d - 2 * np.sum(d * n, axis=-1, keepdims=True) * n

def refract(d, n, eta):
    dot = np.sum(n * d, axis=-1)
    k = 1 - eta ** 2 * (1 - dot ** 2)
    out = eta * d - (eta * dot + np.sqrt(np.maximum(k, 0)))[..., None] * n
    return np.where((k >= 0)[..., None], out, 0)

def fresnel(c, ni, nt):
    c = np.clip(c, 0, 1)
    s = (ni / nt) ** 2 * (1 - c * c)
    ct = np.sqrt(np.maximum(1 - s, 0))
    a = (ni * c - nt * ct) / np.maximum(ni * c + nt * ct, 1e-12)
    b = (ni * ct - nt * c) / np.maximum(ni * ct + nt * c, 1e-12)
    return np.where(s >= 1, 1.0, (a * a + b * b) / 2)

class Studio:
    def __init__(self):
        rgb = np.load(HERE + '/studio.npz')['rgb'].astype(float)
        self.mips = [rgb]
        for _ in range(8):
            a = self.mips[-1]; h, w = a.shape[:2]
            self.mips.append(a[:h // 2 * 2, :w // 2 * 2].reshape(h // 2, 2, w // 2, 2, 3).mean((1, 3)))

    def sample(self, d, level):
        d = d * np.array([-1, 1, -1])
        u = (.5 + np.arctan2(d[..., 0], -d[..., 2]) / (2 * np.pi)) % 1
        v = .5 - np.arcsin(np.clip(d[..., 1], -1, 1)) / np.pi
        a = self.mips[level]; h, w = a.shape[:2]
        x = u * w - .5; y = np.clip(v * h - .5, 0, h - 1)
        x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
        y1 = np.minimum(y0 + 1, h - 1); fx = (x - x0)[..., None]; fy = (y - y0)[..., None]
        return (a[y0, x0 % w] * (1 - fx) * (1 - fy) + a[y0, (x0 + 1) % w] * fx * (1 - fy)
                + a[y1, x0 % w] * (1 - fx) * fy + a[y1, (x0 + 1) % w] * fx * fy)

    def sharp(self, d):
        return np.minimum(self.sample(d, 1), 24)

    def tent(self, d):
        return np.minimum(self.sample(d, 8), 3)

    def level(self, d, lv, clamp):
        lo = int(np.floor(lv)); hi = min(lo + 1, 8); f = lv - lo
        a = np.minimum(self.sample(d, lo), clamp)
        if f <= 1e-6: return a
        return a * (1 - f) + np.minimum(self.sample(d, hi), clamp) * f

STUDIO = None

def studio():
    global STUDIO
    if STUDIO is None:
        STUDIO = Studio()
    return STUDIO

DEFAULT = dict(ior=1.77, absorption=(0.35, 6.0, 1.6), foil=0.92, tent_gain=0.9, exposure=0.6, bounces=4,
               body_level=1.0, body_clamp=24.0, spec_clamp=24.0,
               glow=0.0, glow_color=(1.0, 0.02, 0.16), spec_gain=1.0)

def shade(p, n, d, prm=DEFAULT, deg=0.0):
    """p points, n outward facet normals, d view directions, all in MODEL space.
    deg is the turn about Y; light lookups use world directions."""
    st0 = studio()
    class W:
        def sharp(self, v): return st0.sharp(yaw(v, deg))
        def tent(self, v): return st0.tent(yaw(v, deg))
        def level(self, v, lv, c): return st0.level(yaw(v, deg), lv, c)
    st = W()
    ior = prm['ior']
    a = np.asarray(prm['absorption'], float)
    side = np.sign(p[..., 2:3]); side = np.where(side == 0, 1, side)
    cos = np.clip(-np.sum(n * d, -1), 0, 1)
    R = fresnel(cos, 1.0, ior)[..., None]
    color = prm.get('spec_gain', 1.0) * R * np.clip(st.sharp(reflect(d, n)) - prm.get('spec_floor', 0.0), 0, prm['spec_clamp'])
    t = refract(d, n, 1 / ior)
    pos = p.copy(); direction = t; weight = np.repeat(1 - R, 3, axis=-1); path = np.zeros(p.shape[:-1])
    for _ in range(prm['bounces']):
        dz = direction[..., 2]
        dist = np.where(dz * side[..., 0] < -1e-4, -pos[..., 2] / np.where(dz == 0, 1, dz), 0)
        dist = np.maximum(np.nan_to_num(dist), 0)
        pos = pos + direction * dist[..., None]; path = path + dist
        direction = direction * np.array([1, 1, -1]); weight = weight * prm['foil']
        approach = np.sum(n * direction, -1)
        dist2 = np.where(approach > 1e-4, np.sum(n * (p - pos), -1) / np.maximum(approach, 1e-4), 0)
        dist2 = np.maximum(np.nan_to_num(dist2), 0)
        pos = pos + direction * dist2[..., None]; path = path + dist2
        Rin = fresnel(approach, ior, 1.0)[..., None]
        out = refract(direction, -n, ior)
        light = st.level(out, prm['body_level'], prm['body_clamp']) + st.tent(out) * prm['tent_gain']
        color = color + weight * np.exp(-a * (np.minimum(path, 12) + prm.get('path_base', 0.0))[..., None]) * (1 - Rin) * light
        weight = weight * Rin
        direction = reflect(direction, n)
    color = color + weight * np.exp(-a * (np.minimum(path, 12) + prm.get('path_base', 0.0))[..., None]) * st.tent(direction) * prm['tent_gain']
    color = color + (1 - R) * prm['glow'] * np.asarray(prm['glow_color'])
    return color * prm['exposure']

def display(lin):
    return np.clip(agx(lin), 0, 1)

EYE = np.array([0, 1.8, 23.0])

def yaw(v, deg):
    c, s = np.cos(np.radians(deg)), np.sin(np.radians(deg))
    Rm = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return v @ Rm.T
