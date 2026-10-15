"""edgeflat.py <work> <config.json> : surface face-vertices near the outline take a normal blended toward the normal found
d0 inside the outline, so a rounded edge stops mirroring a different part of the studio than the face next to it (no dark or white
rim at rest). config: {"mesh": "...", "surfaces": ["Finish_1", "Finish_2"], "outline": ["Finish_3"], "d0": 0.06, "power": 1.0}
Outline = face-vertex positions of the outline subsets (walls). Merges into <work>/edit.npz (faceVarying normals)."""
import sys, os, json, numpy as np
from scipy.spatial import cKDTree
w = sys.argv[1]; cfg = json.load(open(sys.argv[2])); d = dict(np.load(w + '/mesh.npz')); meta = json.load(open(w + '/meta.json'))
ed = dict(np.load(w + '/edit.npz')) if os.path.exists(w + '/edit.npz') else {}
m = [x for x in meta if x['name'] == cfg['mesh']][0]; i = m['i']; assert m['normals_interp'] == 'faceVarying'
get = lambda k: ed[f'{i}:{k}'] if f'{i}:{k}' in ed else (ed[f'{i}:new{k}'] if f'{i}:new{k}' in ed else d[f'{i}:{k}'])
P = get('points'); C = d[f'{i}:counts']; I = d[f'{i}:indices']; N = get('normals').copy(); off = np.r_[0, np.cumsum(C)[:-1]]
def slots(sub):
    f = get(f'subset:{sub}'); return np.concatenate([np.arange(off[k], off[k] + C[k]) for k in f])
ol = np.concatenate([slots(s) for s in cfg['outline']]); otree = cKDTree(P[I[ol]])
d0 = cfg['d0']; pw = cfg.get('power', 1.0)
groups = cfg.get('groups') or [[x] for x in cfg['surfaces']]   # surfaces in one group share their inner normals
for grp in groups:
    s = np.concatenate([slots(x) for x in grp]); pos = P[I[s]]; dist, _ = otree.query(pos)
    inner = dist >= d0; N0 = N[s].copy()
    itree = cKDTree(pos[inner]); _, k = itree.query(pos); n_in = N0[inner][k]
    wgt = np.clip(1 - dist / d0, 0, 1) ** pw; nn = (1 - wgt[:, None]) * N0 + wgt[:, None] * n_in
    N[s] = nn / np.maximum(np.linalg.norm(nn, axis=1, keepdims=True), 1e-9)
    print(f'{grp}: {len(s)} face-vertices, within d0: {int((dist < d0).sum())}')
ed[f'{i}:normals'] = N; np.savez(w + '/edit.npz', **ed)
