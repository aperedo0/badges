# Correct placement in the actual accepted file, preserving all existing mesh data.
import numpy as np,math
from mathutils import Matrix,Vector
sc=bpy.context.scene;assert sc.frame_current==0
assert 'Status: APPROVED' in (P/'correction34/PLAN.md').read_text()
layout34=json.loads((C/'layout_changes.json').read_text());changes34=layout34['translations'];rot34=Matrix.Rotation(math.radians(32),3,'Y')
# Refuse a second application to an already centered scene.
meta34=json.loads((P/'candidate33/validation.json').read_text());base34=np.load(P/'candidate33/geometry.npz')
for i34,row34 in enumerate(meta34['checks']):
 ob34=sc.objects[row34['name']];assert ob34.get('full_form'),('Not baseline33',ob34.name)
 a34=np.array([v.co[:] for v in ob34.data.vertices]);a34=np.c_[a34[:,0],a34[:,2],-a34[:,1]]
 assert a34.shape==base34[f'part{i34}_v'].shape and np.max(abs(a34-base34[f'part{i34}_v']))<1e-6,('Placement already applied or scene differs from33',ob34.name)
for name in list(changes34)+layout34['hide']:
 assert name in sc.objects and sc.objects[name].get('full_form'),name
for name,d0 in changes34.items():
 d=list(d0);d[1]*=.95;q=rot34@Vector(d);delta=Vector((q.x,-q.z,q.y));sc.objects[name].data.transform(Matrix.Translation(delta))
for name in layout34['hide']:
 ob=sc.objects[name];ob['full_form']=False;ob.hide_render=True;ob.hide_set(True)
name=layout34['new_front_small'];positive=sc.objects['Chest Rail Rivet 1 2'];negative=sc.objects.get(name)
if negative is None:
 negative=positive.copy();negative.data=positive.data.copy();negative.name=name;sc.collection.objects.link(negative)
else:negative.data=positive.data.copy()
q=rot34@Vector((-3.604,0,0));negative.data.transform(Matrix.Translation(Vector((q.x,-q.z,q.y))));negative['full_form']=True;negative.hide_render=False;negative.hide_set(False)
bpy.context.view_layer.update()
(C/'layout_stage.json').write_text(json.dumps(dict(moved=43,hidden=layout34['hide'],added=name,geometry_not_deformed=True,direct_accepted_meshes=True),indent=2))
print('Placed43 accepted meshes directly without regeneration; mirrored one current front small head, hid the obscured rear head.')
