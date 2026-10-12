"""Smoothness numbers for badge renders at the master camera (1080 x 1440).

Adapted from the app team's facetstats.py / ringstats.py / analyze.py (same metrics,
same camera model), with masks built from the emblem geometry and the ring and inset
radii, so they follow the badge at any pose.

  python measure_smoothness.py --emblem emblem.json --pose 0 --out table.json NAME=render.png [NAME=render.png ...]

All values are in display luma levels (0..255, Rec.709 weights on the 8-bit AgX image):
  facet rough   cubic-fit residual RMS inside each eroded broad facet (facetstats.py)
  facet mottle  local residual RMS, sigma 6 px (blotches)
  facet grain   local residual RMS, sigma 2.5 px (fine grain)
  edge jag      RMS of the along-edge high-pass (sigma 6 samples) on the facet boundary
                lines, offsets -1, 0, +1 px: dotted, broken glint lines score high
  edge excess   how far the boundary line's 99th percentile rises above the brighter of
                its two facets' mean near the edge (glints that outshine their facet)
  ring / inset  grain (sigma 2.5) and mottle (sigma 6) on the brushed ring band (left
                arc) and two inset patches left and right of the emblem (ringstats.py)
"""
import json
import math
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_erosion, gaussian_filter, gaussian_filter1d, map_coordinates

CAM_POS = np.array([0.0, 1.8, 23.0])
CAM_TARGET = np.array([0.0, -0.55, 0.0])
FOCAL = 75 / 36 * 1080
SHAPE = (1440, 1080)


def load_gray(path):
    a = np.asarray(Image.open(path).convert('RGB'), dtype=np.float32)
    return a @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def rotation(degrees):
    a = math.radians(degrees)
    return np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])


def project(points, degrees):
    world = np.asarray(points, dtype=np.float64) @ rotation(degrees).T
    forward = CAM_TARGET - CAM_POS
    forward /= np.linalg.norm(forward)
    right = np.cross(forward, [0, 1, 0])
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    d = world - CAM_POS
    depth = d @ forward
    return np.stack([540 + FOCAL * (d @ right) / depth, 720 - FOCAL * (d @ up) / depth], axis=1), world


def raster(polys):
    img = Image.new('L', (SHAPE[1], SHAPE[0]), 0)
    draw = ImageDraw.Draw(img)
    for poly in polys:
        draw.polygon([tuple(p) for p in poly], fill=1)
    return np.asarray(img, dtype=bool)


def residual_rms(luma, mask, order=3):
    ys, xs = np.nonzero(mask)
    if len(ys) < 50:
        return float('nan')
    x, y = (xs - xs.mean()) / 50.0, (ys - ys.mean()) / 50.0
    cols = [np.ones_like(x)]
    for p in range(1, order + 1):
        for i in range(p + 1):
            cols.append(x ** (p - i) * y ** i)
    a = np.stack(cols, axis=1)
    values = luma[ys, xs]
    coef, *_ = np.linalg.lstsq(a, values, rcond=None)
    return float(np.sqrt(np.mean((values - a @ coef) ** 2)))


def local_residual_rms(luma, mask, sigma):
    m = mask.astype(np.float32)
    mean = gaussian_filter(luma * m, sigma) / np.maximum(gaussian_filter(m, sigma), 1e-6)
    inner = binary_erosion(mask, iterations=int(sigma))
    if inner.sum() < 30:
        return float('nan')
    return float(np.sqrt(np.mean((luma - mean)[inner] ** 2)))


