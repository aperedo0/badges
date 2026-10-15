"""holes.py <tris.npz> : weld by position (1e-5), count edges used by 1 face (open) and by >2 faces, per mesh; print open-edge
loops' sizes and screen positions (rest pose) of short loops (pin holes)."""
import sys, numpy as np
from collections import defaultdict
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/diamond/codex_rest_20261011/approved5/tools')
from common import to_screen
d = np.load(sys.argv[1]); P = d['P']; MESH = d['MESH']
for mesh in sorted(set(MESH)):
    sel = MESH == mesh; T = P[sel]
    pts = T.reshape(-1, 3); key = np.round(pts / 1e-5).astype(np.int64)
    _, vid = np.unique(key, axis=0, return_inverse=True); vid = vid.reshape(-1, 3)
    cnt = defaultdict(int)
    for a, b, c in vid:
        for e in ((a, b), (b, c), (c, a)): cnt[tuple(sorted(e))] += 1
    open_ = [e for e, n in cnt.items() if n == 1]; many = sum(1 for n in cnt.values() if n > 2)
    print(f'{mesh}: tris {len(T)}, open edges {len(open_)}, edges with >2 faces {many}')
    if open_:
        # connected components of open edges
        adj = defaultdict(list)
        for a, b in open_: adj[a].append(b); adj[b].append(a)
        seen = set(); comps = []
        for v in adj:
            if v in seen: continue
            st = [v]; comp = []
            while st:
                x = st.pop()
                if x in seen: continue
                seen.add(x); comp.append(x); st += adj[x]
            comps.append(comp)
        upos = np.zeros((vid.max() + 1, 3)); upos[vid.reshape(-1)] = pts
        sizes = sorted(len(c) for c in comps); print('   open loops:', len(comps), 'sizes', sizes[:12], '...' if len(sizes) > 12 else '', sizes[-3:])
        for c in comps:
            if len(c) <= 12:
                s = to_screen(upos[c]).mean(0); print('   small loop', len(c), 'screen', s.round(1), 'z', upos[c][:, 2].mean().round(3))
