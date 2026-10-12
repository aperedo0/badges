"""blobs.py <shot.png> <outline.npz> [out.png] : small blobs (1 to 8 px) that differ from the median of their 9 x 9 surroundings by more than 0.25 luminance, inside the gem;
bright and dark are counted separately; marked in a 3x zoom."""
import sys, numpy as np
from PIL import Image
from scipy.ndimage import median_filter, label
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/diamond/gem_shader_20261011/tools')
from measure_gem import gem_mask
img = Image.open(sys.argv[1]).convert('RGB'); rgb = np.asarray(img, float) / 255
lum = rgb @ [0.2126, 0.7152, 0.0722]; inner = gem_mask(sys.argv[2], img.size)
med = median_filter(lum, size=9)
res = {}
for name, mask in (('bright', (lum - med) > 0.25), ('dark', (med - lum) > 0.25)):
    lab, n = label(mask & inner); sizes = np.bincount(lab.ravel())[1:]
    small = [i + 1 for i, s in enumerate(sizes) if s <= 8]; res[name] = small
    print(f'{name}: {len(small)} small blobs (<= 8 px), {n - len(small)} larger')
if len(sys.argv) > 3:
    ys, xs = np.where(inner); b = (xs.min() - 10, ys.min() - 10, xs.max() + 10, ys.max() + 10)
    crop = img.crop(b).resize(((b[2] - b[0]) * 3, (b[3] - b[1]) * 3), Image.NEAREST); arr = np.asarray(crop).copy()
    for name, color in (('bright', (255, 0, 0)), ('dark', (255, 255, 0))):
        lab, _ = label(((lum - med) > 0.25 if name == 'bright' else (med - lum) > 0.25) & inner)
        for i in res[name]:
            ys2, xs2 = np.where(lab == i); cx = int((xs2.mean() - b[0]) * 3 + 1); cy = int((ys2.mean() - b[1]) * 3 + 1)
            arr[cy - 8:cy + 9, cx - 8:cx + 9][[0, -1], :] = color; arr[cy - 8:cy + 9, cx - 8:cx + 9][:, [0, -1]] = color
    Image.fromarray(arr).save(sys.argv[3]); print(sys.argv[3])
