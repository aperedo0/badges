"""Compare real first-delivery and revised renders at identical camera/lighting."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1]
for kind in ['silver2', 'iron2']:
    base = root / kind
    table = {}
    for name in ['front.png', 'app_light_front.png', 'three_quarter.png']:
        old = Image.open(base / 'previous/first_shape_delivery/proof' / name).convert('RGB')
        new = Image.open(base / 'proof' / name).convert('RGB')
        assert old.size == new.size == (1080, 1440)
        delta = np.abs(np.asarray(new, dtype=np.int16) - np.asarray(old, dtype=np.int16))
        table[name] = {'whole_frame_mean_abs_channel_difference': float(delta.mean()), 'maximum_channel_difference': int(delta.max()), 'changed_pixels': int(np.count_nonzero(delta.max(axis=2))), 'purpose': 'Material appearance change; geometry/normal identity is checked separately at the USD attribute level.'}
        box = (205, 330, 875, 1060)
        tiles = [old.crop(box), new.crop(box)]
        canvas = Image.new('RGB', (1364, 780), (17, 20, 23)); draw = ImageDraw.Draw(canvas)
        for i, (tile, label) in enumerate(zip(tiles, ['First delivery', 'Revised finish'])):
            x = i * 682
            canvas.paste(tile, (x, 50)); draw.text((x+12, 18), label, fill='white')
        canvas.save(base / 'proof' / ('render_before_after_' + name))
    (base / 'reports/compare_renders.json').write_text(json.dumps(table, indent=2) + '\n')
    print(kind, table)
