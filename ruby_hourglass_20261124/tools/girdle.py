"""Identify the outer planes and transverse end bevels of the cut in model space."""
import numpy as np
def polished_border(name,geom):
    p=np.asarray(geom['points']);tri=np.asarray(geom['triangles']);n=np.asarray(geom['normals'])
    rows=87+(2.995-p[tri,1])/(5.45/1245)
    if name.startswith('Upper'):
        bevel=(rows.max(axis=1)<=248) & (rows.min(axis=1)<=192)
    else:
        bevel=(rows.min(axis=1)>=1129) & (rows.max(axis=1)>=1230)
    return np.where((np.abs(n[:,0])>.665) | (np.abs(n[:,2])<.23) | bevel)[0].tolist()
