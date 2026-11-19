"""Enamel pictures for the app: the owner's mockup, worked backwards through the app's color processing.

The enamel is a near black metal that glows with the mockup's own colors (the approved badges' method),
so the app shows the picture's colors instead of washing them pale. Gold is removed from the picture
wherever a real gold piece covers it.
Usage: textures.py candidateNN
"""
from pathlib import Path
import sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
R = Path(__file__).resolve().parent; C = R / sys.argv[1]
sys.path.insert(0, str(R.parent / 'silver2_metal_claude'))
from agx import agx, agx_inv
CAP = 1.42            # the app adds a glow halo above 1.5
EM_SCALE = 2.0
SIZE = 1024
L_WEIGHT = float(sys.argv[2]) if len(sys.argv) > 2 else .55

im = np.asarray(Image.open(R / 'reference/mockup.png').convert('RGB')).astype(np.float64) / 255
m = np.load(C / 'masks.npz')
H, W = im.shape[:2]


def disk(n):
    y, x = np.mgrid[-n:n + 1, -n:n + 1]
    return x * x + y * y <= n * n + .5


covered = ndi.binary_dilation(m['gold'] | (m['rim'] & m['bolt_visible']), disk(4))     # with the painted shadow that hugs each gold line
# (7 px in from the rim: the mockup's own painted rim highlight sits just inside it and showed as a dashed white line)
# The mockup's bolt has a shaded band and a thin pale line inside its rim, 14 to 26 px in from the edge. The real rim
# replaces that band, so the face's picture starts 28 px in and is carried outward smoothly from there. (Cutting
# through the thin line left it as a row of dots.)
face_known = (ndi.distance_transform_edt(m['bolt']) > 31) & m['bolt_visible']
known = ((m['pearl'] | m['blue']) & ~covered & ~m['bolt_visible']) | face_known
known &= ~(ndi.binary_dilation(m['bolt_visible'], disk(5)) & ~m['bolt'])     # no painted bolt edge left beside the real one
# Short leftovers of painted gold (the cut tip of a line, a stray glint) would show as whiskers beside the real
# gold. Long painted hairlines, like the ribbons' thin dividers, are part of the design and stay.
r_, g_, b_ = im[..., 0], im[..., 1], im[..., 2]
mx_ = im.max(2); sat_ = (mx_ - im.min(2)) / np.maximum(mx_, 1e-6)
warm = ((r_ > b_ + .08) & (g_ > b_ + .01) & (sat_ > .25)) & (m['pearl'] | m['blue']) & ~m['bolt_visible']
warm = ndi.binary_dilation(warm, disk(1))
lab, nlab = ndi.label(warm)
if nlab:
    sl = ndi.find_objects(lab)
    # Only bits that sit right beside a real gold piece are leftovers. A thin painted line out on the enamel is part of
    # the mockup's own drawing: removing pieces of it left rows of dots (candidate16 first try).
    beside_gold = set(np.unique(lab[ndi.binary_dilation(covered, disk(6))]).tolist()) - {0}
    # (and only small bits, up to 22 px: a longer thin tail that continues a real gold line stays painted, like the
    # needle under the frame's crown)
    short = [i + 1 for i, s in enumerate(sl) if max(s[0].stop - s[0].start, s[1].stop - s[1].start) < 22 and (i + 1) in beside_gold]
    # The mockup's painted bolt tip reaches a little past the real bolt's tip: that painted bit goes. (Removing every
    # painted line that touches the bolt also erased the ribbons' gold dividers and left a smudge: candidate15.)
    by_, bx_ = np.nonzero(m['bolt']); tip = (bx_[by_.argmax()], by_.max())
    yy_, xx_ = np.mgrid[:H, :W]
    known &= ~ndi.binary_dilation(warm & (np.hypot(xx_ - tip[0], yy_ - tip[1]) < 32), disk(2))
    leftovers = ndi.binary_dilation(np.isin(lab, short), disk(2))
    known &= ~leftovers
    print('short painted gold leftovers removed:', len(short), 'long hairlines kept:', nlab - len(short))
