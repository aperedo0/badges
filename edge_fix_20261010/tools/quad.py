"""quad.py <before.png> <after.png> <out.png> : the whole badge at 2x nearest, split into four quadrants; each row is before | after."""
import sys, numpy as np
from PIL import Image
b = Image.open(sys.argv[1]).convert('RGB'); a = Image.open(sys.argv[2]).convert('RGB')
x = np.asarray(b).astype(int)[300:900, 300:906]; m = x.mean(-1) > 55; ys, xs = np.nonzero(m)
y0, y1, x0, x1 = 300 + ys.min() - 4, 300 + ys.max() + 4, 300 + xs.min() - 4, 300 + xs.max() + 4
ym, xm = (y0 + y1) // 2, (x0 + x1) // 2
boxes = [(x0, y0, xm, ym), (xm, y0, x1, ym), (x0, ym, xm, y1), (xm, ym, x1, y1)]
w = max(bx[2] - bx[0] for bx in boxes) * 2; h = max(bx[3] - bx[1] for bx in boxes) * 2
out = Image.new('RGB', (w * 2 + 10, (h + 10) * 4), (0, 0, 0))
for r, bx in enumerate(boxes):
    sz = ((bx[2] - bx[0]) * 2, (bx[3] - bx[1]) * 2)
    out.paste(b.crop(bx).resize(sz, Image.NEAREST), (0, r * (h + 10))); out.paste(a.crop(bx).resize(sz, Image.NEAREST), (w + 10, r * (h + 10)))
out.save(sys.argv[3])
