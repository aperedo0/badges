"""Crops a transparent badge render (1080 x 1440 master frame at 200%) to the tier-art frame at the fixed Home scale:
the square the app's flat badge frame uses, centered on the coin's center (master row 656, column 540) with side
586 * 120 / 108 master pixels (a 6.03 unit coin spans 108 of 120). Any badge, round or not, lands where its 3D model
sits on Home. Writes a 600 x 600 RGBA PNG, resized in premultiplied alpha.
Usage: /usr/local/bin/python3 make_still_fixed.py <render.png> <out.png>"""
import sys
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGBA'); k = im.width / 1080
cx, cy, side = 540 * k, 656 * k, 586 * 120 / 108 * k
box = (round(cx - side / 2), round(cy - side / 2), round(cx + side / 2), round(cy + side / 2))
im.crop(box).convert('RGBa').resize((600, 600), Image.LANCZOS).convert('RGBA').save(out, optimize=True)
print(out, 'crop', box)
