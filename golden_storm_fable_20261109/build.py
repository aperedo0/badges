"""Golden Storm: real gold pieces over enamel that carries the owner's picture.

Method (the one the approved badges use):
  * every part is its own closed solid with a sculpted front, a mirrored back and side walls;
  * gold is real metal geometry with rounded edges, lit only by the app's studio light;
  * the blue enamel, the pearl clouds and the bolt's yellow face show the owner's picture,
    worked backwards through the app's color processing so the app displays those colors.

Usage: build.py candidateNN
"""
from pathlib import Path
import json, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.spatial import Delaunay

R = Path(__file__).resolve().parent
C = R / sys.argv[1]
(C / 'textures').mkdir(parents=True, exist_ok=True)
im = np.asarray(Image.open(R / 'reference/mockup.png').convert('RGB')).astype(np.float64) / 255
H, W = im.shape[:2]
yy, xx = np.mgrid[:H, :W].astype(np.float64)
seg = np.load(R / 'work/seg_raw.npz')
sil, pearl, blue = seg['sil'], seg['pearl'], seg['blue']

# ---------- measurements ----------
ys, xs = np.nonzero(sil)
TOP, BOT = ys.min(), ys.max() + 1
CX = (xs.min() + xs.max() + 1) / 2
S = 5.47 / (BOT - TOP)                      # units per mockup pixel: top at 3.015, lowest point at -2.455

Z_BASE = .06
Z_BLUE = .10
GOLD_RISE, GOLD_EDGE = .050, 6.0            # how far gold stands above the enamel beside it, and its rounded edge (px)
ROOF, ROOF_CAP = .0016, 40                  # wide gold (the four points, the frame) slopes up to a soft ridge
PEARL_DOME, PEARL_TAU = .055, 18
RIM, RIM_RISE, RIM_EDGE = 16., .030, 5.0
BOLT_TOP_Z, BOLT_TIP_Z = .17, .34           # the bolt tilts: tucked under the upper cloud, over the lower cloud


def disk(n):
    y, x = np.mgrid[-n:n + 1, -n:n + 1]
    return x * x + y * y <= n * n + .5


def signed(mask, sigma):
    d = ndi.distance_transform_edt(mask) - ndi.distance_transform_edt(~mask)
    d = np.where(d > 0, d - .5, d + .5)
    return ndi.gaussian_filter(d, sigma) if sigma else d


def drop_small(m, area):
    lab, n = ndi.label(m)
    s = np.bincount(lab.ravel())
    keep = s >= area; keep[0] = False
    return keep[lab]


def sample(field, p):
    return ndi.map_coordinates(field, [p[:, 1], p[:, 0]], order=1, mode='nearest')


# ---------- the bolt: straight edges fitted to the mockup ----------
A, B, Cc, D, E, G, Hn = np.load(R / 'work/bolt_outer.npy')
# The top of the bolt is cut where it meets the cloud's gold curl, as in the mockup.
B = A + (B - A) * ((296 - A[1]) / (B[1] - A[1]))
Cc = D + (Cc - D) * ((306 - D[1]) / (Cc[1] - D[1]))
BOLT = np.array([A, B, Cc, D, E, G, Hn])


def polygon_sdf(P):
    img = Image.new('L', (W * 4, H * 4)); ImageDraw.Draw(img).polygon([tuple(q * 4 + 1.5) for q in P], fill=255)
    inside = np.asarray(img.resize((W, H), Image.BOX)) > 127
    d = np.full((H, W), 1e9)
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        ab = b - a; t = np.clip(((xx - a[0]) * ab[0] + (yy - a[1]) * ab[1]) / (ab @ ab), 0, 1)
        d = np.minimum(d, np.hypot(xx - (a[0] + t * ab[0]), yy - (a[1] + t * ab[1])))
    return np.where(inside, d, -d)


bolt_sdf = polygon_sdf(BOLT)
boltmask = bolt_sdf > 0
bolt_z = BOLT_TOP_Z + (BOLT_TIP_Z - BOLT_TOP_Z) * np.clip((yy - 296) / (G[1] - 296), 0, 1)

# the upper cloud curls over the top of the bolt: that zone stays cloud and gold
# (outer edge of the cloud's wide gold curl, read off the mockup)
CURL = [(560, 200), (574, 289), (603, 308), (607, 320), (608, 337), (615, 353), (630, 370), (655, 387), (673, 397), (697, 403), (716, 404), (820, 404), (820, 200)]
img = Image.new('L', (W, H)); ImageDraw.Draw(img).polygon(CURL, fill=255)
curl_zone = ndi.gaussian_filter(np.asarray(img).astype(float) / 255, 2.0) > .5
cloud_over = curl_zone & boltmask
# Under the cloud the bolt drops well below it. (The bolt climbs toward its tip, and under the cloud's lower edge
# its rim came up through the pearl as a tiny tab: Blender zoom of candidates 17 and 18.)
bolt_under = ndi.gaussian_filter(ndi.binary_erosion(curl_zone, disk(6)).astype(float), 2.5)
bolt_visible = boltmask & ~cloud_over & ~pearl

