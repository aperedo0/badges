"""One picture of every captured pose of a candidate. Usage: contact.py candidateNN"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
C = Path(__file__).resolve().parent / sys.argv[1]
poses = ['front', 'early_turn', 'turn45', 'side_left', 'turn135', 'back', 'turn225', 'side_right', 'turn315']
SCROLL = dict(front=0, early_turn=68, turn45=75.1, side_left=94.25, turn135=113.4, back=132.5, turn225=151.6, side_right=170.76, turn315=189.9)
tiles = []
for p in poses:
    f = C / 'app' / (p + '.png')
    if not f.exists():
        continue
    up = int(round(SCROLL[p] * 3))                      # the page scrolls up as the badge turns
    top = max(0, 300 - up)
    im = Image.open(f).convert('RGB').crop((330, top, 880, top + 620)).resize((385, 434), Image.LANCZOS)
    ImageDraw.Draw(im).text((8, 8), p, fill=(255, 255, 0)); tiles.append(im)
cols = 5; rows = (len(tiles) + cols - 1) // cols
sheet = Image.new('RGB', (cols * 390, rows * 439), (10, 10, 10))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % cols) * 390, (i // cols) * 439))
sheet.save(C / 'all_sides.png'); print(sheet.size)
