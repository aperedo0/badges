"""Read what a part of a mockup is made of: sample colors across it along a line. Python 3.11.

Usage: pixel_profile.py MOCKUP.png x0,y0 x1,y1 [step]
Prints one letter per sample: Y lemon or yellow enamel, R red, B blue, W white or highlight, g gold metal, . other.
Use it when a written description and the picture could disagree (a spike that looks gold may be lemon inside).
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
img = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float) / 255
img = np.stack([ndi.median_filter(img[..., k], size=3) for k in range(3)], -1)
(x0, y0), (x1, y1) = [tuple(map(float, a.split(','))) for a in sys.argv[2:4]]; step = float(sys.argv[4]) if len(sys.argv) > 4 else 2
n = int(np.hypot(x1 - x0, y1 - y0) / step) + 1; out = ''
for t in np.linspace(0, 1, n):
    x, y = int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t)); r, g, b = img[y, x]
    mx, mn = max(r, g, b), min(r, g, b); s = (mx - mn) / max(mx, 1e-6); d = max(mx - mn, 1e-6)
    h = (((g - b) / d) % 6 if mx == r else ((b - r) / d + 2 if mx == g else (r - g) / d + 4)) * 60
    out += 'W' if s < 0.25 and mx > 0.75 else 'R' if (h < 22 or h > 340) and s > 0.45 else 'Y' if 40 <= h < 60 and s > 0.85 and mx > 0.9 else 'g' if 22 <= h < 62 else 'B' if 180 <= h < 260 else '.'
print(out)