# ---------- gold: everything inside the outline that is not enamel or bolt ----------
r_, g_, b_ = im[..., 0], im[..., 1], im[..., 2]
mx_ = im.max(2); sat_ = (mx_ - im.min(2)) / np.maximum(mx_, 1e-6)
goldish = ((r_ > b_ + .10) & (g_ > b_ + .02) & (sat_ > .28)) | ((sat_ <= .28) & (mx_ > .6) & ((g_ - b_) > .045) & ((r_ - g_) < (g_ - b_)))
goldish = ndi.binary_closing(goldish, disk(2))     # dark edge lines and tiny glints inside gold count as gold
gold0 = sil & ~pearl & ~blue & ~bolt_visible
gold = ndi.binary_opening(gold0 & (goldish | cloud_over), disk(4))   # lines under about 9 px stay painted in the enamel
# white glints: gold when they sit in gold, enamel when they sit in enamel
white = gold0 & ~gold & (mx_ > .72) & (sat_ < .3)
lab, nlab = ndi.label(white)
if nlab:
    ids = np.arange(1, nlab + 1)
    by_gold = ndi.sum(ndi.binary_dilation(gold, disk(2)), lab, ids)
    by_enamel = ndi.sum(ndi.binary_dilation(pearl | blue, disk(2)), lab, ids)
    warm_white = ndi.mean(r_ - b_, lab, ids) > .02           # a ribbon's own glint is bluish white, a gold glint is warm
    is_gold = (by_gold > by_enamel) & (warm_white | (by_gold > 3 * by_enamel))
    gold |= np.isin(lab, ids[is_gold])
    not_gold = np.isin(lab, ids[~is_gold])                    # these go back to the enamel they sit in, for good
    _, nearE = ndi.distance_transform_edt(~(pearl | blue), return_indices=True)
    to_p = not_gold & pearl[nearE[0], nearE[1]]
    pearl = pearl | to_p; blue = blue | (not_gold & ~to_p); gold0 = gold0 & ~not_gold
gold = ndi.binary_closing(gold, disk(5)) & gold0
gold = (ndi.binary_fill_holes(gold) & gold0) | gold
gold = ((ndi.gaussian_filter(gold.astype(float), 1.6) > .5) & gold0) | ndi.binary_erosion(gold, disk(1))
gold = ndi.binary_opening(gold, disk(3))            # no needles at line ends
# A line stays real gold only where most of it is at least 9 px wide. A line that hovers around that width
# would come out as beads, so it stays painted along its whole length instead.
thick = ndi.binary_opening(gold, disk(4)).astype(float)
share = ndi.uniform_filter(thick, 33) / np.maximum(ndi.uniform_filter(gold.astype(float), 33), 1e-6)
gold = ndi.binary_opening(gold & (share > .6), disk(3))
gold = drop_small(gold, 500)
# The mockup's gold border runs all the way around. Wherever the trace lost it (a white glint read as pearl),
# the outline gets its gold border back, at least 9 px wide.
outline0 = ndi.binary_fill_holes(ndi.binary_closing(gold | pearl | blue | boltmask, disk(4)))
# The cloud's tail tip pokes a few pixels past the frame at the lower right. On the phone that is a rough little
# nub on the outline, so the outline runs smooth there and the tail ends inside the frame.
nub = (slice(900, 1010), slice(880, 1000))
outline0[nub] = ndi.binary_opening(outline0, disk(34))[nub]
border = outline0 & ~ndi.binary_erosion(outline0, disk(11))
gold = ndi.binary_closing(gold | border, disk(2)) & outline0
pearl = pearl & ~gold; blue = blue & ~gold
gold0 = gold0 | gold
# Thin gold lines that only run across the blue ribbons (not a cloud outline, not the frame) stay painted unless
# they are at least 13 px wide: traced thinner, they came out as broken bits and spurs.
thick13 = ndi.binary_dilation(ndi.binary_opening(gold, disk(6)), disk(2))
by_pearl = ndi.binary_dilation(pearl, disk(3))
outer_band = outline0 & ~ndi.binary_erosion(outline0, disk(14))
lab, nlab = ndi.label(gold & ~thick13)
if nlab:
    ids = np.arange(1, nlab + 1)
    # a thin piece is a ribbon line when it touches no cloud and is not part of the outer border
    ribbon_line = (ndi.mean(by_pearl, lab, ids) < .05) & (ndi.maximum(outer_band, lab, ids) == 0)
    gold &= ~np.isin(lab, ids[ribbon_line])
    gold = drop_small(ndi.binary_opening(gold, disk(3)), 3000)   # no stray gold islands on the ribbons
# Where the bold arc in the right ribbons forks into two thin lines, the fork's wide base read as a barb.
# The arc ends cleanly just before the fork instead.
fork_img = Image.new('L', (W, H)); ImageDraw.Draw(fork_img).polygon([(873.6, 719), (890, 720), (890, 730), (885, 734), (886, 756), (872, 757), (871, 736)], fill=255)
# (the same at the upper arc, where a thin divider leaves it)
ImageDraw.Draw(fork_img).polygon([(916.7, 634), (950, 645), (946.7, 655), (930, 651.7), (915, 638.3)], fill=255)
gold &= ~(np.asarray(fork_img) > 0)
lost = gold0 & ~gold
_, near = ndi.distance_transform_edt(~(pearl | blue), return_indices=True)
to_pearl = lost & pearl[near[0], near[1]]
pearl2 = pearl | to_pearl
blue2 = (blue | (lost & ~to_pearl)) & ~bolt_visible
enclosed = ndi.binary_fill_holes(gold | boltmask)      # enamel only exists inside the gold border
pearl2 &= enclosed; blue2 &= enclosed
gold |= ndi.binary_dilation(gold, disk(5)) & bolt_visible & (bolt_z > .24)   # line ends tuck under the raised bolt


