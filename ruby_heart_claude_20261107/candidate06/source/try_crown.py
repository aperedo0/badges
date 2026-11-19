import sys, json
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/tools')
import crown, facets
from PIL import Image
names = crown.NAMES; half = crown.HALF
ZG = 0.18
H = dict(B=.40, C=.36, D=.50, E=.50, H=.34, P1=.46, P2=.52, P3=.32, Q=.38, c1=.46, c2=.60, c3=.52, c4=.34)
z = np.array([ZG if crown.GIRDLE[i] else H[names[i]] for i in half])
rc = crown.raster(500)
img = crown.render(crown.full_heights(z), raster_cache=rc)
Image.fromarray(np.uint8(img * 255)).save(sys.argv[1])
n, w, r = crown.planes(crown.full_heights(z))
print('max nonplanar', r.max().round(4), 'max tilt deg', np.degrees(np.arccos(n[:, 2])).max().round(1))
