import sys, json
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/tools')
import crown, facets, foilsim
from PIL import Image
ROOT = '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107'
fit = json.load(open(sys.argv[1]))
z = np.array([fit['heights'][k] if k in fit['heights'] else fit['heights'][k[:-1]] for k in crown.NAMES])
prm = dict(fit['prm']); prm['absorption'] = tuple(prm['absorption'])
rc = crown.raster(420, extent=(-2.6, 2.6, -2.1, 2.55))
panels = []
for deg in [0] + [float(a) for a in sys.argv[3:]]:
    img = crown.render(z, prm, deg=deg, raster_cache=rc)
    panels.append(Image.fromarray(np.uint8(img * 255)))
ref = Image.open(ROOT + '/reference.png').convert('RGB')
# reference crop matching the raster extent
x0, y1 = facets.to_ref((-2.6, 2.55)); x1, y0 = facets.to_ref((2.6, -2.1))
refc = ref.crop((int(x0), int(y1), int(x1), int(y0))).resize(panels[0].size)
W = panels[0].width; H = panels[0].height
out = Image.new('RGB', (W * (len(panels) + 1), H))
out.paste(refc, (0, 0))
for i, p in enumerate(panels):
    out.paste(p, (W * (i + 1), 0))
out.save(sys.argv[2])