def smooth_shape(mask, sigma=5.0, K=3):
    """Buttery edges: trace the shape's outlines as curves, smooth each curve along its length, keep true corners.

    Each outline is resampled every pixel and low passed along itself (wobbles shorter than about 20 px go), with
    one sharpening pass so tight curves such as the spirals do not shrink. Points at real corners (the frame's
    points and notches, cloud cusps, line ends) stay where they are. The curves are then filled at 3x and measured,
    which gives a distance field accurate to a fraction of a pixel.
    """
    from contourpy import contour_generator
    from scipy.ndimage import gaussian_filter1d
    from PIL import ImageChops
    f = ndi.gaussian_filter(mask.astype(float), 1.0) - .5
    lines = contour_generator(z=f).lines(0.0)
    acc = Image.new('1', (W * K, H * K), 0); kept = 0; caps = []
    for L in lines:
        L = np.asarray(L, float)
        if len(L) < 16 or np.hypot(*(L[0] - L[-1])) > 1.5:
            continue
        P = L[:-1]
        seg = np.hypot(*np.diff(np.vstack([P, P[:1]]), axis=0).T); s = np.r_[0, np.cumsum(seg)]
        n = max(int(round(s[-1])), 8); t = np.linspace(0, s[-1], n, endpoint=False)
        P = np.c_[np.interp(t, s, np.r_[P[:, 0], P[0, 0]]), np.interp(t, s, np.r_[P[:, 1], P[0, 1]])]
        if n >= 40:
            # A real corner changes the direction of travel for good: compare the direction a little before with
            # the direction a little after. A small bump turns one way and straight back, so it is not a corner
            # and gets smoothed away. (Judging the turn over 3 px kept every bump: seen in the Blender zoom.)
            Q = gaussian_filter1d(P, 2.5, axis=0, mode='wrap')
            a = np.roll(Q, 4, 0) - np.roll(Q, 12, 0); b = np.roll(Q, -12, 0) - np.roll(Q, -4, 0)
            ang = np.abs(np.arctan2(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0], (a * b).sum(1)))
            pin = np.clip(gaussian_filter1d((ang > np.radians(50)).astype(float), 2.0, mode='wrap') * 3, 0, 1)[:, None]
            light = gaussian_filter1d(P, 1.5, axis=0, mode='wrap')        # corners keep their shape, minus pixel steps
            g1 = gaussian_filter1d(P, sigma, axis=0, mode='wrap')
            g2 = g1 + (g1 - gaussian_filter1d(g1, sigma, axis=0, mode='wrap'))
            # Line ends: the outline makes a U turn around gold.
            from scipy.ndimage import maximum_filter1d
            # (measured on this badge: line ends turn 124 to 153 degrees, the frame's own points 105 to 110)
            peak = np.nonzero((ang > np.radians(120)) & (ang >= maximum_filter1d(ang, 25, mode='wrap') - 1e-9))[0]
            for i_ in peak:
                mid_ = (Q[i_ - 8] + Q[(i_ + 8) % n]) / 2
                if mask[int(round(mid_[1])), int(round(mid_[0]))]:
                    u_ = light[i_] - mid_; u_ = u_ / max(np.linalg.norm(u_), 1e-6)
                    caps.append([light[i_][0], light[i_][1], u_[0], u_[1]])
            P = light * pin + g2 * (1 - pin)
        one = Image.new('1', (W * K, H * K), 0)
        ImageDraw.Draw(one).polygon([tuple(q) for q in (P + .5) * K - .5], fill=1)
        acc = ImageChops.logical_xor(acc, one); kept += 1
    big = np.asarray(acc)
    d = ndi.distance_transform_edt(big) - ndi.distance_transform_edt(~big)
    d = np.where(d > 0, d - .5, d + .5)
    return d.reshape(H, K, W, K).mean((1, 3)) / K, kept, np.array(caps).reshape(-1, 4)


gold = drop_small(ndi.binary_opening(gold, disk(4)), 1500)      # no drips or bumps narrower than a line
gold = ndi.binary_closing(gold, disk(3)) & outline0             # and no dents narrower than two phone pixels
# Line ends taper to a point, as in the mockup, instead of stopping in a blunt round end: toward its end a line is
# pared down from both sides until only its middle is left. (First pass finds the ends, second pass smooths.)
_, _, ends0 = smooth_shape(gold)
depth0 = ndi.distance_transform_edt(gold); far_in = ndi.distance_transform_edt(outline0); TAPER = 28.
tapered = 0
for cx_, cy_, ux_, uy_ in ends0:
    if far_in[int(round(cy_)), int(round(cx_))] < 26:
        continue                                           # the frame's own points are not line ends
    bx_, by2_ = int(round(cx_ - ux_ * 10)), int(round(cy_ - uy_ * 10))
    half = float(np.clip(depth0[max(by2_ - 2, 0):by2_ + 3, max(bx_ - 2, 0):bx_ + 3].max(), 3, 9))
    g_ = np.hypot(xx - cx_, yy - cy_)
    # (a strip about 3.6 px wide is left down the middle, as wide as the painted line that carries on from it)
    gold &= ~((g_ < TAPER) & (depth0 < max(half - 1.8, 0) * (1 - (g_ / TAPER) ** .8)))
    tapered += 1
gold = drop_small(gold, 400)
gold_sdf, n_curves, line_ends = smooth_shape(gold, sigma=9.0)
print('gold outlines smoothed:', n_curves, ' line ends tapered:', tapered, ' line ends found after:', len(line_ends))
gold = gold_sdf > 0
gold_d = np.maximum(gold_sdf, 0)

# ---------- heights ----------
pearl_level = .14 + 7.67e-5 * (xx - 280) - 1.067e-4 * (yy - 720)     # clouds rise toward the upper right
pearl_sdf = signed(pearl2, 1.3)
# The dome rises from the gold's edge itself (not from the first rough trace of the cloud), so the pearl never
# pokes through the gold's shoulder and the line where they meet is as smooth as the gold.
z_pearl = pearl_level + PEARL_DOME * (1 - np.exp(-np.clip(-gold_sdf - 1.0, 0, None) / PEARL_TAU))
# A dome shaped by distance has a small kink along its crest and a pointed peak in the middle of each lobe. The app
# drew a dark pixel at those peaks (candidates 01 to 13), so the dome is smoothed into one soft surface.
z_pearl = ndi.gaussian_filter(z_pearl, 5.0)
enamel_level = np.where(pearl2, pearl_level, np.where(blue2, Z_BLUE, -1.))
gold_level = ndi.maximum_filter(enamel_level, footprint=disk(30))
_, near = ndi.distance_transform_edt(enamel_level < 0, return_indices=True)
gold_level = np.where(gold_level < 0, enamel_level[near[0], near[1]], gold_level)
gold_level = ndi.gaussian_filter(gold_level, 6) + .012


