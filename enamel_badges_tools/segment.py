"""Split an enamel badge mockup into gold (walls, rims) and enamel cells.

Gold: gold hued or bright pixels that form narrow structures (walls), or the band near the outline.
Enamel: the remaining wide regions, labeled into cells.
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def segment(path, mask, wall_r=11, rim_px=None):
    a = np.asarray(Image.open(path).convert('RGB')).astype(float) / 255
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(2), a.min(2); sat = (mx - mn) / np.maximum(mx, 1e-6)
    hue = np.zeros_like(mx); d = np.maximum(mx - mn, 1e-6)
    hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    # v7: ivory and warm white enamel (saturation under about 0.2) is no longer taken for a gold highlight
    goldish = ((hue > 28) & (hue < 62) & (sat > 0.25)) | ((lum > 0.80) & (hue > 20) & (hue < 70) & (sat > 0.22))
    if mask is None:   # light background: the badge is everything inside its outer gold outline
        # v7: everything not backdrop: saturated, dark, or highlights whiter than the backdrop (0.93 to 0.947 here)
        cand = (sat > 0.3) | (lum < 0.35) | (lum > 0.965)
        mask = ndi.binary_fill_holes(ndi.binary_closing(cand, structure=disk(9)))
        mask = ndi.binary_opening(mask, structure=disk(3))   # v7: drop thin shadow strips stuck to the outline
        lab0, n0 = ndi.label(mask); sz0 = ndi.sum(mask, lab0, range(1, n0 + 1)); mask = lab0 == (1 + int(np.argmax(sz0)))
    goldish &= mask
    # local contrast: metal walls have strong light and dark within a few pixels
    lc = ndi.maximum_filter(lum, 7) - ndi.minimum_filter(lum, 7)
    # wide regions survive an opening; walls do not
    wide = ndi.binary_opening(goldish, structure=disk(wall_r))
    gold = goldish & ~wide
    # near the outline: rim band
    dist_edge = ndi.distance_transform_edt(mask)
    if rim_px:
        gold |= goldish & (dist_edge < rim_px)
    # thin, high contrast warm lines inside wide regions are walls too
    gold |= goldish & (lc > 0.45) & ~ndi.binary_erosion(wide, structure=disk(3))
    # bridge short breaks in walls (bright highlights) with warm, light pixels next to gold
    warm_light = (lum > 0.62) & (hue > 15) & (hue < 75) & (sat > 0.22) & mask   # v7: never bridge into white cloud
    for _ in range(3):
        gold |= warm_light & ndi.binary_dilation(gold, structure=disk(2))
    gold = ndi.binary_closing(gold, structure=disk(3)) & mask
    gold = ndi.binary_opening(gold, structure=disk(1))
    enamel = mask & ~gold
    lab, n = ndi.label(enamel)
    sizes = ndi.sum(enamel, lab, range(1, n + 1))
    small = np.isin(lab, 1 + np.nonzero(sizes < 150)[0])
    gold |= small; enamel &= ~small
    lab, n = ndi.label(enamel)
    return a, gold, enamel, lab, n, mask


if __name__ == '__main__':
    path, mask_path, out = sys.argv[1:4]
    wall_r = int(sys.argv[4]) if len(sys.argv) > 4 else 11
    rim = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    mask = None if mask_path == 'none' else np.load(mask_path)
    a, gold, enamel, lab, n, mask = segment(path, mask, wall_r, rim or None)
    np.savez_compressed(out.replace('.png', '.npz'), gold=gold, enamel=enamel, mask=mask)
    vis = np.zeros(a.shape)
    rng = np.random.default_rng(1); cols = rng.uniform(0.2, 1, (n + 1, 3))
    vis[enamel] = cols[lab[enamel]] * 0.6
    vis[gold] = (1.0, 0.8, 0.1)
    Image.fromarray(np.uint8(vis * 255)).resize((600, int(600 * a.shape[0] / a.shape[1]))).save(out)
    print('cells', n, 'gold share', round(float(gold.sum() / mask.sum()), 3))
