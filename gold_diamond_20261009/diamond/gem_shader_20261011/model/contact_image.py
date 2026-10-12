"""contact_image.py <gem_planes.npz> <out.png> : front, side and top views of the gem, flat shaded with facet edges, to eyeball the facet layout."""
import sys, numpy as np
from PIL import Image, ImageDraw
d = np.load(sys.argv[1]); T = d['ALLP']; N = d['normals']; fam = d['families']
tri_n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); tri_n /= np.linalg.norm(tri_n, axis=1)[:, None]
areas = np.linalg.norm(np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]), axis=1) / 2
print('triangles', len(T), 'min area', areas.min())
S = 70
def view(name, right, up, depth):
    img = Image.new('RGB', (520, 520), (20, 22, 26)); dr = ImageDraw.Draw(img)
    # painter's order by depth (toward the viewer = larger)
    order = np.argsort((T @ depth).mean(axis=1))
    for i in order:
        facing = tri_n[i] @ depth
        if facing <= 0: continue
        shade = 0.25 + 0.75 * max(0, tri_n[i] @ np.array([-0.4, 0.6, 0.7]) / np.linalg.norm([-0.4, 0.6, 0.7]))
        col = (int(60 * shade + 20), int(130 * shade + 30), int(230 * shade + 20))
        pts = [(260 + S * p @ right, 260 - S * p @ up) for p in T[i]]
        dr.polygon(pts, fill=col, outline=(235, 240, 255))
    dr.text((8, 6), name, fill=(255, 255, 255))
    return img
front = view('front (+Z)', np.array([1, 0, 0.]), np.array([0, 1, 0.]), np.array([0, 0, 1.]))
side = view('side (+X)', np.array([0, 0, -1.]), np.array([0, 1, 0.]), np.array([1, 0, 0.]))
top = view('top', np.array([1, 0, 0.]), np.array([0, 0, -1.]), np.array([0, 1, 0.]))
# the app's camera: from (0, 1.8, 23) toward (0, -0.55, 0)
f = np.array([0, -0.55 - 1.8, -23.0]); f /= np.linalg.norm(f); r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
camera = view('as the app camera sees it', r, u, -f)
sheet = Image.new('RGB', (1040, 1040)); sheet.paste(front, (0, 0)); sheet.paste(side, (520, 0)); sheet.paste(top, (0, 520)); sheet.paste(camera, (520, 520))
sheet.save(sys.argv[2]); print(sys.argv[2])
