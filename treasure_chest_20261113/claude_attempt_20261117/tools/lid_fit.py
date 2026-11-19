"""Extract the lid's outer arch points from the lid envelope and save them with the arc length."""
import bpy, numpy as np, json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lid_profile import dense_curve
out = sys.argv[sys.argv.index("--") + 1]
U = np.array([0.8480481513760686, 0.529919175863294, 0.0]); N = np.array([0.529919175863294, -0.8480481513760686, 0.0])
me = bpy.data.meshes.get("Codex backup Lab Chest Barrel Lid Envelope") or bpy.data.objects["Lab Chest Barrel Lid Envelope"].data
vv = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get("co", vv); vv = vv.reshape(-1, 3)
u, d, z = vv @ U, vv @ N, vv[:, 2]
sel = (np.abs(u - u.max()) < 1e-3)
d, z = d[sel], z[sel]
e = (d / 1.5975) ** 2 + ((z - 0.40) / 1.88) ** 2
on = (np.abs(e - 1) < 0.03) & (z > 0.42)
d, z = d[on], z[on]
order = np.argsort(-np.arctan2(z - 0.40, d) * -1)          # from the front (d > 0) over the top to the back
d, z = d[order], z[order]
keep = [0]
for i in range(1, len(d)):
    if np.hypot(d[i] - d[keep[-1]], z[i] - z[keep[-1]]) > 0.03: keep.append(i)
pts = np.stack([d[keep], z[keep]], 1)
# symmetric clean-up: mirror the front half onto the back so both sides match exactly
half = pts[pts[:, 0] > 1e-4]
pts = np.concatenate([half, [[0.0, pts[np.argmin(np.abs(pts[:, 0])), 1]]], half[::-1] * np.array([-1, 1])])
c, arc, tan = dense_curve(pts)
json.dump({"pts": pts.tolist(), "arc": float(arc[-1]), "umax": float(u.max())}, open(out, "w"), indent=0)
print("LIDFIT", len(pts), float(arc[-1]), pts[0].tolist(), pts[len(pts)//2].tolist(), pts[-1].tolist(), float(np.diff(np.hypot(*np.diff(pts,axis=0).T)).max()))