def round_edge(d, width):
    t = np.clip(d / width, 0, 1)
    return 1 - (1 - t) ** 2                         # a soft rounded shoulder, flat on top


def round_edge_slope(d, width):
    t = np.clip(d / width, 1e-3, 1)
    return np.where(d < width, (1 - t) / (width * np.sqrt(1 - (1 - t) ** 2)), 0)


# Gold tops are flat and mirror clean. Only the four big points get a ridge with two flat sides, like the mockup.
# Each point is two flat facets that meet in one straight ridge from its tip toward its base. The shading of each
# facet is one constant lean away from that ridge line, fading gently into the flat frame. (Taking the lean from
# the outline's own direction gave blotches where the point runs into the frame.)
gys, gxs = np.nonzero(gold)
tips = [(gxs[gys.argmin()], gys.min()), (gxs[gys.argmax()], gys.max()), (gxs.min(), gys[gxs.argmin()]), (gxs.max(), gys[gxs.argmax()])]
ridge_w = np.zeros((H, W)); lean_x = np.zeros((H, W)); lean_y = np.zeros((H, W)); ridge_pts = []
RIDGE_SOFT = 2.5                                     # the ridge itself is rounded over about two phone pixels
for tx, ty in tips:                                  # the four big points: top, bottom, left, right
    rad = np.hypot(xx - tx, yy - ty)
    cy_, cx_ = ndi.center_of_mass(gold & (rad < 80))
    ax = np.array([cx_ - tx, cy_ - ty]); ax /= np.linalg.norm(ax)
    nx_ = np.array([-ax[1], ax[0]])
    s_ = (xx - tx) * nx_[0] + (yy - ty) * nx_[1]      # signed distance from the ridge line
    w_ = ndi.gaussian_filter(np.clip(1 - (rad - 85) / 50, 0, 1), 8)
    k_ = np.clip(s_ / RIDGE_SOFT, -1, 1)
    lean_x -= w_ * ROOF * k_ * nx_[0]; lean_y -= w_ * ROOF * k_ * nx_[1]
    ridge_w = np.maximum(ridge_w, w_)
    for d_ in np.arange(5, 150, 5.0):                 # mesh points on the ridge line and just beside it
        for o_ in (-RIDGE_SOFT, 0, RIDGE_SOFT):
            ridge_pts.append((tx + ax[0] * d_ + nx_[0] * o_, ty + ax[1] * d_ + nx_[1] * o_))
ridge_pts = np.array(ridge_pts)
ridge_pts = ridge_pts[sample(gold_sdf, ridge_pts) > GOLD_EDGE + 1.5]
# The outer frame gets the same ridge as the mockup's frame: an outer and an inner facet. A flat frame top would
# mirror the app's two low front lights (they sit right in front of the lower left) as a white patch with a halo.
# candidate08 tried a ridge along the whole frame: it killed the white patch, but every small wobble of the traced
# outline bent the ridge's reflections. So the frame top is one smooth facet instead, leaning 12 degrees outward
# like a bezel, with its direction taken from a heavily smoothed outline so the reflection runs clean.
from_outside = ndi.distance_transform_edt(outline0)
frame_w = ndi.gaussian_filter(np.clip(1 - (from_outside - 34) / 12, 0, 1), 4) * (1 - ridge_w)
by0, bx0 = np.gradient(ndi.gaussian_filter(from_outside, 10))
bn = np.maximum(np.hypot(bx0, by0), 1e-6)
BEZEL = np.tan(np.radians(12)) * S
bezel_x, bezel_y = BEZEL * frame_w * bx0 / bn, BEZEL * frame_w * by0 / bn
# A gold line that stops on the enamel does not end in a blunt stub: over its last stretch it sinks until it is
# level with the enamel, where the mockup's painted line carries on. (The frame's own points are not line ends.)
fade = np.ones((H, W)); sunk = 0
for cx_, cy_, _, _ in line_ends:
    if from_outside[int(round(cy_)), int(round(cx_))] < 26:
        continue
    fade = np.minimum(fade, np.clip((np.hypot(xx - cx_, yy - cy_) - 3) / 18, 0, 1)); sunk += 1
fade = ndi.gaussian_filter(fade, 2.0); fade = fade * fade * (3 - 2 * fade)
print('line ends that sink into the enamel:', sunk)
z_gold = gold_level + GOLD_RISE * fade * round_edge(gold_d, GOLD_EDGE) + ridge_w * ROOF * np.clip(gold_d - GOLD_EDGE, 0, ROOF_CAP)
gy, gx = np.gradient(ndi.gaussian_filter(gold_sdf, 2.5))      # a smooth field for directions, so reflections never crinkle
ry2, rx2 = gy, gx
# Shading on the rounded edge leans at most 38 degrees: a steeper lean mirrors the bright studio wall and,
# on a line only a few phone pixels wide, breaks into sparkle.
EDGE_LEAN = np.tan(np.radians(32)) * S
# A bevel thinner than a phone pixel breaks into dots along curved lines. So the edge is a soft shoulder about
# two phone pixels wide whose shading leans 32 degrees at the very edge and eases to flat: no crease, no thin strip.
edge_slope = EDGE_LEAN * np.clip(1 - gold_d / GOLD_EDGE, 0, 1) * fade
# the whole badge is very slightly domed in its shading, so the flat gold shows one smooth sweep of light
DOME = .026        # tilt per unit from the center: about 4 degrees at the outer edge
dome_x, dome_y = -DOME * (xx - CX) * S * S, -DOME * (yy - (TOP + BOT) / 2) * S * S
gold_zx, gold_zy = edge_slope * gx + lean_x + dome_x, edge_slope * gy + lean_y + dome_y

