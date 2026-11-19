import sys
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/tools')
import numpy as np
from PIL import Image, ImageDraw
import facets
names, xy, girdle, faces = facets.layout()
ref = Image.open('/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/reference.png').convert('RGB')
d = ImageDraw.Draw(ref)
for f in faces:
    pts = [tuple(facets.to_ref(xy[i])) for i in f]
    d.line(pts + [pts[0]], fill=(0, 255, 255), width=2)
for n, p in zip(names, xy):
    r = facets.to_ref(p)
    d.text((r[0] + 4, r[1] - 12), n, fill=(255, 255, 0))
ref.crop((150, 150, 1100, 1060)).save(sys.argv[1])
print(len(names), 'vertices', len(faces), 'faces')
