import sys, json
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/tools')
import crown, foilsim
from PIL import Image, ImageDraw
H = dict(B=.30, C=.30, D=.46, E=.46, H=.32, P1=.45, P2=.52, P3=.30, Q=.36, c1=.42, c2=.55, c3=.48, c4=.32)
ZG = 0.18
z = crown.full_heights(np.array([ZG if crown.GIRDLE[i] else H[crown.NAMES[i]] for i in crown.HALF]))
rc = crown.raster(260, extent=(-2.6, 2.6, -2.1, 2.55))
variants = [
    dict(body_level=1.0, spec_clamp=24, absorption=(0.10, 6.0, 1.0), exposure=0.45, tent_gain=0.9),
    dict(body_level=3.0, spec_clamp=8, absorption=(0.10, 6.0, 1.0), exposure=0.45, tent_gain=0.9),
    dict(body_level=4.5, spec_clamp=8, absorption=(0.10, 6.0, 1.0), exposure=0.55, tent_gain=0.9),
    dict(body_level=5.5, spec_clamp=8, absorption=(0.10, 6.0, 1.0), exposure=0.7, tent_gain=0.6),
]
angles = [0, 20, 45, 70]
W = 260; Hh = rc[0].shape[0]
out = Image.new('RGB', (W * len(angles), Hh * len(variants)))
d = ImageDraw.Draw(out)
for r, v in enumerate(variants):
    prm = dict(foilsim.DEFAULT, **v)
    for c, a in enumerate(angles):
        img = crown.render(z, prm, deg=a, raster_cache=rc)
        out.paste(Image.fromarray(np.uint8(img * 255)), (c * W, r * Hh))
    d.text((4, r * Hh + 4), f"blur {v['body_level']} spec {v['spec_clamp']}", fill=(255, 255, 0))
out.save(sys.argv[1])
