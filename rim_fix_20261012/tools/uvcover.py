"""uvcover.py <tris.npz> <material substring> <W> <H> <out.npy> : texel coverage mask of that material's triangles (centers inside)."""
import sys, numpy as np
d = np.load(sys.argv[1]); sel = np.array([sys.argv[2] in m for m in d['MAT']]); UV = d['UV'][sel]; W, H = int(sys.argv[3]), int(sys.argv[4])
cov = np.zeros((H, W), bool)
for uv in UV:
    px = np.stack([uv[:, 0] * W - .5, (1 - uv[:, 1]) * H - .5], -1)
    x0, y0 = np.floor(px.min(0)).astype(int); x1, y1 = np.ceil(px.max(0)).astype(int)
    gx, gy = np.meshgrid(np.arange(max(x0, 0), min(x1, W - 1) + 1), np.arange(max(y0, 0), min(y1, H - 1) + 1))
    if gx.size == 0: continue
    e1 = px[1] - px[0]; e2 = px[2] - px[0]; den = e1[0] * e2[1] - e1[1] * e2[0]
    if abs(den) < 1e-12: continue
    u = ((gx - px[0, 0]) * e2[1] - (gy - px[0, 1]) * e2[0]) / den; v = (e1[0] * (gy - px[0, 1]) - e1[1] * (gx - px[0, 0])) / den
    ins = (u >= -1e-6) & (v >= -1e-6) & (1 - u - v >= -1e-6); cov[gy[ins], gx[ins]] = True
np.save(sys.argv[5], cov); print(int(sel.sum()), 'triangles', int(cov.sum()), 'texels covered')
