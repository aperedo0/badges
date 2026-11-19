"""Checkpoint 2: which material is on top at every pixel, beside the mockup, with a pass or fail per class. Python 3.11.

Usage: material_map.py CAND_DIR MOCKUP.png CLASSES.json OUT.png [MISS_PX]
Writes OUT.png (mockup classes beside the build) and OUT_misses.png (every local miss in red over the mockup).
CLASSES.json maps each material to a class the mockup can show: {"Red": "red", "Lemon": "yellow", "Gold": "gold", ...}.
The mockup is classed per pixel (gold, red, yellow, white, blue, cyan) by color. Pass: inside each class, away from a
3 px band at class borders, at least 85% of pixels show a material of that class, and no pixel inside the silhouette
is uncovered. A gold area left as bare red plate, a missing piece or a hole fails here.
"""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
C = Path(sys.argv[1]); D = np.load(C / 'parts.npz'); META = json.load(open(C / 'parts.json'))
mock = np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(float) / 255; CL = json.load(open(sys.argv[3]))
U = META['units']; S, AX, TOP = U['S'], U['axis'], U.get('top', 15.0); H, W = mock.shape[:2]
top_z = np.full((H, W), -np.inf); top_m = np.full((H, W), '', dtype=object)
for p in META['parts']:
    V = D[p['name'] + '_v'][:p['front']]; M = D[p['name'] + '_m'][:p['front']]; names = p['materials']
    px = V[..., 0] / S + AX; py = TOP + (2.995 - V[..., 1]) / S
    for (x0, x1, x2), (y0, y1, y2), (z0, z1, z2), mi in zip(px, py, V[..., 2], M):
        bx0, bx1 = int(max(np.floor(min(x0, x1, x2)), 0)), int(min(np.ceil(max(x0, x1, x2)), W - 1))
        by0, by1 = int(max(np.floor(min(y0, y1, y2)), 0)), int(min(np.ceil(max(y0, y1, y2)), H - 1))
        if bx1 < bx0 or by1 < by0:
            continue
        gy, gx = np.mgrid[by0:by1 + 1, bx0:bx1 + 1] + 0.5
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-12:
            continue
        w0 = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / den; w1 = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / den; w2 = 1 - w0 - w1
        ins = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6); z = w0 * z0 + w1 * z1 + w2 * z2
        iy, ix = (gy - 0.5).astype(int), (gx - 0.5).astype(int)
        upd = ins & (z > top_z[iy, ix])
        top_z[iy[upd], ix[upd]] = z[upd]; top_m[iy[upd], ix[upd]] = names[mi]
# classes of the mockup by color
mx, mn = mock.max(2), mock.min(2); sat = (mx - mn) / np.maximum(mx, 1e-6); d = np.maximum(mx - mn, 1e-6); r, g, b = mock.transpose(2, 0, 1)
hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
mc = np.full((H, W), 'other', dtype=object)
# white enamel is broad; bright bands on metal (highlights) are narrower than about 16 px and are left out
mc[ndi.binary_opening((sat < 0.25) & (mx > 0.6), iterations=8)] = 'white'
mc[((hue < 22) | (hue > 340)) & (sat > 0.45)] = 'red'
mc[(hue >= 22) & (hue < 62) & (sat > 0.25)] = 'gold'; mc[(hue >= 22) & (hue < 62) & (sat > 0.88) & (mx > 0.75)] = 'yellow'   # lemon, sun: more saturated than gold
mc[(hue >= 185) & (hue < 295) & (sat > 0.25)] = 'blue'; mc[(hue >= 180) & (hue < 219) & (sat > 0.15) & (sat < 0.63) & (mx > 0.6)] = 'cyan'   # purple fields are blue; light blue (cyan) is its own class
# only the badge itself is classed: its colored parts closed and filled (white enamel enclosed by gold comes in, a light
# background or drop shadow stays out)
colored = ndi.binary_closing((sat > 0.3) & (mx > 0.08), iterations=4)
badge = ndi.binary_fill_holes(colored); lab_b, nb = ndi.label(badge)
if nb:
    badge = lab_b == (1 + np.argmax(ndi.sum(badge, lab_b, range(1, nb + 1))))