# The bolt's rim is two bands, as in the mockup: a raised outer band, then a wide inner bevel that slopes down to the
# yellow face. Both are real gold. (With only the outer band real, the inner band was painted fill and came out
# streaky next to the real rim: Blender zoom of candidates 20 and 21. As two flat bands with a narrow step between
# them, the step was thinner than two phone pixels and broke into a dotted line in the simulator: candidate23.)
# Every band here is at least 8 px wide in the mockup, more than two phone pixels.
RIM_TOTAL = 28.
RIM_FLAT = 13.           # where the flat outer band ends and the inner bevel begins


def rim_height(d):
    """The rim's cross section in units of RIM_RISE, by distance in from the bolt's edge (px)."""
    d = np.asarray(d, float)
    up = 1 - (1 - np.clip(d / RIM_EDGE, 0, 1)) ** 2                              # 0 to 5 px: soft shoulder up
    return up - 1.4 * np.clip((d - RIM_FLAT) / (RIM_TOTAL - RIM_FLAT), 0, 1)     # 13 to 28 px: one even bevel down, ending just under the face


rim_sdf = np.minimum(bolt_sdf, RIM_TOTAL - bolt_sdf)
z_rim = bolt_z + RIM_RISE * round_edge(np.maximum(rim_sdf, 0), RIM_EDGE)
ry, rx = np.gradient(ndi.gaussian_filter(rim_sdf, 1.5))
by_ = (BOLT_TIP_Z - BOLT_TOP_Z) / (G[1] - 296)
rs = np.tan(np.radians(28)) * S * np.clip(1 - np.maximum(rim_sdf, 0) / RIM_EDGE, 0, 1)
rim_zx, rim_zy = rs * rx + dome_x, by_ + rs * ry + dome_y



def bolt_ring(inset):
    """The bolt's outline moved inward by `inset`, corner for corner (sharp mitred corners, same vertex order)."""
    P = BOLT; n = len(P); out = []
    area = sum(P[i][0] * P[(i + 1) % n][1] - P[(i + 1) % n][0] * P[i][1] for i in range(n))
    sgn = 1 if area > 0 else -1
    for i in range(n):
        e0 = P[i] - P[i - 1]; e1 = P[(i + 1) % n] - P[i]
        e0 = e0 / np.linalg.norm(e0); e1 = e1 / np.linalg.norm(e1)
        n0 = sgn * np.array([-e0[1], e0[0]]); n1 = sgn * np.array([-e1[1], e1[0]])
        out.append(P[i] + inset * (n0 + n1) / (1 + n0 @ n1))
    return np.array(out)


face_sdf = polygon_sdf(bolt_ring(RIM_TOTAL - 2))
# The badge's true outline is the outline of its pieces (the first trace also caught a sliver of the mockup's shadow).
whole = ndi.binary_fill_holes(ndi.binary_closing(gold | pearl2 | blue2 | boltmask, disk(4)))
sil_in = signed(whole, 1.3)
blue_sdf = signed(ndi.binary_dilation(blue2, disk(6)) & (sil_in > 3), 1.0)
pearl_out_sdf = signed(ndi.binary_dilation(pearl2, disk(6)) & (sil_in > 3), 1.0)
py_, px_ = np.gradient(z_pearl)

# ---------- meshing ----------
parts = []


def contour(f, cell):
    out = []
    a, b = f[:, :-1], f[:, 1:]; m = (a >= 0) != (b >= 0); y, x = np.nonzero(m); t = a[m] / (a[m] - b[m]); out.append(np.c_[x + t, y])
    a, b = f[:-1, :], f[1:, :]; m = (a >= 0) != (b >= 0); y, x = np.nonzero(m); t = a[m] / (a[m] - b[m]); out.append(np.c_[x, y + t])
    p = np.vstack(out)
    _, idx = np.unique(np.round(p / cell).astype(np.int64), axis=0, return_index=True)
    return p[idx]


def mesh(sdf, edge_cell, rings=(), grid=None, grid_min=None, extra=None, tol=1.0, mid=.2):
    pts = [contour(sdf, edge_cell)]
    if extra is not None:
        pts.append(np.asarray(extra, float))
    for level, cell in rings:
        pts.append(contour(sdf - level, cell))
    if grid:
        gyy, gxx = np.mgrid[0:H:grid, 0:W:grid]
        keep = sdf[gyy, gxx] > (grid_min if grid_min is not None else edge_cell)
        pts.append(np.c_[gxx[keep], gyy[keep]].astype(float))
    p = np.vstack(pts)
    # Two points almost on top of each other make sliver triangles: the later one goes.
    from scipy.spatial import cKDTree
    pairs = cKDTree(p).query_pairs(.6, output_type='ndarray')
    if len(pairs):
        drop = np.zeros(len(p), bool)
        for i_, j_ in pairs[np.argsort(pairs[:, 1])]:
            if not drop[i_]:
                drop[j_] = True
        p = p[~drop]
    t = Delaunay(p).simplices
    q = p[t]
    tests = np.stack([q.mean(1), (q[:, 0] + q[:, 1]) / 2, (q[:, 1] + q[:, 2]) / 2, (q[:, 2] + q[:, 0]) / 2], 1).reshape(-1, 2)
    # Keep a triangle when its middle is inside the shape and no edge strays far outside. A stricter test dropped
    # long thin triangles beside curved edges and left slits that showed the gold body as whiskers (candidate05).
    sd = sample(sdf, tests).reshape(-1, 4)
    ok = (sd[:, 0] > -mid) & (sd[:, 1:] > -tol).all(1)
    # Sliver triangles stay in. Dropping one leaves a point sitting on its neighbour's edge, and that hairline
    # crack showed in the app as a dark pinhole on the pearl (candidates 08 to 12).
    t = t[ok]
    used = np.unique(t)
    remap = np.full(len(p), -1); remap[used] = np.arange(len(used))
    return p[used], remap[t]


