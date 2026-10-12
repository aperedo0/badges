"""Rim evenness: for each angle (every 10 deg), the rim band's mean luma and how much of the band is dark (< 90).
A rim that 'thins' has angles where much of the band is dark. Usage: /usr/local/bin/python3 rim_even.py <png> [...]"""
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
cx, cy = 602.0, 587.0
rs = np.arange(205, 229, 1.0)
for p in sys.argv[1:]:
    x = np.asarray(Image.open(p).convert('L')).astype(float)
    means, dark = [], []
    for a in range(0, 360, 10):
        if 250 < a < 290: continue       # skip the floor contact at the bottom
        t = np.deg2rad(a)
        v = map_coordinates(x, [cy - rs * np.sin(t), cx + rs * np.cos(t)], order=1)
        means.append(v.mean()); dark.append((v < 90).mean())
    means, dark = np.array(means), np.array(dark)
    print(f"{p.split('/')[-1]:28s} band mean min {means.min():5.1f} max {means.max():5.1f} spread {means.max()-means.min():5.1f} | worst dark share {dark.max():.2f} mean dark share {dark.mean():.2f}")
