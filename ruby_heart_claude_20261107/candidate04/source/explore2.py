"""Hand designed dome + optics variants, front and turned, beside the per facet reference means."""
import sys, json
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/tools')
import crown, facets, foilsim, fit_crown as F
from PIL import Image, ImageDraw
from matplotlib.path import Path as MPath
rc = crown.raster(230, extent=(-2.5, 2.5, -2.0, 2.45))
X, Y, face = rc
# per facet reference means as a flat image
tgt = np.zeros(X.shape + (3,)) + 0.04
for i in range(len(crown.FACES)):
    tgt[face == i] = F.target[i]
H0 = dict(B=.36, C=.30, D=.46, E=.46, H=.32, P1=.44, P2=.50, P3=.30, Q=.38, c1=.44, c2=.56, c3=.48, c4=.34)
def heights(H):
    return crown.full_heights(np.array([0.18 if crown.GIRDLE[i] else H[crown.NAMES[i]] for i in crown.HALF]))
variants = json.loads(sys.argv[2])
angles = [0, 20, 45]
W = X.shape[1]; Hh = X.shape[0]
out = Image.new('RGB', (W * (len(angles) + 1), Hh * len(variants)))
dr = ImageDraw.Draw(out)
for r, v in enumerate(variants):
    out.paste(Image.fromarray(np.uint8(tgt * 255)), (0, r * Hh))
    prm = dict(foilsim.DEFAULT, **v)
    z = heights(dict(H0, **v.get('H', {})))
    prm.pop('H', None)
    for c, a in enumerate(angles):
        img = crown.render(z, prm, deg=a, raster_cache=rc)
        out.paste(Image.fromarray(np.uint8(img * 255)), ((c + 1) * W, r * Hh))
    dr.text((W + 4, r * Hh + 4), json.dumps({k: v[k] for k in v if k != 'H'})[:60], fill=(255, 255, 0))
out.save(sys.argv[1])
