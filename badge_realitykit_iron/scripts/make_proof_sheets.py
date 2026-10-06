"""Side-by-side zoomed crops for the v2 proof: master | shipped export | v2 export.

  python make_proof_sheets.py <renders folder> <proof folder>

Each sheet has a plain row (the 8-bit AgX render, upscaled with nearest neighbour)
and a detail row (absolute high-pass, sigma 3 px, 0..12 luma levels mapped to black..white)
that makes blotches, grain and dotted edge glints easy to see.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

renders, proof = Path(sys.argv[1]), Path(sys.argv[2])
COLUMNS = [('master', 'Iron master'), ('silver', 'Shipped Silver v3'), ('iron', 'Iron USDZ')]
CROPS = {
    'emblem': dict(poses=(0, 20), box=(400, 440, 690, 880), scale=2),
    'ring_inset': dict(poses=(0,), box=(240, 470, 430, 850), scale=2),
}


def luma(img):
    return np.asarray(img, dtype=np.float32) @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def detail(img):
    g = luma(img)
    hp = np.abs(g - gaussian_filter(g, 3.0))
    return Image.fromarray(np.clip(hp / 12.0 * 255, 0, 255).astype(np.uint8)).convert('RGB')


for part, spec in CROPS.items():
    for rig in ('stage', 'harsh'):
        for pose in spec['poses']:
            box, scale = spec['box'], spec['scale']
            w, h = (box[2] - box[0]) * scale, (box[3] - box[1]) * scale
            sheet = Image.new('RGB', (len(COLUMNS) * (w + 12) - 12, 2 * h + 3 * 26), (40, 40, 40))
            draw = ImageDraw.Draw(sheet)
            for i, (key, label) in enumerate(COLUMNS):
                full = Image.open(renders / f'{key}_{rig}_{pose}.png').convert('RGB')
                plain = full.crop(box).resize((w, h), Image.NEAREST)
                hp = detail(full).crop(box).resize((w, h), Image.NEAREST)
                x = i * (w + 12)
                draw.text((x + 4, 6), f'{label}, {rig} rig, pose {pose}', fill=(255, 255, 255))
                sheet.paste(plain, (x, 26))
                draw.text((x + 4, 26 + h + 6), 'detail: |high-pass| x21 (blotches, grain, glints)', fill=(255, 255, 255))
                sheet.paste(hp, (x, 2 * 26 + h))
            out = proof / f'{part}_{rig}_pose{pose:02d}.png'
            sheet.save(out, optimize=True)
            print(out, sheet.size)
