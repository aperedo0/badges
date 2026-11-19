"""The mockup next to the simulator at the same badge height. Usage: side_by_side.py candidateNN"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
R = Path(__file__).resolve().parent; C = R / sys.argv[1]
f = Image.open(C / 'app/front.png').convert('RGB')
x0, x1, y0, y1 = 394, 810, 358, 778                      # the badge on the simulator screen
pad = 46; k = 2
app = f.crop((x0 - pad, y0 - pad, x1 + pad, y1 + pad)); app = app.resize((app.size[0] * k, app.size[1] * k), Image.LANCZOS)
seg = np.load(R / 'work/seg_raw.npz')['sil']; ys, xs = np.nonzero(seg)
mock = Image.open(R / 'reference/mockup.png').convert('RGB')
s = (y1 - y0) * k / (ys.max() - ys.min())
mk = mock.resize((int(mock.size[0] * s), int(mock.size[1] * s)), Image.LANCZOS)
H = app.size[1]; out = Image.new('RGB', (mk.size[0] + app.size[0] + 24, H), (16, 16, 16))
top = int(pad * k - ys.min() * s)
out.paste(mk, (0, top)); out.paste(app, (mk.size[0] + 24, 0)); out.save(C / 'side_by_side.png'); print(out.size)
