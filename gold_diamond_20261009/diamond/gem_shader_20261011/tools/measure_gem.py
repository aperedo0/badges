"""measure_gem.py <shot.png> <outline.npz> : mean color, hue and luminance of a Home shot inside the gem's own projected outline
(the outline is the model's triangles at rest, projected the way still_cut.py does it; pixels within 2 px of the edge are left out)."""
import sys, colorsys, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_erosion
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from common import to_screen
def gem_mask(npz, size):
    d = np.load(npz); mask = Image.new('L', size, 0); dr = ImageDraw.Draw(mask)
    for t in to_screen(d['ALLP'].reshape(-1, 3)).reshape(-1, 3, 2): dr.polygon([tuple(p) for p in t], fill=255)
    return binary_erosion(np.asarray(mask) > 0, iterations=2)
def srgb_to_linear(v): return np.where(v <= .04045, v / 12.92, ((v + .055) / 1.055) ** 2.4)
if __name__ == '__main__':
    img = Image.open(sys.argv[1]).convert('RGB'); rgb = np.asarray(img, float) / 255; m = gem_mask(sys.argv[2], img.size)
    px = rgb[m]; mean = px.mean(0); h, s, v = colorsys.rgb_to_hsv(*mean)
    luma = px @ [0.2126, 0.7152, 0.0722]; lin = srgb_to_linear(px) @ [0.2126, 0.7152, 0.0722]
    print(f'pixels {m.sum()}  mean RGB (0-255) {(mean*255).round(1)}  hue {h*360:.1f} deg  sat {s:.3f}  display luma {luma.mean():.4f}  linear luminance {lin.mean():.4f}  white(>0.95) {(px.min(1) > 0.95).mean()*100:.1f}%')