# The app draws a dead pixel wherever one of its eight lights reflects straight into the camera (the surface
# direction equals the half way direction between light and camera; found on candidates 01 to 14, see
# light_centers.py). The enamel only glows, so its shading direction is free: it gets one fixed direction that stays
# at least 10 degrees away from every light's reflection across the whole badge at rest.
ENAMEL_NORMAL = np.array([0.383, -0.321, 0.866])


def solid(name, role, side_role, sdf, p, t, z, zx, zy, bevel=None):
    """A closed piece: sculpted front, mirrored back, walls around its outline.

    bevel = (is_edge_vertex, zx, zy): triangles that touch the outline form the bevel and get their own
    shading, so the crease between the bevel and the flat top is crisp instead of blended.
    """
    if bevel is not None:
        edge_v, bzx, bzy = bevel
        tri_edge = edge_v[t].any(1)
        m0 = len(p)
        t = np.where(tri_edge[:, None], t + m0, t)
        p = np.vstack([p, p]); z = np.r_[z, z]; zx = np.r_[zx, bzx]; zy = np.r_[zy, bzy]
        used = np.unique(t); remap = np.full(len(p), -1); remap[used] = np.arange(len(used))
        p, z, zx, zy, t = p[used], z[used], zx[used], zy[used], remap[t]
    n = len(p)
    X, Y = (p[:, 0] - CX) * S, 3.015 - (p[:, 1] - TOP) * S
    front = np.c_[X, Y, z]
    back = front * [1, 1, -1]
    nf = np.c_[-zx / S, zy / S, np.ones(n)]
    nf /= np.linalg.norm(nf, axis=1)[:, None]
    if role.startswith('art'):
        nf = np.tile(ENAMEL_NORMAL, (n, 1))
    nb = nf * [1, 1, -1]
    uv = np.c_[p[:, 0] / W, 1 - p[:, 1] / H]
    cr = np.cross(front[t[:, 1]] - front[t[:, 0]], front[t[:, 2]] - front[t[:, 0]])
    t = t.copy(); flip = cr[:, 2] < 0; t[flip] = t[flip][:, ::-1]
    faces = dict(name=name, role=role, v=np.vstack([front, back]), n=np.vstack([nf, nb]), uv=np.vstack([uv, uv]),
                 t=np.vstack([t, t[:, ::-1] + n]))
    # walls from the outline's edges; their normals lean 70% toward the face so the edge never flashes
    e = np.vstack([t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]])
    _, pid = np.unique(np.round(p, 4), axis=0, return_inverse=True)     # the same point may exist twice (bevel and top)
    key = np.sort(pid.ravel()[e], axis=1)
    _, first, count = np.unique(key, axis=0, return_index=True, return_counts=True)
    be = e[first[count == 1]]
    sy, sx = np.gradient(ndi.gaussian_filter(sdf, 3.0))    # smooth directions: no stripes along the side walls
    out = np.c_[-sample(sx, p), sample(sy, p), np.zeros(n)]
    out /= np.maximum(np.linalg.norm(out, axis=1)[:, None], 1e-9)
    wf = out * .45 + nf * .55; wf /= np.linalg.norm(wf, axis=1)[:, None]
    wb = wf * [1, 1, -1]
    walls = np.vstack([np.c_[be[:, 0], be[:, 1] + n, be[:, 1]], np.c_[be[:, 0], be[:, 0] + n, be[:, 1] + n]])
    wv = np.vstack([front, back])
    wc = np.cross(wv[walls[:, 1]] - wv[walls[:, 0]], wv[walls[:, 2]] - wv[walls[:, 0]])
    mid = wv[walls].mean(1)
    outward = np.vstack([out, out])[walls[:, 0]]
    bad = (wc * outward).sum(1) < 0
    walls[bad] = walls[bad][:, ::-1]
    used = np.unique(walls); remap = np.full(2 * n, -1); remap[used] = np.arange(len(used))     # only the walls' own points
    wall = dict(name=name + ' side walls', role=side_role, v=wv[used], n=np.vstack([wf, wb])[used], uv=np.vstack([uv, uv])[used], t=remap[walls])
    if role == side_role:
        # Same material: the faces and the side walls are stored as one mesh. Same triangles, same shading, one
        # thing less for the app to draw. (The gold frame stays in two: its side walls use a darker gold.)
        parts.append(dict(name=name, role=role, v=np.vstack([faces['v'], wall['v']]), n=np.vstack([faces['n'], wall['n']]),
                          uv=np.vstack([faces['uv'], wall['uv']]), t=np.vstack([faces['t'], wall['t'] + 2 * n])))
    else:
        parts.append(faces); parts.append(wall)


zero = np.zeros((H, W))

# base body: closes the badge behind everything
p, t = mesh(sil_in - 3, 9, grid=60, grid_min=12, tol=2.5, mid=1.5)
solid('Gold body', 'gold_side', 'gold_side', sil_in - 3, p, t, np.full(len(p), Z_BASE), np.zeros(len(p)), np.zeros(len(p)))