_, near = ndi.distance_transform_edt(~known, return_indices=True)
art = im[near[0], near[1]]
# Each hidden or removed pixel takes the color of the nearest enamel pixel, which is always on its own side of a
# gold line, then the filled part is softened a little. (Blurring the fill until smooth let the pearl's color leak
# across a gold line into the blue as a pale fringe: Blender zoom of candidate20.)
soft = np.dstack([ndi.gaussian_filter(art[..., k], 1.5) for k in range(3)])
art[~known] = soft[~known]
Image.fromarray(np.uint8(art * 255 + .5)).save(C / 'textures/art_target_full.png')
target = np.asarray(Image.fromarray(np.uint8(art * 255 + .5)).resize((SIZE, SIZE), Image.LANCZOS)).astype(np.float64) / 255


def to_linear(c):
    return np.where(c <= .04045, c / 12.92, ((c + .055) / 1.055) ** 2.4)


def oklab(srgb):
    l = to_linear(srgb)
    lms = np.cbrt(l @ np.array([[.4122214708, .2119034982, .0883024619], [.5363325363, .6806995451, .2817188376], [.0514459929, .1073969566, .6299787005]]))
    return lms @ np.array([[.2104542553, 1.9779984951, .0259040371], [.7936177850, -2.4285922050, .7827717662], [-.0040720468, .4505937099, -.8086757660]])


flat = np.clip(target.reshape(-1, 3), .004, .985)
lin = np.empty_like(flat)
for s0 in range(0, len(flat), 60000):
    goal = flat[s0:s0 + 60000]; x = np.clip(agx_inv(goal), 1e-6, CAP)
    for it in range(12):
        now = agx(x); h = x * .015 + 1e-5; cols = []
        for ch in range(3):
            q = x.copy(); q[:, ch] += h[:, ch]; cols.append((agx(q) - now) / h[:, ch, None])
        jac = np.stack(cols, -1) + np.eye(3)[None] * 1e-5
        delta = np.linalg.solve(jac, (goal - now)[..., None])[..., 0]
        x = np.clip(x + np.clip(delta, -x * .55, x * .8 + .01) * .8, 1e-6, CAP)
    lin[s0:s0 + 60000] = x
