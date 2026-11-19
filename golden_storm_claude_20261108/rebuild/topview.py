"""Flat top view of a pieces file as the build will show it from straight above: each piece's metal, then each fill's
colored floor (a sunken fill's slope stays metal). Beside the mockup, in crops. Python 3.11.
Usage: topview.py PIECES.json MOCKUP.png OUT_DIR name:x0,y0,x1,y1 ..."""
import sys, json
from pathlib import Path
from PIL import Image, ImageDraw
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
P = json.load(open(sys.argv[1])); mock = Image.open(sys.argv[2]).convert('RGB'); OUT = Path(sys.argv[3]); OUT.mkdir(parents=True, exist_ok=True)
COL = {'Field': (40, 38, 100), 'Ribbon': (120, 170, 225), 'Pearl': (235, 225, 225), 'BoltLight': (250, 225, 90), 'BoltDeep': (240, 175, 30), 'Side': (90, 60, 20)}
GOLD = (200, 150, 50)
geo = lambda s: unary_union([Polygon(q['exterior'], q['holes']).buffer(0) for q in s]) if s else Polygon()
S2 = 2; img = Image.new('RGB', (mock.width * S2, mock.height * S2), (235, 235, 235)); d = ImageDraw.Draw(img)
def fill(g, col):
    """Paint a shape with its holes left open (a gold island inside a fill stays visible)."""
    mk = Image.new('L', img.size, 0); dm = ImageDraw.Draw(mk)
    for q in (g.geoms if isinstance(g, MultiPolygon) else [g]):
        if q.is_empty: continue
        dm.polygon([(x * S2, y * S2) for x, y in q.exterior.coords], fill=255)
        for h in q.interiors: dm.polygon([(x * S2, y * S2) for x, y in h.coords], fill=0)
    img.paste(Image.new('RGB', img.size, col), (0, 0), mk)
def paint(g, col):          # polygons with holes: paint, then repaint holes with what is under (approximate: holes drawn later)
    fill(g, col)
for pc in P['pieces']:
    if pc['name'] == 'core': continue
    out = geo(pc['outline']); fill(out, COL.get(pc['material'], GOLD))
    for c in pc.get('cells', []):
        g = geo(c['shape']).intersection(out)
        if c.get('recess'): g = g.buffer(-c['recess']['width'])
        fill(g, COL.get(c['material'], GOLD))
    # holes in outlines and cells are drawn by redrawing what lies beneath is skipped: holes appear as the piece color
small = img.resize(mock.size, Image.LANCZOS); small.save(OUT / 'topview.png')
for arg in sys.argv[4:]:
    n, box = arg.split(':'); x0, y0, x1, y1 = map(int, box.split(','))
    a = mock.crop((x0, y0, x1, y1)).resize(((x1 - x0) * 2, (y1 - y0) * 2), Image.LANCZOS)
    b = img.crop((x0 * S2, y0 * S2, x1 * S2, y1 * S2))
    o = Image.new('RGB', (a.width * 2 + 8, a.height), (0, 0, 0)); o.paste(a, (0, 0)); o.paste(b, (a.width + 8, 0)); o.save(OUT / f'top_{n}.png')
print('written', OUT)