class Emblem:
    def __init__(self, path):
        data = json.load(open(path))
        self.points = np.array(data['points'])
        self.indices = np.array(data['indices'])
        broad = sorted(i for name, faces in data['subsets'].items() if 'polished' not in name for i in faces)
        normals = {}
        for f in broad:
            a, b, c = self.points[self.indices[f]]
            n = np.cross(b - a, c - a)
            normals[f] = n / np.linalg.norm(n)
        groups = []
        for f in broad:
            for g in groups:
                if any(normals[f] @ normals[h] > math.cos(math.radians(1.0))
                       and set(self.indices[f]) & set(self.indices[h]) for h in g):
                    g.append(f)
                    break
            else:
                groups.append([f])
        self.groups, self.normals = groups, normals

    def facet_masks(self, degrees, erode=3, min_pixels=250):
        px, world = project(self.points, degrees)
        rot = rotation(degrees)
        out = {}
        for gi, g in enumerate(self.groups):
            n = rot @ self.normals[g[0]]
            centre = world[np.unique(self.indices[g].ravel())].mean(axis=0)
            to_cam = CAM_POS - centre
            if n @ to_cam <= 0.05 * np.linalg.norm(to_cam):
                continue
            full = raster([px[self.indices[f]] for f in g])
            mask = binary_erosion(full, iterations=erode)
            if mask.sum() >= min_pixels:
                ys, xs = np.nonzero(mask)
                out[gi] = dict(mask=mask, full=full, centre=(float(xs.mean()), float(ys.mean())))
        return out, px

    def boundary_edges(self, degrees, facets, min_len=30):
        """Visible facet-boundary segments: (p0, p1, facet a, facet b or None)."""
        px, _ = project(self.points, degrees)
        group_of = {f: gi for gi, g in enumerate(self.groups) for f in g}
        edge_faces = {}
        for f in group_of:
            i, j, k = self.indices[f]
            for a, b in ((i, j), (j, k), (k, i)):
                edge_faces.setdefault(tuple(sorted((a, b))), []).append(f)
        # Broad facets never share vertices after the bevel, so pair each broad edge with the
        # nearest parallel broad edge of another facet (the other side of the bevel strip).
        segs = []
        for (a, b), faces in edge_faces.items():
            if len(faces) == 2 and group_of[faces[0]] == group_of[faces[1]]:
                continue
            gi = group_of[faces[0]]
            if gi not in facets:
                continue
            p0, p1 = px[a], px[b]
            if np.linalg.norm(p1 - p0) >= min_len:
                segs.append((p0, p1, gi))
        return segs


def edge_scores(luma, segs, facets):
    jags, excess = [], []
    for p0, p1, gi in segs:
        d = p1 - p0
        length = np.linalg.norm(d)
        n = np.array([-d[1], d[0]]) / length
        centre = np.array(facets[gi]['centre'])
        if (((p0 + p1) / 2) - centre) @ n < 0:
            n = -n                                  # n points out of facet gi, across the edge
        ts = np.linspace(0.1, 0.9, max(60, int(length)))
        lines = []
        for off in (-1.0, 0.0, 1.0, 2.0, 3.0):
            pts = p0[None] + ts[:, None] * d[None] + off * n[None]
            lines.append(map_coordinates(luma, [pts[:, 1], pts[:, 0]], order=1, mode='nearest'))
        lines = np.array(lines)
        hp = lines[:4] - gaussian_filter1d(lines[:4], 6, axis=1)
        jags.append(float(np.sqrt(np.mean(hp ** 2))))
        inside = []
        for off in (-6.0, -5.0, -4.0):
            pts = p0[None] + ts[:, None] * d[None] + off * n[None]
            inside.append(map_coordinates(luma, [pts[:, 1], pts[:, 0]], order=1, mode='nearest'))
        excess.append(float(np.percentile(lines[:4], 99) - np.mean(inside)))
    return dict(edges=len(segs), jag_mean=float(np.mean(jags)), jag_max=float(np.max(jags)),
                excess_mean=float(np.mean(excess)), excess_max=float(np.max(excess)))


def ring_mask(degrees, radius=2.77, z=0.255, half_width=6):
    angles = np.radians(np.linspace(150, 210, 240))
    pts = np.stack([radius * np.cos(angles), radius * np.sin(angles), np.full_like(angles, z)], axis=1)
    px, _ = project(pts, degrees)
    img = Image.new('L', (SHAPE[1], SHAPE[0]), 0)
    ImageDraw.Draw(img).line([tuple(p) for p in px], fill=1, width=2 * half_width)
    return np.asarray(img, dtype=bool)


