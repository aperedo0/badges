import bpy,json,numpy as np,math
from mathutils import Matrix
from pathlib import Path
P=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab');o=bpy.context.scene.objects['Chest Body Envelope'];M=np.array(Matrix.Rotation(math.radians(32),3,'Y'));a=np.array([v.co for v in o.data.vertices]);a=np.c_[a[:,0],a[:,2],-a[:,1]]@M
slot=[i for i,m in enumerate(o.data.materials) if 'Sample45' in m.name][0]
d=[dict(i=f.index,v=a[list(f.vertices)].round(5).tolist(),n=list(f.normal)) for f in o.data.polygons if f.material_index==slot]
(P/'faces.json').write_text(json.dumps(d,indent=2));print(json.dumps(d[:9]))
