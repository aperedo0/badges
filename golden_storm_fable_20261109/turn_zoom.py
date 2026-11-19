"""3x zooms of the badge while it turns, to look for specks and flashing edges. Usage: turn_zoom.py candidateNN"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
C = Path(__file__).resolve().parent / sys.argv[1]
tiles = []
for pose in ['early_turn', 'turn45', 'turn135', 'back']:
    f = Image.open(C / 'app' / (pose + '.png')).convert('RGB'); a = np.asarray(f).astype(int)
    sat = ((a.max(2) - a.min(2)) > 45) & (a.max(2) > 90)
    sat[:, :300] = False; sat[:, 900:] = False; sat[:110] = False
    rows = np.nonzero(sat.sum(1) > 3)[0]
    start = rows[0]; end = start
    for r in rows[1:]:
        if r - end > 25:
            break
        end = r
    cols = np.nonzero(sat[start:end + 1].sum(0) > 0)[0]
    box = (cols.min() - 14, start - 14, cols.max() + 14, end + 14)
    t = f.crop(box); t = t.resize((t.size[0] * 3, t.size[1] * 3), Image.NEAREST); tiles.append(t)
W = sum(t.size[0] for t in tiles) + 10 * len(tiles); H = max(t.size[1] for t in tiles)
sheet = Image.new('RGB', (W, H), (255, 0, 255)); x = 0
for t in tiles:
    sheet.paste(t, (x, 0)); x += t.size[0] + 10
sheet.save(C / 'finish_turning_3x.png'); print(sheet.size)