miss = np.abs(agx(lin) - flat).max(1)
out = miss > .02
print('pixels the app cannot show exactly:', round(out.mean() * 100, 1), '%')
# those (the vivid yellows, the brightest whites) take the closest color the app can show, judged by eye distance
g1 = np.r_[0, np.geomspace(.003, CAP, 200)]
a, b = np.meshgrid(g1, g1, indexing='ij'); z = np.zeros(a.size)
g2 = np.r_[0, np.geomspace(.004, CAP, 34)]
r3, gg3, b3 = np.meshgrid(g2, g2, g2, indexing='ij')
cand = np.vstack([np.c_[a.ravel(), b.ravel(), z], np.c_[a.ravel(), z, b.ravel()], np.c_[z, a.ravel(), b.ravel()], np.c_[r3.ravel(), gg3.ravel(), b3.ravel()]])
wts = np.array([L_WEIGHT, 1, 1])
tree = cKDTree(oklab(np.clip(agx(cand), 0, 1)) * wts)
_, idx = tree.query(oklab(flat[out]) * wts)
lin[out] = cand[idx]
lin = lin.reshape(SIZE, SIZE, 3)
om = out.reshape(SIZE, SIZE)
sm = np.dstack([ndi.gaussian_filter(lin[..., k], 1.2) for k in range(3)])
edge_free = ndi.binary_erosion(om, disk(2))
lin[edge_free] = sm[edge_free]
# The bolt's face: the app cannot show the mockup's bright yellow at full strength (bright yellows wash pale).
# Keep it a strong, pure yellow instead: full color at a slightly deeper brightness, with the mockup's own
# light and dark shapes, and a hue nudged from orange toward lemon so it never blends into the gold rim.
import colorsys
# The bolt's picture has its own file, so it can be finer than the rest (2048 px): its thin inner line showed stair
# steps in the Blender zoom at 1024. The file is mostly black and stays small.
BS = 2048
fm = np.asarray(Image.fromarray(np.uint8(ndi.binary_dilation(m['face'], disk(4)) * 255)).resize((BS, BS), Image.LANCZOS)) > 100
target_fine = np.asarray(Image.fromarray(np.uint8(art * 255 + .5)).resize((BS, BS), Image.LANCZOS)).astype(np.float64) / 255
t = np.clip(target_fine[fm], .004, .985)
mxv = t.max(1); mnv = t.min(1); sat = (mxv - mnv) / np.maximum(mxv, 1e-6)
hue = np.degrees(np.arctan2(np.sqrt(3) * (t[:, 1] - t[:, 2]), 2 * t[:, 0] - t[:, 1] - t[:, 2])) % 360
luma = t @ np.array([.2126, .7152, .0722])
hue2 = np.clip(hue + 2, 42, 52)
k = np.interp(hue2, [37, 43, 48, 52, 56, 60], [.35, .5, .65, .8, 1.0, 1.15])
strength = np.interp(luma, [.35, .55, .70, .85, .95, 1.0], [.38, .50, .60, .70, .86, 1.10])   # the app shows these as pure yellow (measured on candidate03)
blue_part = strength * .55 * np.clip((.45 - sat) / .45, 0, 1)
bolt_yellow = np.c_[strength, strength * k, blue_part]
# The app converts a normal color picture into its wider working colors, which turns a pure yellow pale
# (measured on candidate02: blue rose from 0.01 to 0.20). The bolt's picture is therefore handed over as
# raw numbers, which the app uses as they are.
BOLT_SCALE = 1.5
# (only the bolt's own picture gets this yellow: the cloud that covers the bolt's top keeps its pearl colors)
bolt_lin = np.zeros((BS, BS, 3)); bolt_lin[fm] = bolt_yellow
Image.fromarray(np.uint8(np.clip(bolt_lin / BOLT_SCALE, 0, 1) * 255 + .5)).save(C / 'textures/bolt_emission.png')
shown = np.clip(agx(lin.reshape(-1, 3)), 0, 1).reshape(SIZE, SIZE, 3)
Image.fromarray(np.uint8(np.concatenate([target, shown], 1) * 255 + .5)).save(C / 'textures/art_target_vs_app.png')


def encode(x):
    return np.uint8(np.clip(np.where(x <= .0031308, x * 12.92, 1.055 * np.maximum(x, 0) ** (1 / 2.4) - .055) * 255 + .5, 0, 255))


color = np.minimum(lin * .035, .012)
emission = np.maximum(0, lin - color * .4)
Image.fromarray(encode(color)).save(C / 'textures/art_color.png')
Image.fromarray(encode(emission / EM_SCALE)).save(C / 'textures/art_emission.png')
(C / 'textures/art.json').write_text(json.dumps(dict(bolt_scale=BOLT_SCALE, emission_scale=EM_SCALE, cap=CAP, lightness_weight=L_WEIGHT, white_shown=np.round(agx(np.array([[CAP] * 3]))[0], 3).tolist()), indent=1))
for name, px in dict(bolt_bright=(560, 470), bolt_lemon=(700, 560), bolt_amber=(520, 790), pearl=(250, 730), ribbon=(330, 480), field=(880, 560)).items():
    x, y = int(px[0] * SIZE / W), int(px[1] * SIZE / H)
    print(f'{name:12s} mockup {np.round(target[y, x], 2)} app shows {np.round(shown[y, x], 2)}')
print('brightest white the app shows without a halo:', np.round(agx(np.array([[CAP] * 3]))[0], 3))
