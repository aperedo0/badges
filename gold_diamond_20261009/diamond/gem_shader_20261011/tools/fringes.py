"""fringes.py <shot.png> <outline.npz> [out.png] : pixels inside the gem whose color is clearly not blue (hue outside 185..245 degrees, saturation above 0.18, value above 0.25),
as a share of the gem and as a count; marks them white on a dimmed 3x copy."""
import sys, colorsys, numpy as np
from PIL import Image
from matplotlib.colors import rgb_to_hsv
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/diamond/gem_shader_20261011/tools')
from measure_gem import gem_mask
img = Image.open(sys.argv[1]).convert('RGB'); rgb = np.asarray(img, float) / 255; inner = gem_mask(sys.argv[2], img.size)
hsv = rgb_to_hsv(rgb); h = hsv[..., 0] * 360
off = inner & (hsv[..., 1] > 0.18) & (hsv[..., 2] > 0.25) & ((h < 185) | (h > 245))
print(f'off-blue pixels: {off.sum()} ({off.sum() / inner.sum() * 100:.2f}% of the gem)')
if len(sys.argv) > 3:
    ys, xs = np.where(inner); b = (xs.min() - 10, ys.min() - 10, xs.max() + 10, ys.max() + 10)
    out = (rgb * 0.45); out[off] = [1, 1, 0]
    Image.fromarray((out * 255).astype(np.uint8)).crop(b).resize(((b[2] - b[0]) * 2, (b[3] - b[1]) * 2), Image.NEAREST).save(sys.argv[3]); print(sys.argv[3])
