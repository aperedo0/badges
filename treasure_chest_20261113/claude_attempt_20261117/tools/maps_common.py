"""Shared helpers for the procedural wood and iron maps (numpy only, no bpy)."""
import struct
import zlib

import numpy as np


def write_png(path, arr):
    """arr: HxW or HxWx3, uint8 or uint16. Row 0 is the top of the image."""
    arr = np.ascontiguousarray(arr)
    h, w = arr.shape[:2]
    ch = 1 if arr.ndim == 2 else arr.shape[2]
    ct = {1: 0, 3: 2, 4: 6}[ch]
    bd = 8 * arr.dtype.itemsize
    raw = arr.astype(">u2" if bd == 16 else "u1").reshape(h, -1)
    raw = np.ascontiguousarray(raw).view(np.uint8).reshape(h, -1)
    data = np.concatenate([np.zeros((h, 1), np.uint8), raw], axis=1).tobytes()

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, bd, ct, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(data, 4)))
        f.write(chunk(b"IEND", b""))


def _gauss_filter(shape, sy, sx):
    fy = np.fft.fftfreq(shape[0])[:, None]
    fx = np.fft.rfftfreq(shape[1])[None, :]
    return np.exp(-2 * np.pi**2 * ((fy * sy) ** 2 + (fx * sx) ** 2)).astype(np.float32)


def blur(a, sy, sx=None):
    """Periodic gaussian blur, sigma in pixels."""
    sx = sy if sx is None else sx
    return np.fft.irfft2(np.fft.rfft2(a) * _gauss_filter(a.shape, sy, sx), s=a.shape).astype(np.float32)


def fnoise(shape, sy, sx, seed):
    """Smooth periodic noise with unit standard deviation; sigma in pixels."""
    rng = np.random.default_rng(seed)
    wn = rng.standard_normal(shape, dtype=np.float32)
    out = np.fft.irfft2(np.fft.rfft2(wn) * _gauss_filter(shape, sy, sx), s=shape)
    out -= out.mean()
    return (out / out.std()).astype(np.float32)


def fnoise1(n, s, seed):
    return fnoise((1, n), 0.0, s, seed)[0]


def sample(T, yy, xx):
    """Bilinear lookup with wrap; yy, xx in pixel coordinates of T."""
    h, w = T.shape
    y0 = np.floor(yy).astype(np.int64)
    x0 = np.floor(xx).astype(np.int64)
    fy = (yy - y0).astype(np.float32)
    fx = (xx - x0).astype(np.float32)
    y0 %= h
    x0 %= w
    y1 = (y0 + 1) % h
    x1 = (x0 + 1) % w
    return (T[y0, x0] * (1 - fy) * (1 - fx) + T[y0, x1] * (1 - fy) * fx
            + T[y1, x0] * fy * (1 - fx) + T[y1, x1] * fy * fx)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def lin2srgb(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def ramp(t, stops):
    """Piecewise linear color ramp. stops: [(pos, (r,g,b)), ...] ascending."""
    pos = np.array([s[0] for s in stops], np.float32)
    col = np.array([s[1] for s in stops], np.float32)
    t = np.clip(t, pos[0], pos[-1])
    out = np.empty(t.shape + (3,), np.float32)
    for c in range(3):
        out[..., c] = np.interp(t, pos, col[:, c])
    return out


def to8(a):
    return np.clip(a * 255.0 + 0.5, 0, 255).astype(np.uint8)


def to16(a):
    return np.clip(a * 65535.0 + 0.5, 0, 65535).astype(np.uint16)
