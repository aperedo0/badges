"""Bake local mounting contact darkening into the unchanged inset UV atlas."""
from pathlib import Path
import json
import numpy as np
from PIL import Image

r = Path(__file__).resolve().parents[1]
p = json.loads((r / 'parameters.json').read_text())
g = next(v for k, v in json.loads((r / 'work/uv_geometry.json').read_text()).items() if k.startswith('Inset___'))
points, indices, uvs = np.array(g['points']), np.array(g['indices']), np.array(g['uv'])
outline = np.array(p['outline'])[:, :2]
setting = p['contact_occlusion']
factor = np.ones((512, 512))
coverage = np.zeros((512, 512), bool)

def contact(xy):
    inside = np.zeros(len(xy), bool)
    distance = np.full(len(xy), np.inf)
    for a, b in zip(outline, np.roll(outline, -1, axis=0)):
        edge = b - a
        t = np.clip((xy - a) @ edge / (edge @ edge), 0, 1)
        distance = np.minimum(distance, np.linalg.norm(xy - a - t[:, None] * edge, axis=1))
        crosses = (a[1] > xy[:, 1]) != (b[1] > xy[:, 1])
        if abs(edge[1]) > 1e-12:
            crossing_x = a[0] + (xy[:, 1] - a[1]) * edge[0] / edge[1]
            inside ^= crosses & (xy[:, 0] < crossing_x)
    distance[inside] = 0
    strength = setting['maximum_darkening'] * np.exp(-.5 * (distance / setting['sigma_units']) ** 2)
    # Smoothly vanish before the finite support edge; no hard cutoff ring.
    fade = np.clip((setting['maximum_distance_units'] - distance) / .06, 0, 1)
    fade = fade * fade * (3 - 2 * fade)
    return 1 - strength * fade

for tri, tex in zip(indices, uvs):
    vertices = points[tri]
    normal = np.cross(vertices[1] - vertices[0], vertices[2] - vertices[0])
    length = np.linalg.norm(normal)
    if length < 1e-12 or normal[2] / length < .99 or vertices[:, 2].mean() < .03:
        continue
    q = tex * [511, -511] + [0, 511]
    low = np.maximum(np.floor(q.min(0)).astype(int), 0)
    high = np.minimum(np.ceil(q.max(0)).astype(int), 511)
    x0, y0 = low; x1, y1 = high
    if x0 > x1 or y0 > y1:
        continue
    matrix = np.vstack([q.T, np.ones(3)])
    if abs(np.linalg.det(matrix)) < 1e-10:
        continue
    gy, gx = np.mgrid[y0:y1+1, x0:x1+1]
    bary = np.linalg.solve(matrix, np.stack([gx.ravel(), gy.ravel(), np.ones(gx.size)]))
    keep = bary.min(0) >= -1e-4
    x, y = gx.ravel()[keep], gy.ravel()[keep]
    world = bary[:, keep].T @ vertices
    factor[y, x] = contact(world[:, :2])
    coverage[y, x] = True

path = r / 'source/bakes/USDZ_Inset_base_color.png'
rgb = np.asarray(Image.open(path).convert('RGB'), dtype=float) / 255
linear = np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)
linear *= factor[:, :, None]
encoded = np.rint(np.clip(np.where(linear <= .0031308, 12.92 * linear, 1.055 * linear ** (1/2.4) - .055), 0, 1) * 255).astype('uint8')
before = np.rint(rgb * 255).astype('uint8')
assert np.count_nonzero(encoded != before) > 0
assert np.all(encoded <= before)
Image.fromarray(encoded).save(path, compress_level=9)
Image.fromarray(np.rint(factor * 255).astype('uint8')).save(r / 'proof/contact_occlusion_atlas.png')
summary = {
    'method': 'baked local contact occlusion, not a directional cast shadow',
    'receiver': 'existing inset base-color map only',
    'receiver_uvs_and_geometry_unchanged': True,
    'crystal_back_z': p['crystal_back_z'],
    'inset_front_z': setting['receiver_z'],
    'mounting_overlap_units': setting['receiver_z'] - p['crystal_back_z'],
    'visible_front_geometry_unchanged': False,
    'maximum_darkening': setting['maximum_darkening'],
    'sigma_units': setting['sigma_units'],
    'maximum_distance_units': setting['maximum_distance_units'],
    'atlas_coverage_pixels': int(coverage.sum()),
    'minimum_linear_light_factor': float(factor.min()),
    'changed_rgb_values': int(np.count_nonzero(encoded != before)),
    'rgb8_before_min_max': [int(before.min()), int(before.max())],
    'rgb8_after_min_max': [int(encoded.min()), int(encoded.max())],
    'light_behavior': 'fixed mounting occlusion rotates with the badge; broad light-direction shadows are not baked',
}
(r / 'reports/contact_occlusion.json').write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
