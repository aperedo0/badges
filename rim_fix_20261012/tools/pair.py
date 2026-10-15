"""pair.py <out.png> <box x0,y0,x1,y1> <zoom> <img>... : same crop of several screenshots side by side, nearest neighbour zoom."""
import sys
from PIL import Image
out, box, z, files = sys.argv[1], tuple(map(int, sys.argv[2].split(','))), int(sys.argv[3]), sys.argv[4:]
ims = [Image.open(f).convert('RGB').crop(box) for f in files]; w, h = ims[0].size
s = Image.new('RGB', (w * z * len(ims) + 8 * (len(ims) - 1), h * z), (255, 255, 255))
for i, im in enumerate(ims): s.paste(im.resize((w * z, h * z), Image.Resampling.NEAREST), (i * (w * z + 8), 0))
s.save(out)
