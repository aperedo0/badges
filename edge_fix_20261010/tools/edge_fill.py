"""edge_fill.py <tris.npz> <material> <pkg_dir> <inset_texels> <map>... : for each map (e.g. 0/color.png) of <material>, every texel that no triangle
of that material covers is refilled with the nearest covered texel's color, so filtering at the outline never pulls in the white or
streaked fill that used to sit outside the badge. Covered texels are left byte identical. Writes the maps in place."""
import sys, numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, binary_dilation
d = np.load(sys.argv[1]); mat = sys.argv[2]; pkg = sys.argv[3]; inset = int(sys.argv[4])
sel = d['MAT'] == mat; UV = d['UV'][sel]
for rel in sys.argv[5:]:
    path = f'{pkg}/{rel}'; im = Image.open(path); mode = im.mode; a = np.asarray(im.convert('RGB')).copy(); H, W = a.shape[:2]
    cover = np.zeros((H, W), bool)
    for uv in UV:
        px = np.stack([uv[:, 0] * W - .5, (1 - uv[:, 1]) * H - .5], -1)
        x0, y0 = np.floor(px.min(0)).astype(int) - 1; x1, y1 = np.ceil(px.max(0)).astype(int) + 1
        xs, ys = np.meshgrid(np.arange(max(x0, 0), min(x1, W - 1) + 1), np.arange(max(y0, 0), min(y1, H - 1) + 1))
        p0, p1, p2 = px; e1 = p1 - p0; e2 = p2 - p0; den = e1[0] * e2[1] - e1[1] * e2[0]
        if abs(den) < 1e-12: continue
        u = ((xs - p0[0]) * e2[1] - (ys - p0[1]) * e2[0]) / den; v = (e1[0] * (ys - p0[1]) - e1[1] * (xs - p0[0])) / den
        inside = (u >= -0.02) & (v >= -0.02) & (u + v <= 1.02)
        cover[ys[inside], xs[inside]] = True
    # a texel is kept if any of its 2x2 bilinear footprint touches a covered texel center (conservative)
    # inset > 0: the outermost texels of the badge (the reference's thin rim highlight) are replaced from further inside
    from scipy.ndimage import binary_erosion
    keep = binary_erosion(cover, iterations=inset) if inset > 0 else binary_dilation(cover, iterations=1)
    _, (iy, ix) = distance_transform_edt(~keep, return_indices=True)
    out = a[iy, ix]
    Image.fromarray(out).convert(mode).save(path)
    print(rel, 'covered', round(float(cover.mean()), 3), 'refilled', int((~keep).sum()))
