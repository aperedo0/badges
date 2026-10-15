"""flips.py <work> [fix] : face-vertex normals that point against their face's geometric normal (dot < 0.2), per mesh/subset;
with 'fix', replace each such normal by the area-weighted average of the face normals at that vertex position (same subset),
merging into <work>/edit.npz."""
import sys, os, json, numpy as np
from collections import defaultdict
w = sys.argv[1]; fix = len(sys.argv) > 2; d = dict(np.load(w + '/mesh.npz')); meta = json.load(open(w + '/meta.json'))
ed = dict(np.load(w + '/edit.npz')) if os.path.exists(w + '/edit.npz') else {}
for m in meta:
    i = m['i']; get = lambda k: ed.get(f'{i}:{k}', d[f'{i}:{k}'])
    P = get('points'); C = d[f'{i}:counts']; I = d[f'{i}:indices']; N = get('normals').copy(); off = np.r_[0, np.cumsum(C)[:-1]]
    fv = m['normals_interp'] == 'faceVarying'
    fn = np.zeros((len(C), 3)); fa = np.zeros(len(C))
    for f in range(len(C)):
        v = P[I[off[f]:off[f] + C[f]]]; n = np.cross(v[1] - v[0], v[2] - v[0]); a = np.linalg.norm(n); fa[f] = a; fn[f] = n / max(a, 1e-12)
    bad = []
    for f in range(len(C)):
        for s in range(off[f], off[f] + C[f]):
            n = N[s] if fv else N[I[s]]
            if fa[f] > 1e-10 and n @ fn[f] < 0.2: bad.append((f, s))
    if bad:
        print(f"{m['name']}: {len(bad)} face-vertex normals against their face (faces {len(set(b[0] for b in bad))})")
        if fix:
            acc = defaultdict(lambda: np.zeros(3))
            for f in range(len(C)):
                for s in range(off[f], off[f] + C[f]): acc[I[s]] += fn[f] * fa[f]
            for f, s in bad:
                a = acc[I[s]]; nn = a / max(np.linalg.norm(a), 1e-12)
                if nn @ fn[f] < 0.2: nn = fn[f]
                if fv: N[s] = nn
                else: N[I[s]] = nn
            ed[f'{i}:normals'] = N
if fix: np.savez(w + '/edit.npz', **ed); print('fixed')