# blue enamel: field and ribbons, flat, carrying the picture
p, t = mesh(blue_sdf, 7, grid=40, grid_min=9, tol=4, mid=3)
solid('Blue enamel field and ribbons', 'art', 'art', blue_sdf, p, t, np.full(len(p), Z_BLUE), np.zeros(len(p)), np.zeros(len(p)))

# pearl clouds: domed
p, t = mesh(pearl_out_sdf, 5.5, rings=((12, 9), (32, 14)), grid=30, grid_min=46, tol=2.5, mid=1.5)
solid('Pearl clouds', 'art', 'art', pearl_out_sdf, p, t, sample(z_pearl, p), sample(px_, p), sample(py_, p))

# bolt face
from shapely.geometry import Polygon
def corners(inset):
    g = Polygon(BOLT).buffer(-inset, join_style=2, mitre_limit=8) if inset else Polygon(BOLT)
    return np.asarray(g.exterior.coords)[:-1]
p, t = mesh(face_sdf, 4, grid=34, grid_min=8, extra=bolt_ring(RIM_TOTAL - 2 + .01), tol=1.5, mid=1.0)
solid('Bolt yellow face', 'art_bolt', 'art_bolt', face_sdf, p, t, sample(bolt_z, p) - .006 - .07 * sample(bolt_under, p), np.zeros(len(p)), np.full(len(p), by_))

# bolt rim: real gold
# The rim is built as even strips that run along the bolt's straight edges, ring by ring, so its shoulders are
# perfectly straight. (Meshed from scattered points it showed a saw tooth along every edge.)
insets = [0, 1.5, 3.2, 5, 13, 18, 23, 28]
rings_xy = [bolt_ring(d) for d in insets]
nb = len(BOLT); segs = [max(2, int(np.ceil(np.linalg.norm(BOLT[(i + 1) % nb] - BOLT[i]) / 14))) for i in range(nb)]
inward = []
for i in range(nb):
    e = BOLT[(i + 1) % nb] - BOLT[i]; e = e / np.linalg.norm(e); nrm = np.array([-e[1], e[0]])
    mid = (BOLT[i] + BOLT[(i + 1) % nb]) / 2
    inward.append(nrm if bolt_sdf[int(round(mid[1] + 3 * nrm[1])), int(round(mid[0] + 3 * nrm[0]))] > 0 else -nrm)
pts, dirs, dist = [], [], []
for k, d in enumerate(insets):
    R_ = rings_xy[k]
    for i in range(nb):
        for j in range(segs[i]):
            f = j / segs[i]
            pts.append(R_[i] * (1 - f) + R_[(i + 1) % nb] * f)
            if j == 0:
                b_ = inward[i - 1] + inward[i]; dirs.append(b_ / np.linalg.norm(b_))
            else:
                dirs.append(inward[i])
            dist.append(d)
p = np.array(pts); dirs = np.array(dirs); dist = np.array(dist); M = sum(segs)
t = []
for k in range(len(insets) - 1):
    for a in range(M):
        a2 = (a + 1) % M
        t += [(k * M + a, k * M + a2, (k + 1) * M + a2), (k * M + a, (k + 1) * M + a2, (k + 1) * M + a)]
t = np.array(t)
zr = sample(bolt_z, p) + RIM_RISE * rim_height(dist) - .07 * sample(bolt_under, p)
# Shading: the outer shoulder eases from 28 degrees to flat; the inner bevel leans a steady 12 degrees inward, a
# quiet change of tone with no glint line (the owner rejected wide glint lines on ridges inside an emblem).
lean = np.tan(np.radians(28)) * S * np.clip(1 - dist / RIM_EDGE, 0, 1) - np.tan(np.radians(12)) * S * np.clip((dist - RIM_FLAT + 2.5) / 5, 0, 1)
solid('Bolt gold rim', 'gold', 'gold', bolt_sdf, p, t, zr, sample(dome_x, p) + lean * dirs[:, 0], by_ + sample(dome_y, p) + lean * dirs[:, 1])

# all other gold: frame, four points, cloud outlines and spirals


def thin_out(pts, radius):
    """Keep points so that no two are closer than their radius (a number, or one per point)."""
    from scipy.spatial import cKDTree
    pts = np.asarray(pts, float); rad = np.broadcast_to(radius, len(pts)).astype(float)
    tree = cKDTree(pts); keep = np.ones(len(pts), bool)
    for i_ in range(len(pts)):
        if keep[i_]:
            for j_ in tree.query_ball_point(pts[i_], rad[i_]):
                if j_ > i_:
                    keep[j_] = False
    return pts[keep]


def mesh_from_points(sdf, p, tol, mid):
    p = thin_out(p, .6)
    t = Delaunay(p).simplices
    q = p[t]
    tests = np.stack([q.mean(1), (q[:, 0] + q[:, 1]) / 2, (q[:, 1] + q[:, 2]) / 2, (q[:, 2] + q[:, 0]) / 2], 1).reshape(-1, 2)
    sd = sample(sdf, tests).reshape(-1, 4)
    t = t[(sd[:, 0] > -mid) & (sd[:, 1:] > -tol).all(1)]
    used = np.unique(t)
    remap = np.full(len(p), -1); remap[used] = np.arange(len(used))
    return p[used], remap[t]


