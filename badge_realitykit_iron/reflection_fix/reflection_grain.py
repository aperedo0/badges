"""Fine-texture energy in the floor reflection and on the coin's lower rim, from an app screenshot (iPhone 17 sim, coin at rest).
Usage: /usr/local/bin/python3 reflection_grain.py <shot.png> [...]
refl_grain: std of (image - 2px blur) in the reflection band just under the contact (rows 806-880, x 380-826, 3x px)
rim_grain:  same on the coin's lower rim above the contact (rows 700-795, outside the inset circle)"""
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
for p in sys.argv[1:]:
    x = np.asarray(Image.open(p).convert('L')).astype(float)
    hp = x - gaussian_filter(x, 2.0)
    refl = hp[806:880, 380:826]
    yy, xx = np.mgrid[700:795, 380:826]
    ring = ((xx - 603) ** 2 + (yy - 575) ** 2 > 200 ** 2)      # outside the inset: the rim band
    rim = hp[700:795, 380:826][ring]
    print(f"{p.split('/')[-1]}: refl_grain={refl.std():.2f} rim_grain={rim.std():.2f}")
