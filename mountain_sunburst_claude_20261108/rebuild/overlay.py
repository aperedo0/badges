"""Checkpoint 1: every design shape over the mockup, colored by part, plus 3x crops of five areas."""
import json
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent
D = json.load(open(HERE / 'design.json'))
a = Image.open(HERE.parent / 'reference/mockup.png').convert('RGB')
ov = Image.blend(a, Image.new('RGB', a.size), 0.35)
S = 2
big = ov.resize((a.width * S, a.height * S), Image.LANCZOS); d = ImageDraw.Draw(big)
COL = {'red': (255, 80, 60), 'lemon': (255, 240, 0), 'spike': (255, 0, 255), 'mountain': (0, 255, 255), 'cell': (120, 255, 120),
       'cloud': (255, 255, 255), 'gold': (255, 150, 0), 'frame': (255, 0, 120), 'gem': (0, 160, 255), 'ring': (180, 180, 255)}
def draw(shape, col, w=2):
    for q in shape:
        for ring in [q['exterior']] + q['holes']:
            pts = [(x * S, y * S) for x, y in ring]
            d.line(pts + [pts[0]], fill=col, width=w)
for c in D['plate_cells']:
    draw(c['shape'], COL['red'] if c['color'] == 'red' else COL['lemon'])
for s in D['spikes']:
    draw(s['shape'], COL['spike'], 3)
for m in D['mountains'].values():
    draw(m['outline'], COL['mountain'], 3)
    for c in m['cells']:
        draw(c['shape'], COL['cell'])
for c in D['cloud_cells']:
    draw(c, COL['cloud'])
draw(D['lower_gold'], COL['gold'])
draw(D['frame'], COL['frame'], 3)
draw([dict(exterior=D['gem']['outline'], holes=[])], COL['gem'], 3)
for cx, cy, r in ((*D['ring']['center'], D['ring']['r_outer']), (*D['ring']['center'], D['ring']['r_inner']), (*D['sun']['center'], D['sun']['r_rim']), (*D['sun']['center'], D['sun']['r_enamel'])):
    d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), outline=COL['ring'], width=2)
big.resize((a.width, a.height), Image.LANCZOS).save(HERE / 'review/design_overlay.png')
for name, (x0, y0, x1, y1) in dict(top_spike_ring=(540, 0, 770, 200), side_spike_crossing=(60, 470, 330, 660), central_mountain=(380, 460, 930, 820),
                                    cloud_curl=(60, 760, 460, 1040), bottom_tip=(450, 820, 860, 1190)).items():
    big.crop((x0 * S, y0 * S, x1 * S, y1 * S)).resize(((x1 - x0) * 3, (y1 - y0) * 3), Image.LANCZOS).save(HERE / f'review/cp1_{name}.png')
print('overlay written')
