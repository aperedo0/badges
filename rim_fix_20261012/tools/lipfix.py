"""lipfix.py <work> <config.json> : thin edge bevels (lips) take the normals and UVs of the nearest face-vertex of the surface they
border (front or rear, by the lip face's normal z sign) and join that surface's face group, so at the silhouette the lip shades and
colors exactly like the surface next to it. Walls optionally take UVs from the nearest front/rear face-vertex.
config: {"mesh": "<name>", "front": "<subset>", "rear": "<subset>", "lip": "<subset>", "wall": "<subset or null>", "wall_uv": true}
Writes <work>/edit.npz (normals, uv, subsets) for meshio import (faceVarying normals and UVs only)."""
import sys, json, numpy as np
from scipy.spatial import cKDTree
w = sys.argv[1]; cfg = json.load(open(sys.argv[2])); d = dict(np.load(w + '/mesh.npz')); meta = json.load(open(w + '/meta.json'))
m = [x for x in meta if x['name'] == cfg['mesh']][0]; i = m['i']
assert m['normals_interp'] == 'faceVarying' and m['uv_interp'] == 'faceVarying'
P = d[f'{i}:points']; C = d[f'{i}:counts']; I = d[f'{i}:indices']; N = d[f'{i}:normals'].copy(); UV = d[f'{i}:uv'].copy()
off = np.r_[0, np.cumsum(C)[:-1]]
sub = {s['name']: d[f'{i}:subset:' + s['name']] for s in m['subsets']}
def fv(faces):  # face-vertex slots of these faces
    return np.concatenate([np.arange(off[f], off[f] + C[f]) for f in faces]) if len(faces) else np.zeros(0, int)
fnorm = np.zeros((len(C), 3))
for f in range(len(C)):
    v = P[I[off[f]:off[f] + C[f]]]; n = np.cross(v[1] - v[0], v[2] - v[0]); fnorm[f] = n / max(np.linalg.norm(n), 1e-12)
lip = sub[cfg['lip']]; lip_front = lip[fnorm[lip, 2] >= 0]; lip_rear = lip[fnorm[lip, 2] < 0]
out = {}
for faces, target in ((lip_front, cfg['front']), (lip_rear, cfg['rear'])):
    src = fv(sub[target]); tree = cKDTree(P[I[src]]); dst = fv(faces)
    dist, k = tree.query(P[I[dst]]); N[dst] = N[src[k]]; UV[dst] = UV[src[k]]
    print(f'lip -> {target}: {len(faces)} faces, nearest distance max {dist.max():.4f} mean {dist.mean():.4f}')
newsub_front = np.r_[sub[cfg['front']], lip_front]
if cfg.get('wall') and cfg.get('wall_uv'):
    both = fv(newsub_front) if cfg.get('wall_uv') == 'front' else np.r_[fv(sub[cfg['front']]), fv(sub[cfg['rear']])]; tree = cKDTree(P[I[both]]); dst = fv(sub[cfg['wall']])
    dist, k = tree.query(P[I[dst]]); UV[dst] = UV[both[k]]; print(f'wall uv from nearest front/rear: max distance {dist.max():.4f}')
newsub = dict(sub)
if cfg.get('keep_rear_lip'): out[f'{i}:newsubset:RearLip'] = np.sort(lip_rear)
else: newsub[cfg['rear']] = np.sort(np.r_[sub[cfg['rear']], lip_rear])
if cfg.get('keep_front_lip'): newsub[cfg['lip']] = np.sort(lip_front)   # front lips keep their own material
else:
    newsub[cfg['front']] = np.sort(np.r_[sub[cfg['front']], lip_front]); newsub[cfg['lip']] = np.zeros(0, int)
out[f'{i}:normals'] = N; out[f'{i}:uv'] = UV
for k_, v in newsub.items(): out[f'{i}:subset:{k_}'] = v
np.savez(w + '/edit.npz', **out); print('wrote edit.npz', {k_: len(v) for k_, v in newsub.items()})
