"""still_cut.py <model.npz> <app.png> <out.png> : the 600 x 600 Badges screen still from a real Home render, as Codex's proof.py
cut them: the fixed art frame (the coins' 6.03 units = 108 of 120), alpha from the 4x supersampled projected geometry, the stage
behind edge pixels removed using the nearest outside color."""
import sys, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from common import to_screen
d = np.load(sys.argv[1]); im = Image.open(sys.argv[2]).convert('RGB')
center = np.array([540, 656]) * 47 / 60 + [180, 70]; side = 586 * 120 / 108 * 47 / 60
box = tuple(np.round(np.r_[center - side / 2, center + side / 2]).astype(int))
art = im.crop(box); SS = 4; alpha = Image.new('L', (art.width * SS, art.height * SS), 0); dr = ImageDraw.Draw(alpha)
for t in to_screen(d['ALLP'].reshape(-1, 3)).reshape(-1, 3, 2):
    dr.polygon([tuple((p - box[:2]) * SS) for p in t], fill=255)
alpha = alpha.resize(art.size, Image.Resampling.LANCZOS); av = np.asarray(alpha, float) / 255; rgb = np.asarray(art, float) / 255
_, (iy, ix) = distance_transform_edt(av > .01, return_indices=True); bg = rgb[iy, ix]
rgb = np.clip((rgb - bg * (1 - av[..., None])) / np.maximum(av[..., None], .03), 0, 1)
rgba = Image.fromarray(np.dstack([np.uint8(rgb * 255 + .5), np.uint8(av * 255 + .5)]), 'RGBA').convert('RGBa').resize((600, 600), Image.Resampling.LANCZOS).convert('RGBA')
rgba.save(sys.argv[3], optimize=True); print(sys.argv[3], rgba.size)