mc[~badge] = 'other'
# a material may show several classes (one enamel whose colors come from the picture): it counts for each of them
MULTI = {m: v for m, v in CL.items() if isinstance(v, list)}
built = np.vectorize(lambda m: (m if m in MULTI else CL.get(m, 'none')) if m else 'uncovered')(top_m)
for m, v in MULTI.items():
    on = built == m
    built[on] = np.where(np.isin(mc[on], v), mc[on], v[0])          # it shows whichever of its classes the mockup has there
inside = np.isfinite(top_z) | ndi.binary_erosion(np.isin(mc, ['gold', 'red', 'yellow', 'white', 'blue', 'cyan']), iterations=2)
report, fails = {}, []
for cls in ('gold', 'red', 'yellow', 'white', 'blue', 'cyan'):
    core = ndi.binary_erosion(mc == cls, iterations=3)
    if core.sum() < 200:
        continue
    ok = (built[core] == cls) | ((cls in ('gold', 'yellow')) & np.isin(built[core], ['gold', 'yellow']) & (cls == 'yellow'))
    share = float((built[core] == cls).mean()); report[cls] = round(share, 3)
    if share < 0.85 and cls in ('gold', 'red', 'white', 'blue', 'cyan'):
        fails.append(f'{cls}: only {share:.0%} of its pixels show a {cls} material')
# real holes: uncovered pixels enclosed by the build itself; outline differences: inside the mockup but outside the build
covered = built != 'uncovered'
holes = int((~covered & ndi.binary_fill_holes(covered)).sum())
outline_diff = int((~covered & ~ndi.binary_fill_holes(covered) & ndi.binary_erosion(mc != 'other', iterations=4)).sum())
report['outline_difference_px'] = outline_diff
if holes > 20:
    fails.append(f'{holes} pixels inside the build are not covered by any piece (see through holes)')
# local misses: a whole badge share hides a missing part (cand02: the C curls built as thorns and the border at half
# width still scored gold 0.84). Every connected area of a class that shows another material is listed with its
# center and what shows there; one larger than MISS_PX fails.
MISS_PX = int(sys.argv[5]) if len(sys.argv) > 5 else 1200
misses = []; miss_img = np.zeros((H, W), bool)
for cls in ('gold', 'red', 'yellow', 'white', 'blue', 'cyan'):
    core = ndi.binary_erosion(mc == cls, iterations=3)
    wrong = core & (built != cls) & ~((cls == 'yellow') & (built == 'gold')) & ~((cls == 'gold') & (built == 'yellow'))
    wrong = ndi.binary_opening(wrong, iterations=2)
    lab, n = ndi.label(wrong)
    if not n:
        continue
    sizes = ndi.sum(wrong, lab, range(1, n + 1)); cents = ndi.center_of_mass(wrong, lab, range(1, n + 1))
    for i in np.argsort(sizes)[::-1][:6]:
        if sizes[i] < 150:
            break
        shows = built[lab == i + 1]; vals, cnt = np.unique(shows, return_counts=True)
        misses.append(dict(cls=cls, px=int(sizes[i]), center=[round(cents[i][1]), round(cents[i][0])], shows=str(vals[np.argmax(cnt)])))
        miss_img |= lab == i + 1
        if sizes[i] > MISS_PX:
            fails.append(f'{cls} area of {int(sizes[i])} px at {[round(cents[i][1]), round(cents[i][0])]} shows {vals[np.argmax(cnt)]}')
report['local_misses'] = misses
dim = (mock * 0.45 * 255).astype(np.uint8); dim[miss_img] = (255, 0, 0)
Image.fromarray(dim).save(str(Path(sys.argv[4]).with_name(Path(sys.argv[4]).stem + '_misses.png')))
pal = {'gold': (220, 170, 40), 'red': (215, 70, 40), 'yellow': (250, 235, 120), 'white': (240, 240, 240), 'blue': (40, 80, 200), 'cyan': (60, 200, 240), 'uncovered': (255, 0, 255), 'none': (0, 0, 0), 'other': (30, 30, 30)}
img_b = np.array([[pal.get(c, (0, 0, 0)) for c in row] for row in built], np.uint8); img_m = np.array([[pal.get(c, (0, 0, 0)) for c in row] for row in mc], np.uint8)
Image.fromarray(np.concatenate([img_m, img_b], 1)).resize((W, H // 2)).save(sys.argv[4])
print(json.dumps(dict(share_per_class=report, failures=fails), indent=1)); sys.exit(1 if fails else 0)
