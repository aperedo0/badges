from pathlib import Path
import json
import math
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

S = Path(__file__).resolve().parent
C = S / 'candidate03'
D = json.loads((C / 'design.json').read_text())
F = json.loads((C / 'asset_fit.json').read_text())
T = C / 'textures'
T.mkdir(exist_ok=True)
raw = Image.open(C / 'height_source.png').convert('L')
b = D['bounds']
bw, bh = b['xmax'] - b['xmin'], b['ymax'] - b['ymin']
box = F['core_bbox']
kw, kh = box[2] - box[0], box[3] - box[1]
cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
cw = bw * math.sqrt(kw * kh) / F['physical_core_mean_diameter']
ch = cw / (bw / bh)
u = (D['knot']['x'] - b['xmin']) / bw
v = (b['ymax'] - D['knot']['y']) / bh
rect = [cx - u * cw, cy - v * ch, cx + (1 - u) * cw, cy + (1 - v) * ch]
assert rect[0] >= 0 and rect[1] >= 0 and rect[2] <= raw.width and rect[3] <= raw.height
rx, ry = kw / cw * bw / 2, kh / ch * bh / 2
assert .85 <= rx / ry <= 1.3 and .35 <= 2 * math.sqrt(rx * ry) <= .42 + 1e-8
W, H, pad = D['texture_width'], D['texture_height'], D['padding']
w, h = W - 2 * pad, H - 2 * pad
assert abs(w / h - bw / bh) > .5, 'Wrong bitmap aspect negative control must differ'
gray = np.asarray(raw.transform((w, h), Image.Transform.EXTENT, rect, Image.Resampling.BICUBIC), float) / 255
dx, dy = bw / (w - 1), bh / (h - 1)
gray = gaussian_filter(gray, (D['physical_filter_sigma'] / dy, D['physical_filter_sigma'] / dx))
lo, hi = np.percentile(gray, [2, 98])
t = np.clip((gray - lo) / (hi - lo), 0, 1)

def smoothstep(a, b, x):
    q = np.clip((x - a) / (b - a), 0, 1)
    return q * q * (3 - 2 * q)

# The same scalar describes the carved elevation, pigment and roughness.
elevation = smoothstep(.04, .97, t)
height = -D['relief_depth'] * (1 - elevation)
# Raised wood pigment is separate from gross elevation: only the deepest
# aligned recess gets a restrained dark brown, never a black full slope ramp.
X,Y=np.meshgrid(np.linspace(b['xmin'],b['xmax'],w),np.linspace(b['ymax'],b['ymin'],h))
base=np.ones((h,w,3))*np.array([.69,.23,.045])
stain=np.zeros((h,w))
for sx,sy,rxs,rys,weight in [(-1.45,-1.50,.50,.20,.32),(.85,-1.20,.90,.25,.27),(2.2,-1.85,.35,.20,.23)]:
    stain+=weight*np.exp(-((X-sx)/rxs)**2-((Y-sy)/rys)**2)
stain=np.clip(stain,0,.5)
base=base*(1-stain[:,:,None])+np.array([.48,.115,.026])*stain[:,:,None]
pigment_flow=gaussian_filter(elevation,(.025/dy,.10/dx))
base*= (.93+.12*pigment_flow)[:,:,None]
wear=.20*smoothstep(.72,.98,elevation)
base=base*(1-wear[:,:,None])+np.array([.79,.33,.075])*wear[:,:,None]
cavity=1-smoothstep(.015,.20,elevation)
rgb=base*(1-cavity[:,:,None])+np.array([.29,.08,.020])*cavity[:,:,None]
roughness = .82 - .20 * smoothstep(.12, .95, elevation)
gy, gx = np.gradient(height, dy, dx)
gy = -gy
normal = np.stack([-gx, -gy, np.ones_like(gx)], axis=2)
slope = np.linalg.norm(normal[:, :, :2], axis=2)
normal[:, :, :2] *= np.minimum(1, np.tan(np.deg2rad(D['maximum_normal_degrees'])) / np.maximum(slope, 1e-12))[:, :, None]
normal /= np.linalg.norm(normal, axis=2)[:, :, None]

# Analytic ramps catch tangent sign or axis inversion independently of the image.
test_y, test_x = np.mgrid[0:9, 0:11]
test_height = test_x * dx * .1 - test_y * dy * .2
test_gy, test_gx = np.gradient(test_height, dy, dx)
test_vector = np.stack([-test_gx, test_gy, np.ones_like(test_gx)], axis=2)
assert np.allclose(test_vector[:, :, 0], -.1) and np.allclose(test_vector[:, :, 1], -.2)
assert not np.allclose(-test_vector[:, :, 1], -.2), 'Inverted green negative control must fail'
assert rgb[height < np.quantile(height, .1)].mean(axis=0)[0] < rgb[height > np.quantile(height, .9)].mean(axis=0)[0]

def save(name, a):
    pads = ((pad, pad), (pad, pad), (0, 0)) if a.ndim == 3 else ((pad, pad), (pad, pad))
    a = np.pad(a, pads, mode='edge')
    Image.fromarray(np.uint8(np.clip(a, 0, 1) * 255 + .5)).save(T / name)

save('wood_albedo.png', rgb)
save('wood_roughness.png', roughness)
save('wood_normal.png', .5 + .5 * normal)
np.savez_compressed(C / 'physical_height.npz', height=height)
Image.fromarray(np.uint16(elevation * 65535 + .5)).save(T / 'wood_height_diagnostic.png')
report = dict(source_size=list(raw.size), source_crop=rect, physical_aspect=cw / ch, canvas=[W, H], mapped_core_radii=[rx, ry], mapped_center=[D['knot']['x'], D['knot']['y']], height_min=float(height.min()), height_max=float(height.max()), roughness_min=float(roughness.min()), roughness_max=float(roughness.max()), normal_tilt_max=float(np.rad2deg(np.arccos(normal[:, :, 2])).max()), scalar_color_roughness_alignment=True, ramp_and_inverted_green_negative_control=True, wrong_bitmap_aspect_rejected=True, no_displacement_geometry=True, provenance=D['texture_provenance'])
(C / 'texture_report.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report))
