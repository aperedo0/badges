"""8x close ups of named trouble spots in a candidate's front capture. Usage: spots.py candidateNN"""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
C = Path(__file__).resolve().parent / sys.argv[1]
app = Image.open(C / 'app/front.png').convert('RGB')
meta = json.load(open(C / 'parts.json')); S = meta['units_per_pixel']; CX = meta['center_x']; TOP = meta['top']; bmin, bmax = meta['bounds_min'], meta['bounds_max']
a = np.asarray(app).astype(float) / 255; reg = a[300:850, 300:900]; mm = ((reg.max(2) - reg.min(2)) > .16) & (reg.max(2) > .35)
cols = np.nonzero(mm.any(0))[0]; rows = np.nonzero(mm.any(1))[0]; x0, x1, y0 = cols.min() + 300, cols.max() + 300, rows.min() + 300
ppu = (x1 - x0) / (bmax[0] - bmin[0])
SPOTS = dict(bolt_top=(590, 300), outline_corner=(930, 952), pearl_low=(401, 929), pearl_up=(903, 317), bottom_point=(627, 1130), right_point=(1140, 600),
             left_point=(112, 596), top_point=(627, 110), spiral_tip=(715, 384), bolt_tip=(428, 960), ribbons_right=(880, 720), ribbons_left=(330, 470))
if len(sys.argv) > 2:
    SPOTS = {k: SPOTS[k] for k in sys.argv[2].split(',')}
R = 22; P = 352; n = len(SPOTS); ncol = 4
sheet = Image.new('RGB', (ncol * (P + 6), ((n + ncol - 1) // ncol) * (P + 6)), (255, 0, 255))
for i, (k, (px, py)) in enumerate(SPOTS.items()):
    sx = x0 + ((px - CX) * S - bmin[0]) * ppu; sy = y0 + (bmax[1] - (3.015 - (py - TOP) * S)) * ppu
    t = app.crop((int(sx - R), int(sy - R), int(sx + R), int(sy + R))).resize((P, P), Image.NEAREST)
    ImageDraw.Draw(t).text((4, 4), k, fill=(255, 255, 0))
    sheet.paste(t, ((i % ncol) * (P + 6), (i // ncol) * (P + 6)))
sheet.save(C / 'zoom_spots.png'); print(sheet.size)
