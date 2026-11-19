import bpy,numpy as np,math,json
from pathlib import Path
from mathutils import Matrix
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab/timber_refinement/lookdev_evidence');sc=bpy.data.scenes['Test plank master'];m=sc.objects['Master Chest Body Envelope'].data;n=len(bpy.data.scenes['Chest Complete Form Phase 1'].objects['Chest Body Envelope'].data.vertices)
a=np.empty((len(m.vertices),3),dtype=np.float32);m.vertices.foreach_get('co',a.ravel());norm=np.array([v.normal[:] for v in m.vertices],dtype=np.float32);R=np.array(Matrix.Rotation(math.radians(32),3,'Y'));q=np.c_[a[:,0],a[:,2],-a[:,1]]@R;nv=np.c_[norm[:,0],norm[:,2],-norm[:,1]]@R
assert len(q)-n==1537*417
np.savez_compressed(D/'actual_surface.npz',positions=q[n:].reshape(417,1537,3).astype('float32'),normals=nv[n:].reshape(417,1537,3).astype('float32'))
print('Read actual surface sampling and normals; no geometry or material changes')
