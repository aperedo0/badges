"""Tone of a facet as a function of its normal (front view), as a disc image.

Disc center = facet facing the camera; edge = 45 degrees tilt. Right of the
disc = facet tilted to the viewer's right, top = tilted up.
"""
import sys, json
import numpy as np
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/tools')
import foilsim
from PIL import Image, ImageDraw
prm = dict(foilsim.DEFAULT, **json.loads(sys.argv[2]))
height = float(sys.argv[3]) if len(sys.argv) > 3 else 0.4
R = 140
yy, xx = np.mgrid[-R:R + 1, -R:R + 1] / R
inside = xx ** 2 + yy ** 2 <= 1
tilt = np.radians(45) * np.sqrt(xx ** 2 + yy ** 2)
az = np.arctan2(-yy, xx)
n = np.stack([np.sin(tilt) * np.cos(az), np.sin(tilt) * np.sin(az), np.cos(tilt)], -1)
p = np.zeros_like(n); p[..., 2] = height; p[..., 1] = 0.3
d = foilsim.unit(p - foilsim.EYE)
img = foilsim.display(foilsim.shade(p, n, d, prm))
img[~inside] = 0.05
im = Image.fromarray(np.uint8(img * 255)).resize((2 * R + 1, 2 * R + 1))
dr = ImageDraw.Draw(im)
for t in (15, 30):
    r = R * t / 45; dr.ellipse((R - r, R - r, R + r, R + r), outline=(80, 200, 255))
im.save(sys.argv[1])
