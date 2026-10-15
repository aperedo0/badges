"""quads.py <out_prefix> <box x0,y0,x1,y1> <zoom> <a.png> <b.png> : split the box into 2x2 quadrants; for each, a and b side by side."""
import sys
from PIL import Image
pre, box, z, a, b = sys.argv[1], list(map(int, sys.argv[2].split(','))), int(sys.argv[3]), sys.argv[4], sys.argv[5]
A = Image.open(a).convert('RGB'); B = Image.open(b).convert('RGB'); x0, y0, x1, y1 = box; mx, my = (x0 + x1) // 2, (y0 + y1) // 2
for n, q in enumerate([(x0, y0, mx, my), (mx, y0, x1, my), (x0, my, mx, y1), (mx, my, x1, y1)]):
    w, h = q[2] - q[0], q[3] - q[1]; s = Image.new('RGB', (2 * w * z + 6, h * z), 'white')
    s.paste(A.crop(q).resize((w * z, h * z), Image.Resampling.NEAREST), (0, 0)); s.paste(B.crop(q).resize((w * z, h * z), Image.Resampling.NEAREST), (w * z + 6, 0))
    s.save(f'{pre}_q{n}.png')
