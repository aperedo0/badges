import bpy,numpy as np,json,math
from pathlib import Path
from mathutils import Matrix,Vector
P=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab');sc=bpy.data.scenes['Test plank master'];o=sc.objects['Master Chest Body Envelope'];R=np.array(Matrix.Rotation(math.radians(32),3,'Y'));n=len(bpy.data.scenes['Chest Complete Form Phase 1'].objects['Chest Body Envelope'].data.vertices)
a=np.empty((len(o.data.vertices),3));o.data.vertices.foreach_get('co',a.ravel());q=np.c_[a[:,0],a[:,2],-a[:,1]]@R;positive=q[n:,2]>1.6;q[n:,2]=np.minimum(q[n:,2],1.6);v=q@R.T;v=np.c_[v[:,0],-v[:,2],v[:,1]];a[n:]=v[n:];o.data.vertices.foreach_set('co',a.ravel());o.data.update()
proof=json.loads((P/'master_validation.json').read_text());proof['depth_max']=float(q[n:,2].max()-1.6);proof['positive_fiber_vertices_capped']=int(positive.sum());proof['hardware_clearance']='All new front vertices remain at or behind the source front plane; boundary untouched';(P/'master_validation.json').write_text(json.dumps(proof,indent=2))
cam=sc.camera;cam.name='Whole chest evaluation';close=cam.copy();close.data=cam.data.copy();close.name='Plank close evaluation';sc.collection.objects.link(close);rot=Matrix.Rotation(math.radians(32),3,'Y');p=rot@Vector((-1.18,-1.52,1.6));target=Vector((p.x,-p.z,p.y));forward=cam.matrix_world.to_quaternion()@Vector((0,0,-1));close.location=target-forward*12;close.rotation_euler=cam.rotation_euler;close.data.type='ORTHO';close.data.ortho_scale=2.2
sc.render.resolution_x=sc.render.resolution_y=1400;sc.render.resolution_percentage=100;sc.camera=cam
old=bpy.context.preferences.filepaths.save_version;bpy.context.preferences.filepaths.save_version=0
try:bpy.ops.wm.save_as_mainfile(filepath=str(P/'wood_master.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
print(json.dumps(dict(capped_vertices=int(positive.sum()),max_front=proof['depth_max'],cameras=[cam.name,close.name])))
