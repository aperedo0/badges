"""geostats.py <work> : per mesh subset: face count, mean |n.z|, n.z range, z range, screen width estimate of the subset strip."""
import sys, json, numpy as np
w = sys.argv[1]; d = np.load(w + '/mesh.npz'); meta = json.load(open(w + '/meta.json'))
for m in meta:
    i = m['i']; P = d[f'{i}:points']; C = d[f'{i}:counts']; I = d[f'{i}:indices']; off = np.r_[0, np.cumsum(C)[:-1]]
    for s in m['subsets']:
        f = d[f'{i}:subset:' + s['name']]
        n = []; zs = []
        for k in f[:4000]:
            v = P[I[off[k]:off[k] + C[k]]]; nn = np.cross(v[1] - v[0], v[2] - v[0]); l = np.linalg.norm(nn)
            if l > 0: n.append(nn / l); zs.append(v[:, 2].mean())
        n = np.array(n); print(f"{m['name']}/{s['name']} {s['material']}: faces {len(f)}, n.z mean {n[:,2].mean():.2f} [{n[:,2].min():.2f},{n[:,2].max():.2f}], |n.z|<0.3: {np.mean(np.abs(n[:,2])<0.3):.2f}, z [{min(zs):.3f},{max(zs):.3f}]")
