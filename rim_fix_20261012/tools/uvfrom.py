"""uvfrom.py <work> <config.json> : target faces take, per face-vertex, the UV (and optionally a normal blended toward) of the
nearest face-vertex among source faces (any mesh). config: {"targets": [["mesh","subset"],...], "sources": [["mesh","subset"],...],
"normal_blend": 0.0}  normal_blend 0 keeps the target's own normals, 1 copies the source normal. Merges into <work>/edit.npz."""
import sys, os, json, numpy as np
from scipy.spatial import cKDTree
w = sys.argv[1]; cfg = json.load(open(sys.argv[2])); d = dict(np.load(w + '/mesh.npz')); meta = json.load(open(w + '/meta.json'))
ed = dict(np.load(w + '/edit.npz')) if os.path.exists(w + '/edit.npz') else {}
byname = {m['name']: m for m in meta}
def get(i, k): return ed.get(f'{i}:{k}', d[f'{i}:{k}'])
def slots(mesh, sub):
    m = byname[mesh]; i = m['i']; C = d[f'{i}:counts']; off = np.r_[0, np.cumsum(C)[:-1]]
    faces = get(i, f'subset:{sub}')
    return i, (np.concatenate([np.arange(off[f], off[f] + C[f]) for f in faces]) if len(faces) else np.zeros(0, int))
def fvpos(i, s): return get(i, 'points')[d[f'{i}:indices'][s]]
def fvuv(i, s):
    m = [x for x in meta if x['i'] == i][0]; uv = get(i, 'uv')
    return uv[s] if m['uv_interp'] == 'faceVarying' else uv[d[f'{i}:indices'][s]]
def fvn(i, s):
    m = [x for x in meta if x['i'] == i][0]; n = get(i, 'normals')
    return n[s] if m['normals_interp'] == 'faceVarying' else n[d[f'{i}:indices'][s]]
src = [slots(*x) for x in cfg['sources']]
SP = np.concatenate([fvpos(i, s) for i, s in src]); SU = np.concatenate([fvuv(i, s) for i, s in src]); SN = np.concatenate([fvn(i, s) for i, s in src])
tree = cKDTree(SP); nb = cfg.get('normal_blend', 0.0)
for mesh, sub in cfg['targets']:
    i, s = slots(mesh, sub); m = byname[mesh]
    assert m['uv_interp'] == 'faceVarying', 'vertex UV targets not supported'
    dist, k = tree.query(fvpos(i, s)); uv = get(i, 'uv').copy(); uv[s] = SU[k]; ed[f'{i}:uv'] = uv
    if nb > 0:
        assert m['normals_interp'] == 'faceVarying'
        n = get(i, 'normals').copy(); nn = (1 - nb) * n[s] + nb * SN[k]; n[s] = nn / np.maximum(np.linalg.norm(nn, axis=1, keepdims=True), 1e-9); ed[f'{i}:normals'] = n
    print(f'{mesh}/{sub}: {len(s)} face-vertices, nearest source distance max {dist.max():.4f} mean {dist.mean():.4f}')
np.savez(w + '/edit.npz', **ed)
