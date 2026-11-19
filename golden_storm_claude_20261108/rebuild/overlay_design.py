"""Checkpoint 1: every measured shape over the mockup, full view and crops. Python 3.11."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent
D = json.load(open(HERE / 'design.json')); mo = Image.open(HERE.parent / 'reference/mockup.png').convert('RGB')
dr = ImageDraw.Draw(mo)
def draw(shape, col, w=2):
    for q in shape:
        dr.line([tuple(x) for x in q['exterior']], fill=col, width=w)
        for h in q['holes']: dr.line([tuple(x) for x in h], fill=col, width=w)
draw(D['silhouette'], (255, 0, 0)); draw(D['field_cell'], (0, 255, 0))
for r in D['ribbons']: draw(r['outline'], (255, 0, 255)); draw(r['fill'], (0, 255, 255), 1)
for c in D['clouds'].values(): draw(c['plate'], (255, 128, 0)); draw(c['fills'], (0, 0, 255), 1)
draw(D['bolt']['outline'], (255, 255, 0), 2)
for k, v in D['bolt']['vertices'].items(): x, y = v; dr.ellipse([x - 5, y - 5, x + 5, y + 5], outline=(255, 0, 0), width=2); dr.text((x + 6, y), k, fill=(255, 0, 0))
for p in D['points'].values():
    dr.line([tuple(p['a']), tuple(p['tip']), tuple(p['b'])], fill=(0, 128, 255), width=3)
mo.save(HERE / 'review/design_overlay.png')
crops = [(c.split(':')[0], [int(v) for v in c.split(':')[1].split(',')]) for c in sys.argv[1:]]
for name, (x0, y0, x1, y1) in crops:
    mo.crop((x0, y0, x1, y1)).resize(((x1 - x0) * 2, (y1 - y0) * 2), Image.NEAREST).save(HERE / f'review/overlay_{name}.png')
