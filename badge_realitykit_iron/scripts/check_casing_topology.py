"""Casing topology check: edges shared by one triangle (open), by more than two (non-manifold), and duplicate points. Usage: Blender --background --factory-startup --python check_casing_topology.py -- A.usdz B.usdz"""
import sys, numpy as np
from pxr import Usd, UsdGeom
for path in sys.argv[sys.argv.index('--')+1:]:
    st=Usd.Stage.Open(path)
    m=UsdGeom.Mesh(st.GetPrimAtPath('/Badge/Casing___smooth_rounded_outer_edge/Casing___smooth_rounded_outer_edge_mobile_geometry'))
    idx=np.array(m.GetFaceVertexIndicesAttr().Get()).reshape(-1,3); pts=np.array(m.GetPointsAttr().Get())
    from collections import Counter
    c=Counter(tuple(sorted(e)) for t in idx for e in ((t[0],t[1]),(t[1],t[2]),(t[2],t[0])))
    boundary=[e for e,n in c.items() if n==1]; nonmanifold=[e for e,n in c.items() if n>2]
    on_floor=[e for e in boundary if abs(pts[e[0]][1]+2.895)<1e-5 and abs(pts[e[1]][1]+2.895)<1e-5]
    # duplicate positions (would indicate split vertices that could crack)
    uniq=len({tuple(p) for p in pts})
    print(path.split('/')[-3], 'edges', len(c), 'boundary', len(boundary), 'on floor', len(on_floor), 'non-manifold', len(nonmanifold), 'points', len(pts), 'unique positions', uniq)
