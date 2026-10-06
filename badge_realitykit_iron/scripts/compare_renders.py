"""Pixel differences between two export renders (same camera, rig and pose), by region.

  python compare_renders.py <renders folder> <out.json> <sheet folder>

Regions (1080 x 1440 master frame): the gem, the coin's bottom rim above the floor line
(rows 860 to 930; the floor contact line is at rows 932 to 956 for poses 0 and 20), the
rim crop including the floor contact and the floor below it (rows 860 to 1000), and the
whole rendered frame. Values are 8-bit channel levels (0 to 255).
Also writes one sheet per rig and pose: v2 | v3 | |v3 - v2| x 32.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

renders, out_json, sheets = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
REGIONS = {
    'gem': (400, 440, 690, 880),
    'bottom_rim_above_floor': (380, 860, 700, 930),
    'bottom_rim_with_floor_contact': (380, 860, 700, 1000),
    'whole_frame': (0, 0, 1080, 1440),
}
table = {}
for rig in ('stage', 'harsh'):
    for pose in (0, 20):
        a = np.asarray(Image.open(renders / f'silver_{rig}_{pose}.png').convert('RGB'), dtype=np.int16)
        b = np.asarray(Image.open(renders / f'iron_{rig}_{pose}.png').convert('RGB'), dtype=np.int16)
        row = {}
        for name, (x0, y0, x1, y1) in REGIONS.items():
            d = np.abs(b[y0:y1, x0:x1] - a[y0:y1, x0:x1])
            mse = float((d.astype(np.float64) ** 2).mean())
            row[name] = dict(pixels=int(d.shape[0] * d.shape[1]), max_abs=int(d.max()), mean_abs=float(d.mean()),
                             pixels_differing=int((d.max(axis=2) > 0).sum()),
                             psnr_db=None if mse == 0 else float(10 * np.log10(255 ** 2 / mse)))
        table[f'{rig}_pose{pose:02d}'] = row
        # sheet: rim and gem crops, v2 | v3 | amplified difference
        tiles = []
        for name in ('bottom_rim_with_floor_contact', 'gem'):
            x0, y0, x1, y1 = REGIONS[name]
            diff = np.clip(np.abs(b - a)[y0:y1, x0:x1] * 32, 0, 255).astype(np.uint8)
            crops = [Image.fromarray(a[y0:y1, x0:x1].astype(np.uint8)), Image.fromarray(b[y0:y1, x0:x1].astype(np.uint8)),
                     Image.fromarray(diff)]
            tiles.append([c.resize((c.width * 2, c.height * 2), Image.NEAREST) for c in crops])
        w = sum(t.width for t in tiles[0]) + 24
        h = sum(t[0].height for t in tiles) + 2 * 26
        sheet = Image.new('RGB', (w, h), (40, 40, 40))
        draw = ImageDraw.Draw(sheet)
        y = 0
        for (name, row_tiles) in zip(('bottom rim and floor contact', 'gem'), tiles):
            x = 0
            for label, tile in zip(('Silver v3', 'Iron', '|Iron - Silver| x 32'), row_tiles):
                draw.text((x + 4, y + 6), f'{label}, {name}, {rig} rig, pose {pose}', fill=(255, 255, 255))
                sheet.paste(tile, (x, y + 26))
                x += tile.width + 12
            y += row_tiles[0].height + 26
        sheet.save(sheets / f'silver_vs_iron_{rig}_pose{pose:02d}.png', optimize=True)
json.dump(table, open(out_json, 'w'), indent=1)
for key, row in table.items():
    print(key, ' | '.join(f"{n}: max {r['max_abs']} mean {r['mean_abs']:.4f} differing {r['pixels_differing']}/{r['pixels']}"
                          for n, r in row.items()))