def inset_masks(degrees, z=0.039):
    out = {}
    for name, (x0, x1) in (('inset-left', (-1.95, -1.28)), ('inset-right', (1.28, 1.95))):
        corners = np.array([[x0, -0.95, z], [x1, -0.95, z], [x1, 0.95, z], [x0, 0.95, z]])
        px, _ = project(corners, degrees)
        out[name] = raster([px])
    return out


def measure(emblem, degrees, images):
    facets, _ = emblem.facet_masks(degrees)
    segs = emblem.boundary_edges(degrees, facets)
    order = sorted(facets, key=lambda gi: (facets[gi]['centre'][1], facets[gi]['centre'][0]))
    regions = {'ring': ring_mask(degrees), **inset_masks(degrees)}
    table = {}
    for name, path in images.items():
        luma = load_gray(path)
        row = dict(facets={})
        for gi in order:
            m = facets[gi]['mask']
            row['facets'][f'g{gi}@({facets[gi]["centre"][0]:.0f},{facets[gi]["centre"][1]:.0f})'] = dict(
                px=int(m.sum()), rough=residual_rms(luma, m), mottle=local_residual_rms(luma, m, 6.0),
                grain=local_residual_rms(luma, m, 2.5), mean=float(luma[m].mean()))
        vals = list(row['facets'].values())
        row['facet_rough_mean'] = float(np.nanmean([v['rough'] for v in vals]))
        row['facet_mottle_mean'] = float(np.nanmean([v['mottle'] for v in vals]))
        row['facet_grain_mean'] = float(np.nanmean([v['grain'] for v in vals]))
        row['edges'] = edge_scores(luma, segs, facets)
        for rname, m in regions.items():
            row[rname] = dict(grain=local_residual_rms(luma, m, 2.5), mottle=local_residual_rms(luma, m, 6.0),
                              mean=float(luma[m].mean()), px=int(m.sum()))
        table[name] = row
    return table


def print_table(degrees, table):
    names = list(table)
    keys = list(table[names[0]]['facets'])
    print(f'=== pose {degrees}: per-facet rough (cubic residual RMS, luma levels)')
    print(f'{"":<26}' + ' '.join(f'{k.split("@")[0]:>6}' for k in keys) + '   mean  mottle  grain')
    for n in names:
        r = table[n]
        print(f'{n:<26}' + ' '.join(f'{r["facets"][k]["rough"]:6.2f}' for k in keys)
              + f'  {r["facet_rough_mean"]:5.2f}  {r["facet_mottle_mean"]:5.2f}  {r["facet_grain_mean"]:5.2f}')
    print(f'{"":<26}  edge jag mean/max   edge excess mean/max   ring grain/mottle   inset-L grain   inset-R grain')
    for n in names:
        r = table[n]
        e = r['edges']
        print(f'{n:<26}  {e["jag_mean"]:5.2f} / {e["jag_max"]:5.2f}      {e["excess_mean"]:6.1f} / {e["excess_max"]:6.1f}'
              f'        {r["ring"]["grain"]:5.2f} / {r["ring"]["mottle"]:5.2f}      {r["inset-left"]["grain"]:5.2f}'
              f'           {r["inset-right"]["grain"]:5.2f}')


if __name__ == '__main__':
    args = sys.argv[1:]
    emblem = Emblem(args[args.index('--emblem') + 1])
    degrees = float(args[args.index('--pose') + 1])
    out = args[args.index('--out') + 1] if '--out' in args else None
    images = dict(a.split('=', 1) for a in args if '=' in a and not a.startswith('--'))
    table = measure(emblem, degrees, images)
    print_table(degrees, table)
    if out:
        json.dump(dict(pose=degrees, images=images, table=table), open(out, 'w'), indent=1)