# The gold's edge is built in rows: every outline point has its own two shoulder points straight behind it, so the
# shoulder is an even ribbon. (Shoulder points scattered on their own gave narrow bands a saw tooth: Blender zoom of
# candidate17.) Outline points sit closer together where the outline bends tightly, so round ends stay round. Bands
# too narrow for a shoulder on each side get a row of points along their middle instead.
phi = ndi.gaussian_filter(gold_sdf, 1.2); fy, fx = np.gradient(phi); fn = np.maximum(np.hypot(fx, fy), 1e-6)
kap = np.abs(np.gradient(fx / fn, axis=1) + np.gradient(fy / fn, axis=0))
kap = ndi.maximum_filter(ndi.gaussian_filter(kap, 1.0), size=7)
edge_all = contour(gold_sdf, .35)
tight = sample(kap, edge_all) > .06
edge_pts = thin_out(edge_all[np.argsort(~tight, kind='stable')], np.where(np.sort(~tight, kind='stable'), 3.6, 1.5))
inward = np.c_[sample(fx / fn, edge_pts), sample(fy / fn, edge_pts)]
ring_a = edge_pts + inward * (GOLD_EDGE / 2); ring_a = ring_a[sample(gold_sdf, ring_a) > GOLD_EDGE / 2 - .5]
ring_b = edge_pts + inward * GOLD_EDGE; ring_b = ring_b[sample(gold_sdf, ring_b) > GOLD_EDGE - .6]
ring_a = thin_out(ring_a, 2.0); ring_b = thin_out(ring_b, 2.6)
narrow = ndi.binary_dilation(gold & ~ndi.binary_opening(gold, disk(6)), disk(2)) & gold
gm = np.hypot(*np.gradient(gold_sdf))
my_, mx_p = np.nonzero(narrow & (gm < .8) & (gold_sdf > 1.5))
if len(mx_p):
    cell = (mx_p // 3) * 100000 + (my_ // 3); order = np.lexsort((-gold_sdf[my_, mx_p], cell))
    first = np.r_[True, cell[order][1:] != cell[order][:-1]]
    middle = thin_out(np.c_[mx_p[order][first], my_[order][first]].astype(float), 2.6)
else:
    middle = np.zeros((0, 2))
inner = np.vstack([contour(gold_sdf - 14, 11), contour(gold_sdf - 30, 15)])
print('gold points: outline', len(edge_pts), 'shoulder', len(ring_a) + len(ring_b), 'middle rows', len(middle), 'inside', len(inner))
p, t = mesh_from_points(gold_sdf, np.vstack([edge_pts, ring_a, ring_b, middle, inner, ridge_pts]), tol=1.2, mid=.6)
edge = sample(edge_slope, p)
solid('Gold frame, points and cloud outlines', 'gold', 'gold_side', gold_sdf, p, t, sample(z_gold, p),
      edge * sample(gx, p) + sample(lean_x, p) + sample(dome_x, p) + sample(bezel_x, p),
      edge * sample(gy, p) + sample(lean_y, p) + sample(dome_y, p) + sample(bezel_y, p))

# App contract: nothing above Y = 3.015. Finer outline points can reach a hair past the first trace's top.
top_y = max(float(q['v'][:, 1].max()) for q in parts)
if top_y > 3.0148:
    for q in parts:
        q['v'][:, 1] -= top_y - 3.0148
total = sum(len(q['t']) for q in parts)
arrays = {}
for i, q in enumerate(parts):
    arrays[f'{i}_v'] = q['v'].astype(np.float32); arrays[f'{i}_n'] = q['n'].astype(np.float32)
    arrays[f'{i}_uv'] = q['uv'].astype(np.float32); arrays[f'{i}_t'] = q['t'].astype(np.int32)
np.savez_compressed(C / 'geometry.npz', **arrays)
allv = np.vstack([q['v'] for q in parts])
meta = dict(parts=[dict(name=q['name'], role=q['role'], triangles=int(len(q['t']))) for q in parts], triangles=int(total),
            units_per_pixel=S, center_x=CX, top=int(TOP), bounds_min=allv.min(0).tolist(), bounds_max=allv.max(0).tolist(), mockup_size=[W, H])
(C / 'parts.json').write_text(json.dumps(meta, indent=2) + '\n')
np.savez_compressed(C / 'shapes.npz', **{'Gold body': sil_in - 3 > 0, 'Blue enamel field and ribbons': blue_sdf > 0, 'Pearl clouds': pearl_out_sdf > 0,
                                         'Bolt yellow face': face_sdf > 0, 'Bolt gold rim': rim_sdf > 0, 'Gold frame, points and cloud outlines': gold_sdf > 0})
np.savez_compressed(C / 'masks.npz', gold=gold, pearl=pearl2, blue=blue2, bolt=boltmask, face=face_sdf > 0, rim=(rim_sdf > 0), sil=sil,
                    bolt_visible=bolt_visible)

# ---------- a quick top view to check the shapes before Blender ----------
light = np.array([-.45, .55, .7]); light /= np.linalg.norm(light)
top = np.full((H, W), -1.); shade = im.copy() * 0 + .12
order = [('blue', blue_sdf > 0, np.full((H, W), Z_BLUE), None), ('pearl', pearl_out_sdf > 0, z_pearl, None), ('face', face_sdf > 0, bolt_z, None),
         ('rim', rim_sdf > 0, z_rim, (rim_zx, rim_zy)), ('gold', gold_sdf > 0, z_gold, (gold_zx, gold_zy))]
for name, m, z, grad in order:
    win = m & (z > top)
    if grad is None:
        shade[win] = im[win]
    else:
        nrm = np.dstack([-grad[0] / S, grad[1] / S, np.ones((H, W))]); nrm /= np.linalg.norm(nrm, axis=2)[..., None]
        lit = np.clip((nrm @ light), 0, 1) ** 1.5
        shade[win] = (np.array([.95, .68, .22])[None] * (.25 + .95 * lit[win][:, None]))
    top[win] = z[win]
Image.fromarray(np.uint8(np.clip(np.concatenate([im, shade], 1), 0, 1) * 255)).save(C / 'topview.png')
print('parts', len(parts), 'triangles', total, 'bounds', np.round(allv.min(0), 3), np.round(allv.max(0), 3))
for q in parts:
    print(f"  {q['name']}: {len(q['t'])}")
