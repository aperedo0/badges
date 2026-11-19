"""Draw every piece of a pieces file over the mockup (checkpoint 1), plus 3x crops. Python 3.11.

Usage: overlay.py PIECES.json MOCKUP.png OUT_DIR [name:x0,y0,x1,y1 ...]
"""
import sys, json
from pathlib import Path
from PIL import Image, ImageDraw
P = json.load(open(sys.argv[1])); a = Image.open(sys.argv[2]).convert('RGB'); OUT = Path(sys.argv[3]); OUT.mkdir(parents=True, exist_ok=True)
S2 = 2; big = Image.blend(a, Image.new('RGB', a.size), 0.35).resize((a.width * S2, a.height * S2), Image.LANCZOS); d = ImageDraw.Draw(big)
cols = [(255, 0, 255), (0, 255, 255), (255, 255, 0), (120, 255, 120), (255, 140, 0), (80, 160, 255), (255, 80, 80), (255, 255, 255)]
for i, pc in enumerate(P['pieces']):
    c = cols[i % len(cols)]
    for q in pc['outline']:
        for ring in [q['exterior']] + q.get('holes', []):
            pts = [(x * S2, y * S2) for x, y in ring]; d.line(pts + [pts[0]], fill=c, width=2)
    for cell in pc.get('cells', []):
        for q in cell['shape']:
            pts = [(x * S2, y * S2) for x, y in q['exterior']]; d.line(pts + [pts[0]], fill=c, width=1)
    x, y = pc['outline'][0]['exterior'][0]; d.text((x * S2, y * S2), pc['name'], fill=c)
big.resize(a.size, Image.LANCZOS).save(OUT / 'pieces_overlay.png')
for arg in sys.argv[4:]:
    n, box = arg.split(':'); x0, y0, x1, y1 = map(int, box.split(','))
    big.crop((x0 * S2, y0 * S2, x1 * S2, y1 * S2)).resize(((x1 - x0) * 3, (y1 - y0) * 3), Image.LANCZOS).save(OUT / f'overlay_{n}.png')
print('written', OUT / 'pieces_overlay.png')
