"""rim_metric.py <png>...: how much brighter the badge's outermost 2 px band is than the band 3 to 6 px inside (Home shot, badge area).
Above 1.0 means a bright rim along the outline. Also the share of outline pixels that are near white."""
import sys, numpy as np
from PIL import Image
from scipy.ndimage import binary_erosion
for p in sys.argv[1:]:
    a = np.asarray(Image.open(p).convert('RGB')).astype(float)[330:830, 300:906]; L = a.mean(-1)
    m = L > 55
    m = binary_erosion(binary_erosion(m, iterations=1) == False, iterations=0) == False if False else m
    e1 = binary_erosion(m, iterations=2); e2 = binary_erosion(m, iterations=6)
    rim = m & ~e1; inner = e1 & ~e2
    white = (a.min(-1) > 215) & rim
    print(f'{p.split("/")[-1]:24s} rim/inner {L[rim].mean() / L[inner].mean():.3f}   near-white outline share {white.sum() / rim.sum():.3f}')
