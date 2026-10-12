"""specks.py <shot.png> <outline.npz> [out_marked.png] : counts isolated pixel specks inside the gem: a pixel whose luminance differs by more than 0.20
from the median of its 8 neighbours while those neighbours agree with each other (spread under 0.08), plus the same inside a 6 px band along the outline.
Marks them red in out_marked.png (4x zoom of the gem's box)."""
import sys, numpy as np
from PIL import Image
from scipy.ndimage import median_filter, maximum_filter, minimum_filter, binary_erosion, binary_dilation
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/diamond/gem_shader_20261011/tools')
from measure_gem import gem_mask
img = Image.open(sys.argv[1]).convert('RGB'); rgb = np.asarray(img, float) / 255
lum = rgb @ [0.2126, 0.7152, 0.0722]
H, W = lum.shape
neighbours = np.stack([np.roll(np.roll(lum, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dx) != (0, 0)])
med = np.median(neighbours, axis=0); spread = neighbours.max(0) - neighbours.min(0)
speck = (np.abs(lum - med) > 0.20) & (spread < 0.08)
inner = gem_mask(sys.argv[2], img.size)
outline_band = inner & ~binary_erosion(inner, iterations=6)
inside = speck & inner
print(f'specks inside gem: {inside.sum()}  of which within 6 px of the outline: {(speck & outline_band).sum()}  (bright {((lum - med) > 0)[inside].sum()}, dark {((lum - med) < 0)[inside].sum()})')
if len(sys.argv) > 3:
    ys, xs = np.where(inner); b = (xs.min() - 10, ys.min() - 10, xs.max() + 10, ys.max() + 10)
    crop = img.crop(b).resize(((b[2] - b[0]) * 3, (b[3] - b[1]) * 3), Image.NEAREST); arr = np.asarray(crop).copy()
    for y, x in zip(*np.where(inside)):
        cx, cy = (x - b[0]) * 3 + 1, (y - b[1]) * 3 + 1
        arr[max(cy - 6, 0):cy + 7, max(cx - 6, 0):cx + 7][[0, -1], :] = [255, 0, 0]
        arr[max(cy - 6, 0):cy + 7, max(cx - 6, 0):cx + 7][:, [0, -1]] = [255, 0, 0]
    Image.fromarray(arr).save(sys.argv[3]); print(sys.argv[3])
