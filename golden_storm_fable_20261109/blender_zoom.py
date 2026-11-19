"""Zoomed sweep of the whole badge inside the open Blender, before any simulator run (owner's rule, November 9, 2026).

Takes close screenshots of every part of the badge in the open Blender (about ten times the phone's zoom from the
front, plus angled and back views) and lays them out on sheets to inspect for rough edges.

Usage: blender_zoom.py candidateNN [front,left,right,back]
The candidate must already be loaded in Blender (blender_load.py). Sheets go to candidateNN/blender_zoom/.
"""
import sys, json, time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
R = Path(__file__).resolve().parent
sys.path.insert(0, str(R.parent / 'ruby_heart_claude_20261107/tools'))
import blender_link

C = R / sys.argv[1]
WHICH = sys.argv[2].split(',') if len(sys.argv) > 2 else ['front', 'left', 'right', 'back']
OUT = C / 'blender_zoom'; OUT.mkdir(exist_ok=True)
meta = json.loads((C / 'parts.json').read_text()); S = meta['units_per_pixel']; CX = meta['center_x']; TOP = meta['top']
body = np.load(C / 'shapes.npz')['Gold body']
K = 1.43                      # the viewport shows about 1.43 units across per unit of view distance
ASPECT = None

SET_VIEW = '''
import bpy, math
from mathutils import Vector, Euler
bpy.context.window.scene = bpy.data.scenes['Golden Storm']
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        sp = area.spaces.active; r3 = sp.region_3d
        sp.shading.type = 'MATERIAL'; sp.overlay.show_overlays = False
        r3.view_perspective = '{mode}'
        r3.view_location = Vector(({x}, 0, {z})); r3.view_distance = {dist}
        r3.view_rotation = Euler((math.radians({rx}), 0, math.radians({rz}))).to_quaternion()
        break
'''


def shot(name, x, z, width, rx=90, rz=0, mode='ORTHO', size=1000):
    blender_link.command('execute_code', {'code': SET_VIEW.format(mode=mode, x=x, z=z, dist=width / K, rx=rx, rz=rz)})
    time.sleep(.35)
    p = OUT / f'{name}.png'
    blender_link.command('get_viewport_screenshot', {'filepath': str(p), 'max_size': size})
    return p


def has_badge(x, z, w, h):
    px0 = int((x - w / 2) / S + CX); px1 = int((x + w / 2) / S + CX); py0 = int((3.015 - (z + h / 2)) / S + TOP); py1 = int((3.015 - (z - h / 2)) / S + TOP)
    px0, px1 = max(px0, 0), min(px1, body.shape[1]); py0, py1 = max(py0, 0), min(py1, body.shape[0])
    return px1 > px0 and py1 > py0 and body[py0:py1, px0:px1].mean() > .04      # skip tiles that are nearly all background


def sheet(tiles, name, cols, tile_w):
    if not tiles:
        return
    ims = [(lab, Image.open(p).convert('RGB')) for lab, p in tiles]
    w, h = ims[0][1].size; th = int(round(tile_w * h / w)); rows = (len(ims) + cols - 1) // cols
    out = Image.new('RGB', (cols * (tile_w + 4), rows * (th + 4)), (255, 0, 255))
    for i, (lab, im) in enumerate(ims):
        t = im.resize((tile_w, th), Image.LANCZOS); d = ImageDraw.Draw(t)
        d.rectangle([0, 0, 6 * len(lab) + 8, 13], fill=(0, 0, 0)); d.text((3, 1), lab, fill=(255, 255, 0))
        out.paste(t, ((i % cols) * (tile_w + 4), (i // cols) * (th + 4)))
    out.save(OUT / name); print(name, out.size, len(ims), 'tiles')


first = shot('_probe', 0, .28, 8)
with Image.open(first) as im0:
    ASPECT = im0.size[1] / im0.size[0]

if 'front' in WHICH or 'back' in WHICH:
    W_ = 1.2; H_ = W_ * ASPECT
    xs = [-2.2, -1.1, 0, 1.1, 2.2]; zs = []
    z = 3.05 - H_ / 2 + .02
    while z + H_ / 2 > -2.5:
        zs.append(round(z, 3)); z -= H_ - .08
    if 'front' in WHICH:
        tiles = []
        for zi, z in enumerate(zs):
            for xi, x in enumerate(xs):
                if not has_badge(x, z, W_, H_):
                    continue
                px, py = int(x / S + CX), int((3.015 - z) / S + TOP)
                tiles.append((f'front r{zi + 1} c{xi + 1}  mockup px {px},{py}', shot(f'front_{zi + 1}_{xi + 1}', x, z, W_)))
        for k in range(0, len(tiles), 6):
            sheet(tiles[k:k + 6], f'sheet_front_{k // 6 + 1}.png', 2, 776)
    if 'back' in WHICH:
        # The back is the front's mesh mirrored, so its shapes are already checked: a coarser pass looks for faces
        # that point the wrong way and for anything the mirroring broke.
        Wb = 2.3; Hb = Wb * ASPECT; tiles = []
        for zi, z in enumerate([2.3, 1.15, 0, -1.15, -2.0]):
            for xi, x in enumerate([1.8, 0, -1.8]):
                tiles.append((f'back r{zi + 1} c{xi + 1}', shot(f'back_{zi + 1}_{xi + 1}', x, z, Wb, rz=180)))
        sheet(tiles, 'sheet_back.png', 3, 520)

for side, rz, rx in (('left', -38, 80), ('right', 38, 80)):
    if side not in WHICH:
        continue
    W_ = 2.3; H_ = W_ * ASPECT; tiles = []
    for zi, z in enumerate([2.2, 1.0, -.2, -1.4, -2.2]):
        for xi, x in enumerate([-1.7, 0, 1.7]):
            tiles.append((f'{side} r{zi + 1} c{xi + 1}', shot(f'{side}_{zi + 1}_{xi + 1}', x, z, W_, rx=rx, rz=rz, mode='PERSP')))
    sheet(tiles, f'sheet_{side}.png', 3, 520)

if 'phone' in WHICH or len(sys.argv) <= 2:
    # The badge at the phone's own size (416 pixels wide), then enlarged 4x with hard pixels. A detail thinner than
    # about two phone pixels shows here as a broken or dotted line, which the big zooms cannot show.
    r = blender_link.command('execute_code', {'code': '''
import bpy
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for reg in area.regions:
            if reg.type == 'WINDOW':
                print('REGION', reg.width, reg.height)
'''})
    vw = int(str(r).split('REGION')[1].split()[0])
    width_units = (meta['bounds_max'][0] - meta['bounds_min'][0]) * vw / 416.0
    tiles = []
    for name, rz, rx in (('front', 0, 90), ('turned', -32, 86)):
        p = shot(f'phone_{name}', 0, .28, width_units, rx=rx, rz=rz, size=vw)
        im_ = Image.open(p).convert('RGB'); w_, h_ = im_.size
        c_ = im_.crop((w_ // 2 - 235, h_ // 2 - 250, w_ // 2 + 235, h_ // 2 + 250))
        c_.resize((c_.size[0] * 4, c_.size[1] * 4), Image.NEAREST).save(OUT / f'phone_{name}_4x.png')
    print('phone size pictures written (viewport', vw, 'px wide)')
print('sweep written to', OUT)
