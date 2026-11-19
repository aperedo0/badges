from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
from reference_projection import CrownReference
R=Path(__file__).resolve().parent;B=R/'ruby_crown/candidate10';C=R/'ruby_crown/candidate11';base=np.load(B/'geometry.npz');groups=json.loads((B/'groups.json').read_text());projector=CrownReference(base,groups,627,1022,1010)
d=np.load(C/'geometry.npz');g=json.loads((C/'groups.json').read_text());im=Image.open(R/'ruby_crown/reference.png').convert('RGBA');ink=Image.new('RGBA',im.size);draw=ImageDraw.Draw(ink)
for i,a in enumerate(g):
 if not a['name'].startswith('Ruby measured closed acanthus leaf 1 -1 '):continue
 p=projector.pixel(d[f'{i}_points']);t=d[f'{i}_triangles']
 for tri in t:draw.polygon([tuple(q) for q in p[tri]],fill=(0,220,255,130))
Image.alpha_composite(im,ink).crop((120,595,610,880)).resize((980,570)).save(C/'review/projected_leaf_overlay.png')
